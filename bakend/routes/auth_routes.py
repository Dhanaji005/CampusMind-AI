# =====================================================
# CAMPUSMIND AI - AUTHENTICATION ROUTES
# JWT Issuance, Profile Sync & Role Management
# =====================================================

from flask import Blueprint, jsonify, request, g
from services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_id,
    update_user_profile
)
from middleware.auth_middleware import jwt_required, get_optional_current_user

auth_routes = Blueprint(
    "auth_routes",
    __name__
)


# -----------------------------------------------------
# STATUS ENDPOINT
# -----------------------------------------------------
@auth_routes.route(
    "/api/auth/status",
    methods=["GET"]
)
def auth_status():
    return jsonify({
        "success": True,
        "message": "Authentication & RBAC API is operational.",
        "supported_roles": ["guest", "student", "alumni", "faculty", "admin"]
    })


# -----------------------------------------------------
# SIGN UP ENDPOINT
# POST /api/auth/signup
# Body: { "name", "email", "password", "role", "department", "year_of_study", "semester" }
# -----------------------------------------------------
@auth_routes.route(
    "/api/auth/signup",
    methods=["POST"]
)
def signup():
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be JSON."
        }), 400

    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "student").strip().lower()
    department = data.get("department", "BBA(CA)").strip()
    year_of_study = data.get("year_of_study", "1st Year").strip()
    semester = data.get("semester", 1)
    student_id = data.get("student_id", "").strip()
    passcode = data.get("passcode", "").strip()
    avatar_url = data.get("avatar_url", "").strip()

    if not name:
        return jsonify({"success": False, "error": "Full Name is required."}), 400
    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    if not password:
        return jsonify({"success": False, "error": "Password is required."}), 400

    user, token, error = create_user(
        name=name,
        email=email,
        password=password,
        role=role,
        department=department,
        year_of_study=year_of_study,
        semester=semester,
        student_id=student_id,
        passcode=passcode,
        avatar_url=avatar_url
    )

    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Account created successfully! Welcome to CampusMind AI 🎉",
        "token": token,
        "user": user
    }), 201


# -----------------------------------------------------
# SIGN IN ENDPOINT
# POST /api/auth/signin
# Body: { "email": "...", "password": "..." }
# -----------------------------------------------------
@auth_routes.route(
    "/api/auth/signin",
    methods=["POST"]
)
def signin():
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be JSON."
        }), 400

    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    if not password:
        return jsonify({"success": False, "error": "Password is required."}), 400

    user, token, error = authenticate_user(email=email, password=password)

    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 401

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user.get('name', 'User')}!",
        "token": token,
        "user": user
    }), 200


# -----------------------------------------------------
# GET CURRENT USER PROFILE
# GET /api/auth/profile
# -----------------------------------------------------
@auth_routes.route(
    "/api/auth/profile",
    methods=["GET"]
)
def get_profile():
    current_user = get_optional_current_user()
    user_id = current_user.get("user_id")

    if not user_id:
        return jsonify({
            "success": True,
            "is_guest": True,
            "user": current_user
        })

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({
        "success": True,
        "is_guest": False,
        "user": {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "department": user.get("department"),
            "year_of_study": user.get("year_of_study"),
            "semester": user.get("semester"),
            "student_id": user.get("student_id"),
            "avatar_url": user.get("avatar_url"),
            "created_at": user.get("created_at")
        }
    })


# -----------------------------------------------------
# UPDATE USER PROFILE
# PUT /api/auth/profile
# -----------------------------------------------------
@auth_routes.route(
    "/api/auth/profile",
    methods=["PUT"]
)
@jwt_required
def update_profile():
    user_id = g.current_user.get("user_id")
    data = request.get_json(silent=True) or {}

    updated_user, new_token = update_user_profile(user_id, data)
    if not updated_user:
        return jsonify({"success": False, "error": "Failed to update profile."}), 400

    return jsonify({
        "success": True,
        "message": "Profile updated successfully! ✨",
        "token": new_token,
        "user": updated_user
    })