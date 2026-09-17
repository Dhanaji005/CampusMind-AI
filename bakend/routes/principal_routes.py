# =====================================================
# CAMPUSMIND AI - PRINCIPAL MASTER COCKPIT ROUTES
# Institutional Governance Across All Departments (VPCSC Indapur)
# =====================================================

import os
import sqlite3
from datetime import datetime
from flask import Blueprint, jsonify, request
from config.config import Config
from middleware.auth_middleware import get_optional_current_user

principal_routes = Blueprint(
    "principal_routes",
    __name__
)

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")

DEPARTMENTS_LIST = [
    {"name": "BBA(CA)", "code": "BBA-CA", "hod": "Prof. Nilesh Kaldate", "title": "BBA (Computer Application)"},
    {"name": "BCS", "code": "B.Sc-CS", "hod": "Prof. Shaikh Sarfaraz Yusuf", "title": "B.Sc. (Computer Science)"},
    {"name": "B.Com", "code": "B.Com", "hod": "Prof. Bhosale S. D.", "title": "Bachelor of Commerce"},
    {"name": "BBA", "code": "BBA", "hod": "Prof. Bhong S. N.", "title": "Bachelor of Business Administration"},
    {"name": "B.Sc", "code": "B.Sc", "hod": "Prof. Shaikh M. D.", "title": "Bachelor of Science"},
    {"name": "M.Sc", "code": "M.Sc-CS", "hod": "Prof. Shaikh Sarfaraz Yusuf", "title": "M.Sc. (Computer Science)"}
]


# -----------------------------------------------------
# GET INSTITUTIONAL OVERVIEW METRICS
# GET /api/principal/overview
# -----------------------------------------------------
@principal_routes.route(
    "/api/principal/overview",
    methods=["GET"]
)
def get_principal_overview():
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Total Students Across All Departments
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        total_students = cursor.fetchone()[0]

        # 2. Total Faculty
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'faculty' OR role = 'hod'")
        total_faculty = cursor.fetchone()[0]

        # 3. Overall College Attendance
        cursor.execute("SELECT total_lectures, attended_lectures, percentage FROM attendance")
        all_att = [dict(r) for r in cursor.fetchall()]
        tot_lec = sum(r.get("total_lectures", 0) for r in all_att)
        att_lec = sum(r.get("attended_lectures", 0) for r in all_att)
        overall_college_att = round((att_lec / tot_lec * 100), 1) if tot_lec > 0 else 0.0

        total_defaulters = len([r for r in all_att if r.get("percentage", 0) < 75.0])
        sppu_compliance_pct = round(((len(all_att) - total_defaulters) / len(all_att) * 100), 1) if len(all_att) > 0 else 100.0

        # 4. Total Circulars & Notices
        cursor.execute("SELECT COUNT(*) FROM circulars")
        total_circulars = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM notices")
        total_notices = cursor.fetchone()[0]

        # 5. Department Breakdown
        dept_stats = []
        for d in DEPARTMENTS_LIST:
            dept_name = d["name"]
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE role = 'student' AND (department LIKE ? OR department = ?)
            """, (f"%{dept_name}%", dept_name))
            s_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT total_lectures, attended_lectures, percentage FROM attendance
                WHERE department LIKE ? OR department = ?
            """, (f"%{dept_name}%", dept_name))
            dept_att = [dict(r) for r in cursor.fetchall()]

            d_tot = sum(r.get("total_lectures", 0) for r in dept_att)
            d_att = sum(r.get("attended_lectures", 0) for r in dept_att)
            d_pct = round((d_att / d_tot * 100), 1) if d_tot > 0 else 0.0
            d_defaulters = len([r for r in dept_att if r.get("percentage", 0) < 75.0])

            dept_stats.append({
                "department": dept_name,
                "title": d["title"],
                "code": d["code"],
                "hod": d["hod"],
                "students_count": s_count,
                "attendance_percentage": d_pct,
                "defaulters_count": d_defaulters,
                "records_count": len(dept_att)
            })

    return jsonify({
        "success": True,
        "college": {
            "name": "Vidya Pratishthan's Commerce & Science College, Indapur",
            "principal": "Dr. Lalasaheb Kashid",
            "affiliation": "Savitribai Phule Pune University (SPPU Code: 856)"
        },
        "kpi": {
            "total_students": total_students,
            "total_faculty": total_faculty,
            "overall_attendance": overall_college_att,
            "sppu_compliance_rate": sppu_compliance_pct,
            "total_defaulters": total_defaulters,
            "total_circulars": total_circulars,
            "total_notices": total_notices,
            "departments_count": len(DEPARTMENTS_LIST)
        },
        "departments": dept_stats
    })


# -----------------------------------------------------
# DEEP DIVE INSPECTION FOR ANY DEPARTMENT (PRINCIPAL EYE)
# GET /api/principal/department-data?department=BBA(CA)
# -----------------------------------------------------
@principal_routes.route(
    "/api/principal/department-data",
    methods=["GET"]
)
def get_principal_department_data():
    dept = request.args.get("department", "BBA(CA)")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Students in this department
        cursor.execute("""
            SELECT id, name, email, department, year_of_study, semester, student_id, created_at
            FROM users
            WHERE role = 'student' AND (department LIKE ? OR department = ?)
            ORDER BY year_of_study ASC, name ASC
        """, (f"%{dept}%", dept))
        students = [dict(r) for r in cursor.fetchall()]

        # 2. Attendance Records & Defaulters
        cursor.execute("""
            SELECT * FROM attendance
            WHERE department LIKE ? OR department = ?
            ORDER BY percentage ASC, student_name ASC
        """, (f"%{dept}%", dept))
        att_records = [dict(r) for r in cursor.fetchall()]
        defaulters = [r for r in att_records if r.get("percentage", 0) < 75.0]

        # 3. Timetable
        cursor.execute("""
            SELECT * FROM timetables
            WHERE department LIKE ? OR department = ?
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
        """, (f"%{dept}%", dept))
        timetable = [dict(r) for r in cursor.fetchall()]

        # 4. Scheduled Exams
        cursor.execute("""
            SELECT * FROM exams
            WHERE department LIKE ? OR department = ? OR department = 'All'
            ORDER BY exam_date ASC
        """, (f"%{dept}%", dept))
        exams = [dict(r) for r in cursor.fetchall()]

        # 5. Department Notices
        cursor.execute("""
            SELECT * FROM notices
            WHERE department LIKE ? OR department = ? OR department = 'All'
            ORDER BY created_at DESC
        """, (f"%{dept}%", dept))
        notices = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "department": dept,
        "students": students,
        "attendance": {
            "total_records": len(att_records),
            "defaulters_count": len(defaulters),
            "defaulters": defaulters,
            "all_records": att_records
        },
        "timetable": timetable,
        "exams": exams,
        "notices": notices
    })


# -----------------------------------------------------
# CIRCULARS BROADCAST BY PRINCIPAL
# GET /api/principal/circulars
# POST /api/principal/circular
# DELETE /api/principal/circular/<id>
# -----------------------------------------------------
@principal_routes.route(
    "/api/principal/circulars",
    methods=["GET"]
)
def get_circulars():
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM circulars ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "circulars": rows
    })


@principal_routes.route(
    "/api/principal/circular",
    methods=["POST"]
)
def create_circular():
    data = request.get_json(silent=True) or request.form or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    dept = data.get("department") or "All"
    target = data.get("target_audience") or "All"
    priority = data.get("priority") or "Normal"
    issued_by = data.get("issued_by") or "Dr. Lalasaheb Kashid (Principal)"
    issued_date = data.get("issued_date") or datetime.now().strftime("%Y-%m-%d")
    att_url = data.get("attachment_url") or ""

    if not title or not content:
        return jsonify({"success": False, "error": "Title and content are required."}), 400

    # Auto generate circular number if not provided
    cir_no = data.get("circular_no") or f"VPCSC/{datetime.now().year}/CIR-{int(datetime.now().timestamp()) % 10000:04d}"

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO circulars (circular_no, title, content, department, target_audience, issued_by, priority, attachment_url, issued_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cir_no, title, content, dept, target, issued_by, priority, att_url, issued_date))
        new_id = cursor.lastrowid

        # Also push into notices table so students see it immediately on their notice board
        cursor.execute("""
            INSERT INTO notices (title, content, category, department, target_year, priority, published_by)
            VALUES (?, ?, 'Circular', ?, 'All', ?, ?)
        """, (f"[{cir_no}] {title}", content, dept, priority, issued_by))

        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Official Circular '{cir_no}' issued and broadcasted successfully!",
        "circular_id": new_id,
        "circular_no": cir_no
    }), 201


@principal_routes.route(
    "/api/principal/circular/<int:circular_id>",
    methods=["DELETE"]
)
def delete_circular(circular_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM circulars WHERE id = ?", (circular_id,))
        conn.commit()
        deleted = cursor.rowcount > 0

    if not deleted:
        return jsonify({"success": False, "error": "Circular not found."}), 404

    return jsonify({"success": True, "message": "Circular archived successfully."})
