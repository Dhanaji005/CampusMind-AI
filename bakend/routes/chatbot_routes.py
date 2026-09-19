# =====================================================
# CAMPUSMIND AI - CHATBOT ROUTES
# Personalized Role AI, RAG Grounding & Chat Sessions
# =====================================================

import json
import uuid
import sqlite3
from flask import Blueprint, jsonify, request, g
from config.config import Config
from middleware.auth_middleware import get_optional_current_user
from services.openrouter_service import chat, OpenRouterError
from services.file_service import extract_text_from_pdf, process_image_to_data_url, FileProcessingError
from services.rag_service import retrieve_relevant_chunks

chatbot_routes = Blueprint(
    "chatbot_routes",
    __name__
)

DB_PATH = Config.BASE_DIR + "/campusmind.db"


# -----------------------------------------------------
# STATUS ENDPOINT
# -----------------------------------------------------
@chatbot_routes.route(
    "/api/chatbot/status",
    methods=["GET"]
)
def chatbot_status():
    return jsonify({
        "success": True,
        "message": "CampusMind AI Intelligent Chatbot & RAG Engine is ready 🤖",
        "model": Config.OPENROUTER_MODEL,
        "features": [
            "role-based-personas (guest, student, alumni, faculty, hod, principal, admin)",
            "rag-official-documents-grounding",
            "year-aware-curriculum-detection",
            "pdf-and-image-vision",
            "chat-session-persistence"
        ]
    })


# -----------------------------------------------------
# DEDICATED FILE UPLOAD / PARSE ENDPOINT
# POST /api/chatbot/upload
# Multipart: 'file'
# -----------------------------------------------------
@chatbot_routes.route(
    "/api/chatbot/upload",
    methods=["POST"]
)
def chatbot_upload():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file uploaded. Please select a file."
        }), 400

    file = request.files["file"]
    filename = file.filename or "uploaded_file"
    mimetype = file.mimetype or "application/octet-stream"
    file_bytes = file.read()

    if not file_bytes:
        return jsonify({"success": False, "error": "Uploaded file is empty."}), 400

    if len(file_bytes) > 20 * 1024 * 1024:
        return jsonify({"success": False, "error": "File size exceeds 20MB limit."}), 400

    try:
        if filename.lower().endswith(".pdf") or "pdf" in mimetype:
            pdf_data = extract_text_from_pdf(file_bytes)
            return jsonify({
                "success": True,
                "file": {
                    "name": filename,
                    "type": "pdf",
                    "total_pages": pdf_data["total_pages"],
                    "processed_pages": pdf_data["processed_pages"],
                    "content": pdf_data["extracted_text"],
                    "is_truncated": pdf_data["is_truncated"],
                    "preview": f"PDF ({pdf_data['total_pages']} pages)"
                }
            })

        elif mimetype.startswith("image/") or filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            data_url = process_image_to_data_url(file_bytes, mime_type=mimetype)
            return jsonify({
                "success": True,
                "file": {
                    "name": filename,
                    "type": "image",
                    "content": data_url,
                    "preview": "Image uploaded"
                }
            })

        else:
            return jsonify({
                "success": False,
                "error": "Unsupported file type. Please upload a PDF (.pdf) or image (.png, .jpg, .webp)."
            }), 400

    except FileProcessingError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Failed to process file: {str(exc)}"}), 500


# -----------------------------------------------------
# MAIN PERSONALIZED CHAT ENDPOINT WITH RAG
# POST /api/chatbot/chat
# -----------------------------------------------------
@chatbot_routes.route(
    "/api/chatbot/chat",
    methods=["POST"]
)
def chatbot_chat():
    current_user = get_optional_current_user()

    message = ""
    history = []
    attachments = []
    system_prompt = None
    temperature = 0.7
    persona = current_user.get("role", "student") if not current_user.get("is_guest") else "guest"
    use_rag = True
    session_id = None

    # Parse JSON or Multipart
    if request.is_json:
        body = request.get_json(silent=True) or {}
        message = (body.get("message") or "").strip()
        history = body.get("history") or []
        attachments = body.get("attachments") or []
        system_prompt = body.get("system_prompt")
        persona_override = body.get("persona")
        if persona_override:
            persona = persona_override
        use_rag = body.get("use_rag", True)
        session_id = body.get("session_id")
        if isinstance(body.get("temperature"), (int, float)):
            temperature = max(0.0, min(1.0, float(body["temperature"])))

    elif request.form or request.files:
        message = (request.form.get("message") or "").strip()
        system_prompt = request.form.get("system_prompt")
        persona = request.form.get("persona") or persona
        use_rag = request.form.get("use_rag", "true").lower() in ("true", "1")
        session_id = request.form.get("session_id")

        raw_history = request.form.get("history")
        if raw_history:
            try:
                history = json.loads(raw_history)
            except Exception:
                history = []

        raw_attachments = request.form.get("attachments")
        if raw_attachments:
            try:
                attachments = json.loads(raw_attachments)
            except Exception:
                attachments = []

        for key in request.files:
            file = request.files[key]
            filename = file.filename or "uploaded_file"
            mimetype = file.mimetype or ""
            f_bytes = file.read()

            if f_bytes:
                if filename.lower().endswith(".pdf") or "pdf" in mimetype:
                    try:
                        pdf_info = extract_text_from_pdf(f_bytes)
                        attachments.append({
                            "type": "pdf",
                            "name": filename,
                            "content": pdf_info["extracted_text"]
                        })
                    except Exception as e:
                        print(f"Error parsing PDF: {e}")
                elif mimetype.startswith("image/"):
                    try:
                        data_url = process_image_to_data_url(f_bytes, mimetype)
                        attachments.append({
                            "type": "image",
                            "name": filename,
                            "content": data_url
                        })
                    except Exception as e:
                        print(f"Error processing image: {e}")

    else:
        return jsonify({"success": False, "error": "Request must be JSON or multipart."}), 400

    if not message and not attachments:
        return jsonify({"success": False, "error": "Please provide a question or attach a file."}), 400

    # Auto-load student academic data if role is student
    if persona == "student":
        try:
            from services.academic_service import get_subjects_by_year, get_exams_by_year, get_student_attendance
            s_year = current_user.get("year_of_study", "1st Year")
            s_dept = current_user.get("department", "Computer Science")
            current_user["enrolled_subjects"] = get_subjects_by_year(s_year, s_dept)
            current_user["scheduled_exams"] = get_exams_by_year(s_year, s_dept)
            current_user["attendance"] = get_student_attendance(
                student_id=current_user.get("student_id"),
                email=current_user.get("email"),
                name=current_user.get("name"),
                department=s_dept
            )
        except Exception as e:
            print(f"[Chatbot] Academic context lookup notice: {e}")

    # -----------------------------------------------------
    # RAG Knowledge Base Retrieval
    # -----------------------------------------------------
    rag_chunks = []
    if use_rag and message:
        try:
            rag_chunks = retrieve_relevant_chunks(
                query=message,
                department=current_user.get("department"),
                year_of_study=current_user.get("year_of_study"),
                top_k=Config.RAG_TOP_K,
                min_similarity=Config.RAG_SIMILARITY_THRESHOLD
            )
        except Exception as e:
            print(f"[Chatbot] RAG retrieval notice: {e}")
            rag_chunks = []

    # -----------------------------------------------------
    # Call OpenRouter Service
    # -----------------------------------------------------
    try:
        result = chat(
            message=message,
            persona=persona,
            user_profile=current_user,
            system_prompt=system_prompt,
            history=history,
            attachments=attachments,
            rag_chunks=rag_chunks,
            temperature=temperature
        )
    except OpenRouterError as exc:
        return jsonify({"success": False, "error": str(exc)}), 502
    except Exception as exc:
        return jsonify({"success": False, "error": f"Chatbot engine error: {str(exc)}"}), 500

    # -----------------------------------------------------
    # Persist in Chat History (if session_id provided or user logged in)
    # -----------------------------------------------------
    saved_session_id = session_id or str(uuid.uuid4())[:12]
    user_id = current_user.get("user_id")

    try:
        with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
            cursor = conn.cursor()
            # Ensure session exists
            cursor.execute("SELECT id FROM chat_sessions WHERE id = ?", (saved_session_id,))
            if not cursor.fetchone():
                session_title = (message[:40] + "...") if message else "Document Analysis"
                cursor.execute("""
                    INSERT INTO chat_sessions (id, user_id, title, persona)
                    VALUES (?, ?, ?, ?)
                """, (saved_session_id, user_id, session_title, persona))

            # Insert user message
            cursor.execute("""
                INSERT INTO chat_messages (session_id, user_id, role, content)
                VALUES (?, ?, ?, ?)
            """, (saved_session_id, user_id, "user", message or "[Attached Files]"))

            # Insert assistant response
            cursor.execute("""
                INSERT INTO chat_messages (session_id, user_id, role, content, sources_used)
                VALUES (?, ?, ?, ?, ?)
            """, (saved_session_id, user_id, "assistant", result["reply"], json.dumps(result.get("sources", []))))
            conn.commit()
    except Exception as e:
        print(f"[Chatbot] Session save notice: {e}")

    return jsonify({
        "success": True,
        "reply": result["reply"],
        "model": result["model"],
        "persona": persona,
        "session_id": saved_session_id,
        "sources": result.get("sources", []),
        "rag_applied": len(rag_chunks) > 0,
        "usage": result.get("usage", {})
    })


# -----------------------------------------------------
# GET USER CHAT SESSIONS
# GET /api/chatbot/sessions
# -----------------------------------------------------
@chatbot_routes.route(
    "/api/chatbot/sessions",
    methods=["GET"]
)
def get_sessions():
    current_user = get_optional_current_user()
    user_id = current_user.get("user_id")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if user_id:
            cursor.execute("""
                SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 20
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM chat_sessions ORDER BY updated_at DESC LIMIT 10
            """)
        sessions = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "sessions": sessions
    })


# -----------------------------------------------------
# GET MESSAGES FOR A SESSION
# GET /api/chatbot/sessions/<id>/messages
# -----------------------------------------------------
@chatbot_routes.route(
    "/api/chatbot/sessions/<string:sid>/messages",
    methods=["GET"]
)
def get_session_messages(sid):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, content, sources_used, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (sid,))
        rows = cursor.fetchall()
        messages = []
        for r in rows:
            m = dict(r)
            try:
                m["sources_used"] = json.loads(m.get("sources_used") or "[]")
            except Exception:
                m["sources_used"] = []
            messages.append(m)

    return jsonify({
        "success": True,
        "session_id": sid,
        "messages": messages
    })
