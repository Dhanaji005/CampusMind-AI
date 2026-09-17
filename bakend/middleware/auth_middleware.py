# =====================================================
# CAMPUSMIND AI - AUTHENTICATION & RBAC MIDDLEWARE
# Industry standard JWT token issuance and role-based access control
# =====================================================

import os
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, g
import jwt
from config.config import Config


def generate_token(user_payload: dict, expires_in_hours: int = None) -> str:
    """
    Generates a cryptographically signed JWT token for a user.
    """
    if expires_in_hours is None:
        expires_in_hours = Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS

    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=expires_in_hours)

    claims = {
        "user_id": user_payload.get("id"),
        "email": user_payload.get("email"),
        "name": user_payload.get("name"),
        "role": user_payload.get("role", "student"),
        "department": user_payload.get("department", "Computer Science"),
        "year_of_study": user_payload.get("year_of_study", "1st Year"),
        "semester": user_payload.get("semester", 1),
        "student_id": user_payload.get("student_id", ""),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    token = jwt.encode(claims, Config.JWT_SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Returns: dict payload if valid, None if expired/invalid.
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header() -> str:
    """
    Extracts Bearer token from the Authorization header.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def get_optional_current_user():
    """
    Extracts the current user if token is present, else returns a default Guest dictionary.
    """
    token = get_token_from_header()
    if token:
        user = decode_token(token)
        if user:
            return user

    # Check query param or header for explicit persona simulation if not authenticated
    persona = request.headers.get("X-Campus-Persona") or request.args.get("persona") or "guest"
    return {
        "user_id": None,
        "email": "guest@campusmind.ai",
        "name": "Guest Visitor",
        "role": persona if persona in ["guest", "student", "alumni", "faculty", "admin"] else "guest",
        "department": "General",
        "year_of_study": "All",
        "is_guest": True
    }


def jwt_required(f):
    """
    Decorator to enforce valid JWT authentication on protected routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({
                "success": False,
                "error": "Authentication token is missing. Please sign in."
            }), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Session has expired or token is invalid. Please sign in again."
            }), 401

        g.current_user = payload
        return f(*args, **kwargs)

    return decorated_function


def role_required(allowed_roles: list):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Usage: @role_required(['admin']) or @role_required(['admin', 'faculty'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_header()
            if not token:
                return jsonify({
                    "success": False,
                    "error": "Authentication required for this endpoint."
                }), 401

            payload = decode_token(token)
            if not payload:
                return jsonify({
                    "success": False,
                    "error": "Invalid or expired token."
                }), 401

            user_role = payload.get("role", "student")
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": f"Access denied. Requires one of roles: {', '.join(allowed_roles)}. Your role is '{user_role}'."
                }), 403

            g.current_user = payload
            return f(*args, **kwargs)

        return decorated_function

    return decorator
