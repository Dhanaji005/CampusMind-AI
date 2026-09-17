# =====================================================
# CAMPUSMIND AI - RAG (RETRIEVAL-AUGMENTED GENERATION) SERVICE
# Grounded Knowledge Engine for Official Campus Documents
# =====================================================

import os
import json
import sqlite3
from config.config import Config
from services.embedding_service import get_embedding, cosine_similarity
from services.file_service import extract_text_from_pdf

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list:
    """
    Splits text into semantically coherent overlapping chunks.
    Prefers breaking on paragraph breaks, periods, or newlines.
    """
    if chunk_size is None:
        chunk_size = Config.RAG_CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = Config.RAG_CHUNK_OVERLAP

    text = (text or "").strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for natural sentence or paragraph break near the end
        boundary = -1
        # Try paragraph break
        p_break = text.rfind("\n\n", start + (chunk_size // 2), end)
        if p_break != -1:
            boundary = p_break + 2
        else:
            # Try sentence period or newline
            for sep in [". ", ".\n", "?\n", "!\n", "\n"]:
                pos = text.rfind(sep, start + (chunk_size // 2), end)
                if pos != -1:
                    boundary = pos + len(sep)
                    break

        if boundary == -1:
            # Fallback to space
            pos = text.rfind(" ", start + (chunk_size // 2), end)
            if pos != -1:
                boundary = pos + 1
            else:
                boundary = end

        chunk = text[start:boundary].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward with overlap
        start = max(start + 1, boundary - chunk_overlap)

    return chunks


def ingest_document_text(conn, title: str, content: str, category: str = "general",
                         department: str = "All", target_year: str = "All",
                         uploaded_by: str = "admin", file_name: str = "document.txt") -> dict:
    """
    Ingests raw text into the document catalog, chunks it, generates embeddings,
    and indexes it in database tables for RAG retrieval.
    """
    cursor = conn.cursor()

    # 1. Insert into documents table
    cursor.execute("""
        INSERT INTO documents (title, file_name, file_type, category, department, target_year, content, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, file_name, "text", category, department, target_year, content, uploaded_by))
    doc_id = cursor.lastrowid

    # 2. Chunk text
    chunks = chunk_text(content)
    inserted_chunks = 0

    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        embedding_json = json.dumps(embedding)
        meta = json.dumps({
            "title": title,
            "category": category,
            "department": department,
            "target_year": target_year,
            "chunk_index": idx,
            "total_chunks": len(chunks)
        })

        cursor.execute("""
            INSERT INTO document_chunks (document_id, chunk_index, chunk_text, embedding_json, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, idx, chunk, embedding_json, meta))
        inserted_chunks += 1

    conn.commit()

    # Also try mirroring into Supabase if configured
    try:
        from database import get_supabase
        sb = get_supabase()
        if sb:
            sb.table("documents").insert({
                "title": title,
                "file_name": file_name,
                "file_type": "text",
                "category": category,
                "department": department,
                "target_year": target_year,
                "content": content[:4000],
                "uploaded_by": uploaded_by
            }).execute()
    except Exception as e:
        print(f"[RAG] Supabase mirror notice: {e}")

    return {
        "success": True,
        "document_id": doc_id,
        "title": title,
        "chunks_indexed": inserted_chunks
    }


def ingest_document_pdf(file_bytes: bytes, filename: str, title: str = None,
                         category: str = "general", department: str = "All",
                         target_year: str = "All", uploaded_by: str = "admin") -> dict:
    """
    Extracts text from an uploaded PDF file, chunks it, generates vector embeddings,
    and indexes it in the RAG store.
    """
    if not title:
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

    # Extract text from PDF
    pdf_data = extract_text_from_pdf(file_bytes)
    extracted_text = pdf_data.get("extracted_text", "").strip()

    if not extracted_text:
        raise ValueError("Could not extract any readable text from the uploaded PDF.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (title, file_name, file_type, category, department, target_year, content, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, filename, "pdf", category, department, target_year, extracted_text, uploaded_by))
        doc_id = cursor.lastrowid

        chunks = chunk_text(extracted_text)
        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            embedding_json = json.dumps(embedding)
            meta = json.dumps({
                "title": title,
                "category": category,
                "department": department,
                "target_year": target_year,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "total_pages": pdf_data.get("total_pages", 1)
            })

            cursor.execute("""
                INSERT INTO document_chunks (document_id, chunk_index, chunk_text, embedding_json, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, idx, chunk, embedding_json, meta))

        conn.commit()
        return {
            "success": True,
            "document_id": doc_id,
            "title": title,
            "file_name": filename,
            "total_pages": pdf_data.get("total_pages", 1),
            "chunks_indexed": len(chunks)
        }
    finally:
        conn.close()


def retrieve_relevant_chunks(query: str, department: str = None, year_of_study: str = None,
                             category: str = None, top_k: int = None, min_similarity: float = None) -> list:
    """
    Retrieves top matching document chunks grounded in official campus docs
    using cosine vector similarity and metadata filtering.
    """
    if top_k is None:
        top_k = Config.RAG_TOP_K
    if min_similarity is None:
        min_similarity = Config.RAG_SIMILARITY_THRESHOLD

    query = (query or "").strip()
    if not query:
        return []

    # Generate query embedding
    query_vec = get_embedding(query)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    results = []

    try:
        cursor = conn.cursor()
        # Fetch chunks along with parent document metadata
        cursor.execute("""
            SELECT 
                dc.id AS chunk_id,
                dc.document_id,
                dc.chunk_index,
                dc.chunk_text,
                dc.embedding_json,
                dc.metadata,
                d.title AS doc_title,
                d.category AS doc_category,
                d.department AS doc_dept,
                d.target_year AS doc_year
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
        """)
        rows = cursor.fetchall()

        query_lower = query.lower()
        import re
        query_tokens = [t for t in re.findall(r'[a-zA-Z0-9\-]+', query_lower) if len(t) >= 2]
        query_words = set(query_tokens)

        # Stop words: only filter pure filler / questioning words, NEVER academic terms like syllabus, sem, units
        stop_words = {"what", "is", "the", "for", "in", "and", "according", "to", "tell", "me", "about", "ka", "ki", "ke", "hai", "kya", "batao", "karo", "do", "kise", "hota"}

        # Detect User Intent
        is_syllabus_query = any(t in query_words for t in {"syllabus", "subject", "subjects", "curriculum", "course", "courses", "sem", "semester", "semesters", "unit", "units", "credit", "credits"}) or "syllabus" in query_lower
        is_admission_query = any(t in query_words for t in {"admission", "admissions", "intake", "eligibility", "cet", "vriddhi", "fee", "fees", "seats", "seat", "prospectus"}) or "admission" in query_lower
        is_location_query = any(t in query_words for t in {"where", "location", "floor", "wing", "room", "building", "cabin", "hall", "lab", "labs", "window"})
        is_faculty_query = any(t in query_words for t in {"teaches", "teacher", "teachers", "faculty", "professor", "sir", "madam", "hod", "coordinator", "who"})

        # Detect Target Academic Year
        detected_year = None
        if any(t in query_lower for t in ["3rd year", "third year", "ty", "tybba", "tybca", "tybcom", "sem 5", "sem 6", "sem-v", "sem-vi", "semester 5", "semester 6", "5th sem", "6th sem"]):
            detected_year = "3rd Year"
        elif any(t in query_lower for t in ["2nd year", "second year", "sy", "sybba", "sybca", "sem 3", "sem 4", "sem-iii", "sem-iv", "semester 3", "semester 4", "3rd sem", "4th sem"]):
            detected_year = "2nd Year"
        elif any(t in query_lower for t in ["1st year", "first year", "fy", "fybba", "fybca", "sem 1", "sem 2", "sem-i", "sem-ii", "semester 1", "semester 2", "1st sem", "2nd sem"]):
            detected_year = "1st Year"

        # Detect Target Department
        detected_dept = None
        if any(t in query_lower for t in ["bba ca", "bbaca", "bba-ca", "bca", "computer application"]):
            detected_dept = "Computer Application"
        elif any(t in query_lower for t in ["bcom", "b.com", "commerce", "accounting", "costing"]):
            detected_dept = "Commerce"
        elif any(t in query_lower for t in ["bcs", "b.sc", "computer science"]):
            detected_dept = "Computer Science"
        elif any(t in query_lower for t in ["bba", "business administration"]):
            detected_dept = "Business Administration"

        for row in rows:
            emb_json = row["embedding_json"]
            if not emb_json:
                continue

            try:
                chunk_vec = json.loads(emb_json)
            except Exception:
                continue

            sim = cosine_similarity(query_vec, chunk_vec)

            # Keyword lexical overlap boost
            chunk_lower = row["chunk_text"].lower()
            doc_title_lower = (row["doc_title"] or "").lower()

            keyword_matches = 0
            code_matches = 0
            title_exact_matches = 0

            for w in query_words:
                if w in stop_words:
                    continue
                if w in chunk_lower:
                    keyword_matches += 1
                    if "-" in w or any(c.isdigit() for c in w):
                        code_matches += 2
                if w in doc_title_lower:
                    keyword_matches += 2
                    if "-" in w or any(c.isdigit() for c in w):
                        title_exact_matches += 2

            # Intent-based boosts
            if is_faculty_query and ("faculty" in doc_title_lower or "hod" in doc_title_lower):
                keyword_matches += 5

            if is_location_query and any(t in doc_title_lower for t in ["building", "facility", "layout", "window"]):
                keyword_matches += 5

            if is_admission_query and ("admission" in doc_title_lower or "profile" in doc_title_lower or "handbook" in doc_title_lower):
                keyword_matches += 5

            # Intent-based boost for syllabus queries
            if is_syllabus_query:
                if row["doc_category"] == "syllabus" or "syllabus" in doc_title_lower or "curriculum" in doc_title_lower:
                    keyword_matches += 6
                    if "complete" in doc_title_lower or "structure" in doc_title_lower:
                        keyword_matches += 4

            # Academic Year boost
            if detected_year:
                if row["doc_year"] == detected_year or detected_year.lower() in doc_title_lower:
                    keyword_matches += 4

            # Department boost
            if detected_dept:
                if row["doc_dept"] == detected_dept or detected_dept.lower() in doc_title_lower:
                    keyword_matches += 4

            lexical_boost = min(0.85, (keyword_matches * 0.05) + (code_matches * 0.15) + (title_exact_matches * 0.20))
            final_score = sim + lexical_boost

            # Penalize unrelated categories during specific query intents
            if is_syllabus_query and not is_location_query:
                if row["doc_category"] in ("handbook", "policy", "facility") and not any(t in doc_title_lower for t in ["syllabus", "curriculum"]):
                    final_score -= 0.60

            if detected_year and row["doc_year"] not in ("All", None, "") and row["doc_year"] != detected_year:
                final_score -= 0.35

            if detected_dept and row["doc_dept"] not in ("All", None, "") and row["doc_dept"] != detected_dept:
                final_score -= 0.35

            if final_score >= min_similarity:
                results.append({
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "title": row["doc_title"],
                    "category": row["doc_category"],
                    "department": row["doc_dept"],
                    "target_year": row["doc_year"],
                    "chunk_text": row["chunk_text"],
                    "similarity": round(final_score, 4)
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)

        if not results:
            return []

        # Collect top matching documents
        matched_doc_ids = []
        for item in results:
            if item["document_id"] not in matched_doc_ids:
                matched_doc_ids.append(item["document_id"])
            if len(matched_doc_ids) >= 3:
                break

        expanded_results = []
        seen_chunk_ids = set()

        for doc_id in matched_doc_ids:
            cursor.execute("""
                SELECT dc.id, dc.document_id, dc.chunk_index, dc.chunk_text, d.title, d.category, d.department, d.target_year
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE dc.document_id = ?
                ORDER BY dc.chunk_index ASC
            """, (doc_id,))
            doc_rows = cursor.fetchall()
            for r in doc_rows:
                if r["id"] not in seen_chunk_ids:
                    seen_chunk_ids.add(r["id"])
                    expanded_results.append({
                        "chunk_id": r["id"],
                        "document_id": r["document_id"],
                        "title": r["title"],
                        "category": r["category"],
                        "department": r["department"],
                        "target_year": r["target_year"],
                        "chunk_text": r["chunk_text"],
                        "similarity": 0.88
                    })

        # Add any other distinct results up to top_k
        for item in results:
            if item["chunk_id"] not in seen_chunk_ids and len(expanded_results) < top_k:
                seen_chunk_ids.add(item["chunk_id"])
                expanded_results.append(item)

        return expanded_results[:max(top_k, 8)]

    finally:
        conn.close()


def list_all_documents() -> list:
    """Returns all indexed campus documents with chunk statistics."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                d.id,
                d.title,
                d.file_name,
                d.file_type,
                d.category,
                d.department,
                d.target_year,
                d.uploaded_by,
                d.created_at,
                COUNT(dc.id) as total_chunks
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id = dc.document_id
            GROUP BY d.id
            ORDER BY d.id DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_document_by_id(doc_id: int) -> bool:
    """Deletes a document and its chunks from the RAG store."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM document_chunks WHERE document_id = ?", (doc_id,))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
