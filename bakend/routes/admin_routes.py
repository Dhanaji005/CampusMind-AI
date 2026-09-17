# =====================================================
# CAMPUSMIND AI - ADMIN ROUTES
# Document Uploads for RAG, Notices, Events & System Management
# =====================================================

import os
from flask import Blueprint, jsonify, request, g
from middleware.auth_middleware import jwt_required, role_required, get_optional_current_user
from services.rag_service import (
    ingest_document_pdf,
    ingest_document_text,
    list_all_documents,
    delete_document_by_id
)
from services.academic_service import (
    create_notice,
    delete_notice,
    get_all_notices,
    create_event,
    get_all_events
)
from services.user_service import get_all_users, update_user_role

admin_routes = Blueprint(
    "admin_routes",
    __name__
)


# -----------------------------------------------------
# RAG PDF / DOCUMENT UPLOAD & INDEXING
# POST /api/admin/documents/upload
# Multipart form: 'file', 'title', 'category', 'department', 'target_year'
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/documents/upload",
    methods=["POST"]
)
def upload_document():
    current_user = get_optional_current_user()

    if "file" not in request.files:
        return jsonify({"success": False, "error": "Please select a file to upload."}), 400

    file = request.files["file"]
    filename = file.filename or "uploaded_doc.pdf"
    title = request.form.get("title") or os.path.splitext(filename)[0].replace("_", " ").title()
    category = request.form.get("category", "general")
    department = request.form.get("department", "All")
    target_year = request.form.get("target_year", "All")
    uploaded_by = current_user.get("name", "Administrator")

    file_bytes = file.read()
    if not file_bytes:
        return jsonify({"success": False, "error": "Uploaded file is empty."}), 400

    # Limit file size to 25MB
    if len(file_bytes) > 25 * 1024 * 1024:
        return jsonify({"success": False, "error": "File size exceeds 25MB limit."}), 400

    try:
        if filename.lower().endswith(".pdf"):
            result = ingest_document_pdf(
                file_bytes=file_bytes,
                filename=filename,
                title=title,
                category=category,
                department=department,
                target_year=target_year,
                uploaded_by=uploaded_by
            )
            return jsonify({
                "success": True,
                "message": f"Document '{title}' successfully processed and indexed into RAG Knowledge Base! 🚀",
                "document": result
            }), 201

        elif filename.lower().endswith((".txt", ".md", ".csv")):
            text_content = file_bytes.decode("utf-8", errors="ignore")
            import sqlite3
            from config.config import Config
            conn = sqlite3.connect(os.path.join(Config.BASE_DIR, "campusmind.db"))
            result = ingest_document_text(
                conn=conn,
                title=title,
                content=text_content,
                category=category,
                department=department,
                target_year=target_year,
                uploaded_by=uploaded_by,
                file_name=filename
            )
            conn.close()
            return jsonify({
                "success": True,
                "message": f"Text document '{title}' successfully indexed into RAG! 🚀",
                "document": result
            }), 201

        else:
            return jsonify({
                "success": False,
                "error": "Unsupported file format. Please upload PDF (.pdf) or text (.txt) files."
            }), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to ingest document: {str(e)}"}), 500


# -----------------------------------------------------
# LIST ALL INDEXED RAG DOCUMENTS
# GET /api/admin/documents
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/documents",
    methods=["GET"]
)
def list_documents():
    docs = list_all_documents()
    return jsonify({
        "success": True,
        "count": len(docs),
        "documents": docs
    })


# -----------------------------------------------------
# DELETE DOCUMENT FROM RAG
# DELETE /api/admin/documents/<int:doc_id>
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/documents/<int:doc_id>",
    methods=["DELETE"]
)
def delete_document(doc_id):
    deleted = delete_document_by_id(doc_id)
    if deleted:
        return jsonify({"success": True, "message": "Document and associated embeddings deleted successfully."})
    return jsonify({"success": False, "error": "Document not found."}), 404


# -----------------------------------------------------
# CREATE NOTICE
# POST /api/admin/notices
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/notices",
    methods=["POST"]
)
def add_notice():
    current_user = get_optional_current_user()
    data = request.get_json(silent=True) or request.form or {}

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    category = data.get("category", "Academic")
    department = data.get("department", "All")
    target_year = data.get("target_year", "All")
    priority = data.get("priority", "Normal")
    published_by = current_user.get("name", "Campus Administration")

    if not title or not content:
        return jsonify({"success": False, "error": "Title and content are required."}), 400

    notice = create_notice(
        title=title,
        content=content,
        category=category,
        department=department,
        target_year=target_year,
        priority=priority,
        published_by=published_by
    )

    return jsonify({
        "success": True,
        "message": "Notice published successfully! 📢",
        "notice": notice
    }), 201


# -----------------------------------------------------
# DELETE NOTICE
# DELETE /api/admin/notices/<int:notice_id>
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/notices/<int:notice_id>",
    methods=["DELETE"]
)
def remove_notice(notice_id):
    deleted = delete_notice(notice_id)
    if deleted:
        return jsonify({"success": True, "message": "Notice deleted."})
    return jsonify({"success": False, "error": "Notice not found."}), 404


# -----------------------------------------------------
# CREATE CAMPUS EVENT
# POST /api/admin/events
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/events",
    methods=["POST"]
)
def add_event():
    data = request.get_json(silent=True) or request.form or {}

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "Workshop")
    venue = data.get("venue", "Campus Main Hall")
    event_date = data.get("event_date")
    organizer = data.get("organizer", "Student Council")
    reg_link = data.get("registration_link", "")

    if not title or not description:
        return jsonify({"success": False, "error": "Event title and description are required."}), 400

    event = create_event(
        title=title,
        description=description,
        category=category,
        venue=venue,
        event_date=event_date,
        organizer=organizer,
        registration_link=reg_link
    )

    return jsonify({
        "success": True,
        "message": "Event created successfully! 🎪",
        "event": event
    }), 201


# -----------------------------------------------------
# GET ALL USERS (Admin user manager)
# GET /api/admin/users
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/users",
    methods=["GET"]
)
def list_users():
    users = get_all_users()
    return jsonify({
        "success": True,
        "count": len(users),
        "users": users
    })


# -----------------------------------------------------
# UPDATE USER ROLE
# PUT /api/admin/users/<int:user_id>/role
# Body: { "role": "faculty" | "admin" | "student" }
# -----------------------------------------------------
@admin_routes.route(
    "/api/admin/users/<int:user_id>/role",
    methods=["PUT"]
)
def change_user_role(user_id):
    data = request.get_json(silent=True) or {}
    new_role = data.get("role", "").strip().lower()

    if not new_role:
        return jsonify({"success": False, "error": "New role is required."}), 400

    success, err = update_user_role(user_id, new_role)
    if not success:
        return jsonify({"success": False, "error": err}), 400

    return jsonify({
        "success": True,
        "message": f"User role updated to '{new_role}' successfully."
    })
