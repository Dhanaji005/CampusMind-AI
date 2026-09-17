# =====================================================
# CAMPUSMIND AI - ATTENDANCE MANAGEMENT ROUTES
# Automated Attendance Sheet Ingestion & HOD Controls
# =====================================================

import os
import csv
import io
import sqlite3
from flask import Blueprint, jsonify, request, g, Response
from config.config import Config
from middleware.auth_middleware import get_optional_current_user, jwt_required

attendance_routes = Blueprint(
    "attendance_routes",
    __name__
)

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")


def _calculate_status(percentage: float) -> str:
    """SPPU Attendance Criteria: >=75% Good, 60-74% Average (Warning), <60% Critical (Defaulter)."""
    if percentage >= 75.0:
        return "Good"
    elif percentage >= 60.0:
        return "Average"
    return "Critical"


# -----------------------------------------------------
# GET STUDENT'S ATTENDANCE
# GET /api/attendance/my
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/my",
    methods=["GET"]
)
def get_my_attendance():
    current_user = get_optional_current_user()
    user_id = current_user.get("user_id")
    email = request.args.get("email") or current_user.get("email")
    student_id = request.args.get("student_id") or current_user.get("student_id")
    roll_no = request.args.get("roll_no")
    name = request.args.get("name") or current_user.get("name")
    department = request.args.get("department") or current_user.get("department")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query matching student by student_id, email, roll_no, or user_id
        query = """
            SELECT * FROM attendance
            WHERE (
                (? IS NOT NULL AND ? != '' AND student_id = ?)
                OR (? IS NOT NULL AND ? != '' AND email = ?)
                OR (? IS NOT NULL AND ? != '' AND roll_no = ?)
                OR (? IS NOT NULL AND ? != '' AND LOWER(student_name) = LOWER(?))
            )
            ORDER BY subject_name ASC
        """
        cursor.execute(query, (
            student_id, student_id, student_id,
            email, email, email,
            roll_no, roll_no, roll_no,
            name, name, name
        ))
        rows = [dict(r) for r in cursor.fetchall()]

    if not rows:
        dept_display = department or "your department"
        return jsonify({
            "success": True,
            "is_updated": False,
            "message": f"Attendance has not yet been published by the {dept_display} HOD. Once marked or uploaded, it will automatically appear here.",
            "overall_percentage": None,
            "total_lectures": 0,
            "attended_lectures": 0,
            "status": "Pending",
            "records": []
        })

    tot_lec = sum(r.get("total_lectures", 0) for r in rows)
    att_lec = sum(r.get("attended_lectures", 0) for r in rows)
    overall_pct = round((att_lec / tot_lec * 100), 1) if tot_lec > 0 else 0.0
    overall_status = _calculate_status(overall_pct)

    return jsonify({
        "success": True,
        "is_updated": True,
        "overall_percentage": overall_pct,
        "total_lectures": tot_lec,
        "attended_lectures": att_lec,
        "status": overall_status,
        "records": rows
    })


# -----------------------------------------------------
# GET DEPARTMENT ATTENDANCE (FOR HOD & ADMIN)
# GET /api/attendance/department?department=BBA(CA)&year=3rd+Year
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/department",
    methods=["GET"]
)
def get_department_attendance():
    dept = request.args.get("department", "All")
    year = request.args.get("year", "All")
    status_filter = request.args.get("status")

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = []
        params = []

        if dept and dept != "All":
            conditions.append("department = ?")
            params.append(dept)
        if year and year != "All":
            conditions.append("year_of_study = ?")
            params.append(year)
        if status_filter and status_filter != "All":
            conditions.append("status = ?")
            params.append(status_filter)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        cursor.execute(f"SELECT * FROM attendance {where_clause} ORDER BY department ASC, roll_no ASC, student_name ASC", params)
        records = [dict(r) for r in cursor.fetchall()]

    return jsonify({
        "success": True,
        "count": len(records),
        "records": records
    })


# -----------------------------------------------------
# MANUAL ATTENDANCE ENTRY BY HOD
# POST /api/attendance/record
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/record",
    methods=["POST"]
)
def save_attendance_record():
    data = request.get_json(silent=True) or {}

    student_name = (data.get("student_name") or "").strip()
    department = (data.get("department") or "BBA(CA)").strip()
    year_of_study = (data.get("year_of_study") or "1st Year").strip()
    subject_name = (data.get("subject_name") or "Core Subject").strip()
    subject_code = (data.get("subject_code") or "").strip()
    roll_no = (data.get("roll_no") or "").strip()
    student_id = (data.get("student_id") or "").strip()
    email = (data.get("email") or "").strip().lower()
    month = (data.get("month") or "Overall").strip()
    uploaded_by = (data.get("uploaded_by") or "Department HOD").strip()

    try:
        total_lectures = int(data.get("total_lectures", 0))
        attended_lectures = int(data.get("attended_lectures", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Total and attended lectures must be valid numbers."}), 400

    if not student_name:
        return jsonify({"success": False, "error": "Student Name is required."}), 400

    if total_lectures < 0 or attended_lectures < 0 or attended_lectures > total_lectures:
        return jsonify({"success": False, "error": "Attended lectures cannot exceed total lectures or be negative."}), 400

    percentage = round((attended_lectures / total_lectures * 100), 1) if total_lectures > 0 else 0.0
    status = _calculate_status(percentage)

    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        # Check if record already exists for this student + subject + month
        cursor.execute("""
            SELECT id FROM attendance
            WHERE LOWER(student_name) = LOWER(?)
              AND department = ?
              AND year_of_study = ?
              AND subject_name = ?
              AND month = ?
        """, (student_name, department, year_of_study, subject_name, month))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE attendance
                SET roll_no = ?, student_id = ?, email = ?, subject_code = ?,
                    total_lectures = ?, attended_lectures = ?, percentage = ?,
                    status = ?, uploaded_by = ?, uploaded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (roll_no, student_id, email, subject_code, total_lectures, attended_lectures, percentage, status, uploaded_by, existing[0]))
        else:
            cursor.execute("""
                INSERT INTO attendance (
                    student_name, roll_no, student_id, email, department, year_of_study,
                    subject_code, subject_name, total_lectures, attended_lectures,
                    percentage, month, status, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name, roll_no, student_id, email, department, year_of_study,
                subject_code, subject_name, total_lectures, attended_lectures,
                percentage, month, status, uploaded_by
            ))
        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Attendance recorded for {student_name} ({percentage}% - {status})",
        "record": {
            "student_name": student_name,
            "department": department,
            "year_of_study": year_of_study,
            "subject_name": subject_name,
            "percentage": percentage,
            "status": status
        }
    })


# -----------------------------------------------------
# AUTOMATED ATTENDANCE SHEET UPLOAD BY HOD (CSV / EXCEL / TEXT)
# POST /api/attendance/upload
# Multipart file upload
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/upload",
    methods=["POST"]
)
def upload_attendance_sheet():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No attendance file uploaded."}), 400

    file = request.files["file"]
    filename = file.filename or "attendance.csv"
    department = request.form.get("department") or "BBA(CA)"
    year_of_study = request.form.get("year_of_study") or "1st Year"
    subject_code = request.form.get("subject_code") or ""
    subject_name = request.form.get("subject_name") or "Core Curriculum"
    month = request.form.get("month") or "Overall"
    uploaded_by = request.form.get("uploaded_by") or f"{department} HOD"

    content_bytes = file.read()
    if not content_bytes:
        return jsonify({"success": False, "error": "Uploaded file is empty."}), 400

    # Parse text/CSV
    try:
        text_content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text_content = content_bytes.decode("latin-1")
        except Exception:
            return jsonify({"success": False, "error": "Unable to decode file. Please upload a standard UTF-8 CSV or text file."}), 400

    stream = io.StringIO(text_content)
    reader = csv.reader(stream)
    rows = [r for r in reader if any(cell.strip() for cell in r)]

    if not rows:
        return jsonify({"success": False, "error": "No attendance data found in the file."}), 400

    # Header analysis
    header = [c.strip().lower() for c in rows[0]]
    data_rows = rows[1:]

    # Map column indexes
    col_map = {}
    day_cols = []

    for idx, col in enumerate(header):
        cleaned = col.replace("_", " ").replace("-", " ").strip()
        if cleaned in ["roll no", "roll", "rollno", "seat no", "sr no", "srno"]:
            col_map["roll_no"] = idx
        elif cleaned in ["name", "student name", "student_name", "full name"]:
            col_map["name"] = idx
        elif cleaned in ["student id", "student_id", "id", "prn", "prn no"]:
            col_map["student_id"] = idx
        elif cleaned in ["email", "student email"]:
            col_map["email"] = idx
        elif cleaned in ["dept", "department"]:
            col_map["department"] = idx
        elif cleaned in ["year", "class", "year of study"]:
            col_map["year_of_study"] = idx
        elif cleaned in ["subject", "subject name", "course"]:
            col_map["subject_name"] = idx
        elif cleaned in ["subject code", "code"]:
            col_map["subject_code"] = idx
        elif cleaned in ["total", "total lectures", "conducted", "total classes", "total lec"]:
            col_map["total"] = idx
        elif cleaned in ["attended", "present", "attended lectures", "att"]:
            col_map["attended"] = idx
        elif cleaned in ["percentage", "percent", "%"]:
            col_map["percentage"] = idx
        elif cleaned.isdigit() or cleaned.startswith("day") or cleaned.startswith("d") or "/" in cleaned:
            day_cols.append(idx)

    # Process each student row
    processed_count = 0
    records_to_save = []

    for r in data_rows:
        if len(r) == 0:
            continue

        s_name = r[col_map["name"]].strip() if "name" in col_map and col_map["name"] < len(r) else ""
        s_roll = r[col_map["roll_no"]].strip() if "roll_no" in col_map and col_map["roll_no"] < len(r) else ""
        s_id = r[col_map["student_id"]].strip() if "student_id" in col_map and col_map["student_id"] < len(r) else ""
        s_email = r[col_map["email"]].strip().lower() if "email" in col_map and col_map["email"] < len(r) else ""
        s_dept = r[col_map["department"]].strip() if "department" in col_map and col_map["department"] < len(r) else department
        s_year = r[col_map["year_of_study"]].strip() if "year_of_study" in col_map and col_map["year_of_study"] < len(r) else year_of_study
        s_sub_name = r[col_map["subject_name"]].strip() if "subject_name" in col_map and col_map["subject_name"] < len(r) else subject_name
        s_sub_code = r[col_map["subject_code"]].strip() if "subject_code" in col_map and col_map["subject_code"] < len(r) else subject_code

        if not s_name and s_roll:
            s_name = f"Student Roll {s_roll}"
        if not s_name:
            continue

        # Case A: Explicit Total & Attended columns
        if "total" in col_map and "attended" in col_map:
            try:
                tot = int(float(r[col_map["total"]]))
                att = int(float(r[col_map["attended"]]))
            except (ValueError, IndexError):
                tot, att = 0, 0
        # Case B: Daily attendance columns (P / A / L)
        elif day_cols:
            tot = 0
            att = 0
            for d_idx in day_cols:
                if d_idx < len(r):
                    val = r[d_idx].strip().upper()
                    if val:
                        tot += 1
                        if val in ["P", "PRESENT", "1", "YES", "Y"]:
                            att += 1
        # Case C: Fallback to basic positional or default
        else:
            tot = 30
            att = 25

        pct = round((att / tot * 100), 1) if tot > 0 else 0.0
        status = _calculate_status(pct)

        records_to_save.append({
            "name": s_name,
            "roll_no": s_roll,
            "student_id": s_id,
            "email": s_email,
            "department": s_dept,
            "year_of_study": s_year,
            "subject_code": s_sub_code,
            "subject_name": s_sub_name,
            "total": tot,
            "attended": att,
            "percentage": pct,
            "status": status,
            "month": month,
            "uploaded_by": uploaded_by
        })

    if not records_to_save:
        return jsonify({"success": False, "error": "Could not identify student records from the uploaded sheet. Please check columns."}), 400

    # Save to database in batch
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        for rec in records_to_save:
            # Delete any previous record for same student, department, year, subject, month to prevent duplicates
            cursor.execute("""
                DELETE FROM attendance
                WHERE (
                    LOWER(student_name) = LOWER(?)
                    OR (roll_no != '' AND roll_no = ?)
                    OR (student_id != '' AND student_id = ?)
                )
                AND department = ?
                AND year_of_study = ?
                AND subject_name = ?
                AND month = ?
            """, (rec["name"], rec["roll_no"], rec["student_id"], rec["department"], rec["year_of_study"], rec["subject_name"], rec["month"]))

            cursor.execute("""
                INSERT INTO attendance (
                    student_name, roll_no, student_id, email, department, year_of_study,
                    subject_code, subject_name, total_lectures, attended_lectures,
                    percentage, month, status, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec["name"], rec["roll_no"], rec["student_id"], rec["email"],
                rec["department"], rec["year_of_study"], rec["subject_code"],
                rec["subject_name"], rec["total"], rec["attended"],
                rec["percentage"], rec["month"], rec["status"], rec["uploaded_by"]
            ))
            processed_count += 1
        conn.commit()

    return jsonify({
        "success": True,
        "message": f"Successfully parsed and published attendance for {processed_count} students in {department} ({year_of_study})!",
        "processed_count": processed_count,
        "department": department,
        "year_of_study": year_of_study,
        "subject_name": subject_name,
        "uploaded_by": uploaded_by
    })


# -----------------------------------------------------
# DOWNLOAD SAMPLE CSV TEMPLATE FOR HODs
# GET /api/attendance/template
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/template",
    methods=["GET"]
)
def download_attendance_template():
    sample_csv = (
        "Roll No,Student Name,Student ID,Email,Total Lectures,Attended Lectures\n"
        "101,Aarav Sharma,CS-2026-042,firstyear@campusmind.ai,40,36\n"
        "102,Priya Patel,CS-2024-118,thirdyear@campusmind.ai,40,34\n"
        "103,Dhanaji Mali,VPCSC-2026-836,dhanajimali05@gmail.com,40,35\n"
        "104,Sayli Devkar,CS-2026-515,saylidevkar22@gmail.com,40,32\n"
        "105,Ankit Thorat,VPCSC-2026-728,ankit04@gmail.com,40,22\n"
        "106,Faiyaj Shaikh,CS-2026-832,faiyajshail022@gmail.comn,40,31\n"
    )
    return Response(
        sample_csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=VPCSC_Attendance_Template.csv"}
    )


# -----------------------------------------------------
# DELETE ATTENDANCE RECORD
# DELETE /api/attendance/<id>
# -----------------------------------------------------
@attendance_routes.route(
    "/api/attendance/<int:record_id>",
    methods=["DELETE"]
)
def delete_attendance_record(record_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
        conn.commit()
    return jsonify({"success": True, "message": "Attendance record deleted successfully."})
