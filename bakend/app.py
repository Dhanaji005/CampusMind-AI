# =====================================================
# CAMPUSMIND AI - SMART CAMPUS PLATFORM
# FLASK BACKEND WITH JWT RBAC & RAG PIPELINE
# =====================================================

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from config.config import Config
from database import init_db, get_supabase, get_db_connection

# Blueprints
from routes.auth_routes import auth_routes
from routes.chatbot_routes import chatbot_routes
from routes.student_routes import student_routes
from routes.admin_routes import admin_routes
from routes.attendance_routes import attendance_routes
from routes.hod_routes import hod_routes
from routes.principal_routes import principal_routes


# =====================================================
# CREATE AND CONFIGURE FLASK APP
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS with authorization header support
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With,Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

@app.route("/api/<path:path>", methods=["OPTIONS"])
def handle_options(path):
    response = jsonify({"status": "ok"})
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With,Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

# Initialize database tables and foundational data
try:
    init_db()
except Exception as e:
    print(f"[App] Database initialization note: {e}")


# =====================================================
# REGISTER BLUEPRINTS
# =====================================================

app.register_blueprint(auth_routes)
app.register_blueprint(chatbot_routes)
app.register_blueprint(student_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(attendance_routes)
app.register_blueprint(hod_routes)
app.register_blueprint(principal_routes)


# =====================================================
# CORE API STATUS & HEALTH ROUTES
# =====================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "message": "CampusMind AI Smart Campus Platform API is running 🚀",
        "version": "2.0.0",
        "database": "SQLite (WAL Mode)",
        "model": Config.OPENROUTER_MODEL,
        "rag_pipeline": "Active (grounded VPCSC records & RAG engine)",
        "features": {
            "jwt_rbac": True,
            "roles": ["guest", "student", "alumni", "faculty", "admin"],
            "year_detection": True,
            "admin_document_uploads": True
        }
    })


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@app.route("/", methods=["GET"])
def index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({
        "success": True,
        "message": "CampusMind AI Smart Campus Platform API is running 🚀"
    })


@app.route("/<path:path>", methods=["GET"])
def serve_frontend_static(path):
    # Do not intercept API endpoints
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404

    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    if os.path.exists(file_path + ".html"):
        return send_from_directory(FRONTEND_DIR, path + ".html")

    return jsonify({"error": f"Resource '{path}' not found"}), 404


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
