# =====================================================
# CAMPUSMIND AI - USER SERVICE
# Supabase + SQLite Resilient Auth with Role & Year Profile Support
# =====================================================

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from config.config import Config
from middleware.auth_middleware import generate_token

load_dotenv()

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")


def get_supabase_client():
    from database import get_supabase
    return get_supabase()


def get_user_by_email(email: str):
    """Finds a user by email from Supabase (if available) or local SQLite."""
    email = (email or "").strip().lower()
    if not email:
        return None

    # Try Supabase first
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("users").select("*").eq("email", email).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    # SQLite fallback
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
            row = cursor.fetchone()
            if row:
                return dict(row)
    except Exception as e:
        print(f"[UserService] SQLite find user error: {e}")

    return None


def get_user_by_id(user_id: int):
    """Finds a user by ID."""
    if not user_id:
        return None

    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("users").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
    except Exception as e:
        print(f"[UserService] SQLite find user by id error: {e}")

    return None


def create_user(name: str, email: str, password: str, role: str = "student",
                department: str = "BBA(CA)", year_of_study: str = "1st Year",
                semester: int = 1, student_id: str = None, passcode: str = None, avatar_url: str = None):
    """
    Creates a new user account with role-based and academic profile attributes.
    Enforces security authorization keys for privileged roles (admin, faculty).
    Returns: tuple (user_dict_or_None, token_or_None, error_message_or_None)
    """
    name = (name or "").strip()
    email = (email or "").strip().lower()
    role = (role or "student").strip().lower()
    department = (department or "BBA(CA)").strip()
    year_of_study = (year_of_study or "1st Year").strip()
    passcode = (passcode or "").strip()

    valid_roles = ["guest", "student", "alumni", "faculty", "admin"]
    if role not in valid_roles:
        role = "student"

    # --- SECURITY ROLE VERIFICATION ---
    if role == "admin":
        valid_admin_keys = ["VPCSC@ADMIN2026", "VPCSC-ADMIN-2026", "Admin@123"]
        if not passcode or passcode not in valid_admin_keys:
            return None, None, "Invalid Administrator Security Passcode. Unauthorized access denied."

    if role == "faculty":
        valid_faculty_keys = ["VPCSC@FAC2026", "VPCSC-FACULTY-2026", "Faculty@123"]
        if not passcode or passcode not in valid_faculty_keys:
            return None, None, "Invalid Faculty Verification Code. Please enter official VPCSC faculty security key or register as Student."

    if not name or len(name) < 2:
        return None, None, "Name must be at least 2 characters long."
    if not email or "@" not in email:
        return None, None, "A valid email address is required."
    if not password or len(password) < 8:
        return None, None, "Password must be at least 8 characters long."

    existing = get_user_by_email(email)
    if existing:
        return None, None, "An account with this email already exists. Please sign in."

    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()

    # Generate VPCSC Student PRN/ID if student and not provided
    if role == "student" and not student_id:
        student_id = f"VPCSC-{datetime.now().year}-{str(abs(hash(email)) % 900 + 100)}"
    elif role == "faculty" and not student_id:
        student_id = f"FAC-VPCSC-{str(abs(hash(email)) % 900 + 100)}"
    elif role == "admin" and not student_id:
        student_id = f"ADM-VPCSC-{str(abs(hash(email)) % 90 + 10)}"

    user_record = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "department": department,
        "year_of_study": year_of_study,
        "semester": semester or 1,
        "student_id": student_id or "",
        "avatar_url": avatar_url or "",
        "created_at": created_at
    }

    # 1. Try Supabase insert
    supabase = get_supabase_client()
    created_user_id = None
    if supabase:
        try:
            res = supabase.table("users").insert(user_record).execute()
            if res.data and len(res.data) > 0:
                created_user_id = res.data[0].get("id")
        except Exception as e:
            print(f"[UserService] Supabase insert note: {e}")

    # 2. SQLite insert
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, department, year_of_study, semester, student_id, avatar_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, password_hash, role, department, year_of_study, semester or 1, student_id or "", avatar_url or ""))
            if not created_user_id:
                created_user_id = cursor.lastrowid
            conn.commit()

            user_data = {
                "id": created_user_id,
                "name": name,
                "email": email,
                "role": role,
                "department": department,
                "year_of_study": year_of_study,
                "semester": semester or 1,
                "student_id": student_id or "",
                "avatar_url": avatar_url or "",
                "created_at": created_at
            }

            token = generate_token(user_data)
            return user_data, token, None

    except sqlite3.IntegrityError:
        return None, None, "An account with this email already exists."
    except Exception as e:
        return None, None, f"Database error: {str(e)}"


def authenticate_user(email: str, password: str):
    """
    Authenticates a user and generates a signed JWT token with role & year claims.
    Returns: tuple (user_dict_or_None, token_or_None, error_message_or_None)
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return None, None, "Email and password are required."

    user = get_user_by_email(email)
    if not user:
        return None, None, "No account found with this email. Please create an account."

    stored_hash = user.get("password_hash")
    if not stored_hash or not check_password_hash(stored_hash, password):
        return None, None, "Incorrect password. Please try again."

    user_data = {
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role", "student"),
        "department": user.get("department", "BBA(CA)"),
        "year_of_study": user.get("year_of_study", "1st Year"),
        "semester": user.get("semester", 1),
        "student_id": user.get("student_id", ""),
        "avatar_url": user.get("avatar_url", ""),
        "created_at": user.get("created_at")
    }

    token = generate_token(user_data)
    return user_data, token, None


def update_user_profile(user_id: int, updates: dict):
    """Updates user profile details such as year of study, department, name, avatar."""
    allowed_fields = ["name", "department", "year_of_study", "semester", "student_id", "avatar_url"]
    clean_updates = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}

    if not clean_updates:
        return get_user_by_id(user_id), None

    # Update SQLite
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            set_clauses = [f"{k} = ?" for k in clean_updates.keys()]
            values = list(clean_updates.values()) + [user_id]
            cursor.execute(f"UPDATE users SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
    except Exception as e:
        return None, str(e)

    # Mirror to Supabase
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("users").update(clean_updates).eq("id", user_id).execute()
        except Exception:
            pass

    updated = get_user_by_id(user_id)
    new_token = generate_token(updated)
    return updated, new_token


def get_all_users():
    """Returns all registered users (for Admin management)."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, department, year_of_study, semester, student_id, created_at FROM users ORDER BY id DESC")
        return [dict(r) for r in cursor.fetchall()]


def update_user_role(user_id: int, new_role: str):
    """Updates a user's role (e.g. promote to admin or faculty)."""
    valid_roles = ["guest", "student", "alumni", "faculty", "admin"]
    if new_role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()
        return True, None
