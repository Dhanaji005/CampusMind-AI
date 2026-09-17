# =====================================================
# CAMPUSMIND AI - HOD (HEAD OF DEPARTMENT) ROUTES
# Scoped Department Cockpit: Attendance, Timetable, Exams & Notices
# =====================================================

import os
import sqlite3
from flask import Blueprint, jsonify, request
from config.config import Config
from middleware.auth_middleware import get_optional_current_user

hod_routes = Blueprint(
    "hod_routes",
    __name__
)

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")


def _resolve_department(user: dict) -> str:
    """Helper to detect department from query params or logged-in HOD session."""
    query_dept = request.args.get("department")
    if query_dept and query_dept != "All":
        return query_dept
    if user and user.get("department") and user.get("department") != "All":
        return user.get("department")
    return "BBA(CA)"


# -----------------------------------------------------
# GET HOD DEPARTMENT OVERVIEW STATS
# GET /api/hod/overview?department=BBA(CA)
# -----------------------------------------------------
@hod_routes.route(
    "/api/hod/overview",
    methods=["GET"]
)
def get_hod_overview():
    current_user = get_optional_current_user()
    dept = _resolve_department(current_user)

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Total Registered Students in Department
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role = 'student' AND (department LIKE ? OR department = ?)
        """, (f"%{dept}%", dept))
        student_count = cursor.fetchone()[0]

        # 2. Attendance Stats & Defaulters Count
        cursor.execute("""
            SELECT student_id, email, student_name, total_lectures, attended_lectures, percentage, status
            FROM attendance
            WHERE department LIKE ? OR department = ?
        """, (f"%{dept}%", dept))
        att_rows = [dict(r) for r in cursor.fetchall()]

        total_lec = sum(r.get("total_lectures", 0) for r in att_rows)
        att_lec = sum(r.get("attended_lectures", 0) for r in att_rows)
        avg_pct = round((att_lec / total_lec * 100), 1) if total_lec > 0 else 0.0

        defaulters_count = len([r for r in att_rows if r.get("percentage", 0) < 75.0])
        good_count = len([r for r in att_rows if r.get("percentage", 0) >= 75.0])

        # 3. Timetable Slots Count
        cursor.execute("""
            SELECT COUNT(*) FROM timetables
            WHERE department LIKE ? OR department = ?
        """, (f"%{dept}%", dept))
        timetable_slots_count = cursor.fetchone()[0]

        # 4. Upcoming Exams Count
        cursor.execute("""
            SELECT COUNT(*) FROM exams
            WHERE department LIKE ? OR department = ? OR department = 'All'
        """, (f"%{dept}%", dept))
        exams_count = cursor.fetchone()[0]

        # 5. Department Notices Count
        cursor.execute("""
            SELECT COUNT(*) FROM notices
            WHERE department LIKE ? OR department = ? OR department = 'All'
        """, (f"%{dept}%", dept))
        notices_count = cursor.fetchone()[0]

    return jsonify({
        "success": True,
        "department": dept,
        "metrics": {
            "total_students": student_count,
            "average_attendance": avg_pct,
            "defaulters_count": defaulters_count,
            "good_attendance_count": good_count,
            "total_attendance_records": len(att_rows),
            "timetable_slots_count": timetable_slots_count,
            "upcoming_exams_count": exams_count,
            "active_notices_count": notices_count
        }
    })


# -----------------------------------------------------
# GET DEPARTMENT STUDENTS ROSTER
# GET /api/hod/students?department=BBA(CA)&year=1st+Year
# -----------------------------------------------------
@hod_routes.route(
    "/api/hod/students",
    methods=["GET"]
)
def get_hod_students():
    current_user = get_optional_current_user()
    dept = _resolve_department(current_user)
    year = request.args.get("year", "All")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT id, name, email, department, year_of_study, semester, student_id, avatar_url, created_at
            FROM users
            WHERE role = 'student' AND (department LIKE ? OR department = ?)
        """
        params = [f"%{dept}%", dept]

        if year and year != "All":
            query += " AND year_of_study = ?"
            params.append(year)

        query += " ORDER BY year_of_study ASC, name ASC"
        cursor.execute(query, params)
        students = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "department": dept,
        "year": year,
        "total": len(students),
        "students": students
    })


# -----------------------------------------------------
# TIMETABLE CRUD FOR HOD
# GET /api/hod/timetable?department=BBA(CA)&year=3rd+Year
# POST /api/hod/timetable
# DELETE /api/hod/timetable/<id>
# -----------------------------------------------------
@hod_routes.route(
    "/api/hod/timetable",
    methods=["GET"]
)
def get_hod_timetable():
    current_user = get_optional_current_user()
    dept = _resolve_department(current_user)
    year = request.args.get("year", "All")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM timetables WHERE (department LIKE ? OR department = ?)"
        params = [f"%{dept}%", dept]

        if year and year != "All":
            query += " AND year_of_study = ?"
            params.append(year)

        # Order logically by day of week then time slot
        query += """
            ORDER BY 
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    ELSE 7
                END,
                time_slot ASC
        """
        cursor.execute(query, params)
        slots = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "department": dept,
        "year": year,
        "timetable": slots
    })


@hod_routes.route(
    "/api/hod/timetable",
    methods=["POST"]
)
def add_hod_timetable_slot():
    data = request.get_json(silent=True) or request.form or {}
    dept = data.get("department") or "BBA(CA)"
    year = data.get("year_of_study") or "1st Year"
    sem = int(data.get("semester") or 1)
    day = data.get("day_of_week") or "Monday"
    slot = data.get("time_slot") or "10:00 AM - 11:00 AM"
    sub_code = (data.get("subject_code") or "").strip()
    sub_name = (data.get("subject_name") or "").strip()
    faculty = (data.get("faculty_name") or "").strip()
    room = (data.get("room_no") or "Classroom 101").strip()

    if not sub_name:
        return jsonify({"success": False, "error": "Subject name is required."}), 400

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO timetables (department, year_of_study, semester, day_of_week, time_slot, subject_code, subject_name, faculty_name, room_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dept, year, sem, day, slot, sub_code, sub_name, faculty, room))
        new_id = cursor.lastrowid
        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Lecture slot added successfully for {day} ({slot})!",
        "slot_id": new_id
    }), 201


@hod_routes.route(
    "/api/hod/timetable/<int:slot_id>",
    methods=["DELETE"]
)
def delete_hod_timetable_slot(slot_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timetables WHERE id = ?", (slot_id,))
        conn.commit()
        deleted = cursor.rowcount > 0

    if not deleted:
        return jsonify({"success": False, "error": "Slot not found."}), 404

    return jsonify({"success": True, "message": "Lecture slot deleted successfully."})


# -----------------------------------------------------
# EXAMS MANAGEMENT FOR HOD
# GET /api/hod/exams?department=BBA(CA)
# POST /api/hod/exam
# DELETE /api/hod/exam/<id>
# -----------------------------------------------------
@hod_routes.route(
    "/api/hod/exams",
    methods=["GET"]
)
def get_hod_exams():
    current_user = get_optional_current_user()
    dept = _resolve_department(current_user)
    year = request.args.get("year", "All")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM exams WHERE (department LIKE ? OR department = ? OR department = 'All')"
        params = [f"%{dept}%", dept]

        if year and year != "All":
            query += " AND (year_of_study = ? OR year_of_study = 'All')"
            params.append(year)

        query += " ORDER BY exam_date ASC"
        cursor.execute(query, params)
        exams = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "department": dept,
        "exams": exams
    })


@hod_routes.route(
    "/api/hod/exam",
    methods=["POST"]
)
def create_hod_exam():
    data = request.get_json(silent=True) or request.form or {}
    sub_name = (data.get("subject_name") or "").strip()
    sub_code = (data.get("subject_code") or "").strip()
    dept = data.get("department") or "BBA(CA)"
    year = data.get("year_of_study") or "1st Year"
    sem = int(data.get("semester") or 1)
    exam_type = data.get("exam_type") or "Mid-Term"
    exam_date = data.get("exam_date") or ""
    start_time = data.get("start_time") or "10:00 AM"
    end_time = data.get("end_time") or "01:00 PM"
    room = data.get("room_no") or "Hall A-101"
    topics = data.get("syllabus_topics") or ""

    if not sub_name or not exam_date:
        return jsonify({"success": False, "error": "Subject name and exam date are required."}), 400

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO exams (subject_name, subject_code, department, year_of_study, semester, exam_type, exam_date, start_time, end_time, room_no, syllabus_topics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sub_name, sub_code, dept, year, sem, exam_type, exam_date, start_time, end_time, room, topics))
        new_id = cursor.lastrowid
        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Exam scheduled successfully for {sub_name} on {exam_date}!",
        "exam_id": new_id
    }), 201


@hod_routes.route(
    "/api/hod/exam/<int:exam_id>",
    methods=["DELETE"]
)
def delete_hod_exam(exam_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        conn.commit()
        deleted = cursor.rowcount > 0

    if not deleted:
        return jsonify({"success": False, "error": "Exam not found."}), 404

    return jsonify({"success": True, "message": "Exam entry removed successfully."})


# -----------------------------------------------------
# DEPARTMENT NOTICES & CIRCULARS FOR HOD
# POST /api/hod/notice
# -----------------------------------------------------
@hod_routes.route(
    "/api/hod/notice",
    methods=["POST"]
)
def create_hod_notice():
    data = request.get_json(silent=True) or request.form or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    category = data.get("category") or "Academic"
    dept = data.get("department") or "BBA(CA)"
    target_year = data.get("target_year") or "All"
    priority = data.get("priority") or "Normal"
    published_by = data.get("published_by") or "Department HOD"

    if not title or not content:
        return jsonify({"success": False, "error": "Title and content are required."}), 400

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notices (title, content, category, department, target_year, priority, published_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, content, category, dept, target_year, priority, published_by))
        new_id = cursor.lastrowid
        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Notice published successfully for {dept}!",
        "notice_id": new_id
    }), 201
