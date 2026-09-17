# =====================================================
# CAMPUSMIND AI - ACADEMIC SERVICE
# Year-aware subjects, exams, notices & campus events
# =====================================================

import os
import sqlite3
from datetime import datetime
from config.config import Config

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")


def _resolve_department_aliases(department: str) -> list:
    """Returns all common aliases for a department to ensure robust lookup."""
    d = (department or "").strip().lower()
    if any(k in d for k in ["bba(ca)", "bba-ca", "bbaca", "bca", "computer application"]):
        return ["BBA(CA)", "Computer Application", "BBA-CA", "BCA"]
    if any(k in d for k in ["bcs", "computer science", "b.sc.(computer science)", "b.sc (cs)"]):
        return ["BCS", "Computer Science", "B.Sc (Computer Science)"]
    if any(k in d for k in ["bba", "business administration"]):
        return ["BBA", "Business Administration"]
    if any(k in d for k in ["b.com", "bcom", "commerce"]):
        return ["B.Com", "Commerce"]
    if any(k in d for k in ["b.sc", "bsc", "science"]):
        return ["B.Sc", "Science"]
    if any(k in d for k in ["m.sc", "msc"]):
        return ["M.Sc", "M.Sc (Computer Science)"]
    return [department] if department else ["All"]

def get_student_attendance(student_id: str = None, email: str = None, name: str = None, department: str = None) -> dict:
    """Returns official attendance records and SPPU compliance status published by Department HOD."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM attendance
            WHERE (
                (? IS NOT NULL AND ? != '' AND student_id = ?)
                OR (? IS NOT NULL AND ? != '' AND email = ?)
                OR (? IS NOT NULL AND ? != '' AND LOWER(student_name) = LOWER(?))
            )
            ORDER BY subject_name ASC
        """, (student_id, student_id, student_id, email, email, email, name, name, name))
        rows = [dict(r) for r in cursor.fetchall()]

        if rows:
            tot_lec = sum(r.get("total_lectures", 0) for r in rows)
            att_lec = sum(r.get("attended_lectures", 0) for r in rows)
            overall_pct = round((att_lec / tot_lec * 100), 1) if tot_lec > 0 else 0.0
            overall_status = "Good" if overall_pct >= 75.0 else ("Average" if overall_pct >= 60.0 else "Critical")
            sppu_msg = (
                "Eligible for SPPU University Examinations (>= 75%)." if overall_pct >= 75.0 else
                ("Warning: Attendance is between 60% and 74%. Must attend remaining lectures to reach SPPU 75% requirement." if overall_pct >= 60.0 else
                 "Critical Defaulter: Attendance is below 60%. University examination clearance at risk according to SPPU regulations.")
            )
            return {
                "is_updated": True,
                "overall_percentage": overall_pct,
                "total_lectures": tot_lec,
                "attended_lectures": att_lec,
                "status": overall_status,
                "sppu_compliance_message": sppu_msg,
                "records": rows
            }
        else:
            dept_name = department or "your department"
            return {
                "is_updated": False,
                "overall_percentage": None,
                "total_lectures": 0,
                "attended_lectures": 0,
                "status": "Pending",
                "message": f"Attendance not yet published by {dept_name} HOD. Once uploaded or marked, your verified attendance will appear here automatically.",
                "records": []
            }
    finally:
        conn.close()


def get_student_dashboard_data(year_of_study: str = "1st Year", department: str = "Computer Science", user_id: int = None) -> dict:
    """
    Synthesizes a personalized academic cockpit for registered students:
    - Subjects filtered specifically for their year of study and department
    - Upcoming exams and schedules filtered for their year
    - Year-specific and campus-wide official notices
    - Upcoming campus events & workshops
    - Academic statistics (total credits, upcoming exams count, active notices count)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    dept_aliases = _resolve_department_aliases(department)
    dept_placeholders = ",".join(["?"] * len(dept_aliases))

    try:
        cursor = conn.cursor()

        # 1. Fetch Subjects for Student's Year & Department
        cursor.execute(f"""
            SELECT * FROM subjects
            WHERE (year_of_study = ? OR year_of_study = 'All')
              AND (department IN ({dept_placeholders}) OR department = 'All')
            ORDER BY semester ASC, id ASC
        """, (year_of_study, *dept_aliases))
        subjects = [dict(row) for row in cursor.fetchall()]

        # 2. Fetch Upcoming Exams for Student's Year & Department
        cursor.execute(f"""
            SELECT * FROM exams
            WHERE (year_of_study = ? OR year_of_study = 'All')
              AND (department IN ({dept_placeholders}) OR department = 'All')
            ORDER BY exam_date ASC
        """, (year_of_study, *dept_aliases))
        exams = [dict(row) for row in cursor.fetchall()]

        # 3. Fetch Targeted Notices (matching student's year or 'All')
        cursor.execute(f"""
            SELECT * FROM notices
            WHERE (target_year = ? OR target_year = 'All')
              AND (department IN ({dept_placeholders}) OR department = 'All')
            ORDER BY 
                CASE priority
                    WHEN 'Urgent' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Normal' THEN 3
                    ELSE 4
                END,
                created_at DESC
            LIMIT 10
        """, (year_of_study, *dept_aliases))
        notices = [dict(row) for row in cursor.fetchall()]

        # 4. Fetch Campus Events
        cursor.execute("""
            SELECT * FROM events
            ORDER BY event_date ASC
            LIMIT 6
        """)
        events = [dict(row) for row in cursor.fetchall()]

        # 5. Fetch Attendance (Recorded / Uploaded by Department HOD)
        user_info = None
        if user_id:
            try:
                cursor.execute("SELECT student_id, email, name FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                if user_row:
                    user_info = dict(user_row)
            except Exception:
                user_info = None

        s_id = user_info.get("student_id") if user_info else None
        s_email = user_info.get("email") if user_info else None
        s_name = user_info.get("name") if user_info else None

        attendance_summary = get_student_attendance(student_id=s_id, email=s_email, name=s_name, department=department)


        # Calculate academic summary
        total_credits = sum(s.get("credits", 4) for s in subjects)
        total_subjects = len(subjects)
        upcoming_exams_count = len(exams)

        return {
            "year_of_study": year_of_study,
            "department": department,
            "summary": {
                "total_subjects": total_subjects,
                "total_credits": total_credits,
                "upcoming_exams_count": upcoming_exams_count,
                "active_notices_count": len(notices),
                "attendance_percentage": attendance_summary.get("overall_percentage"),
                "attendance_status": attendance_summary.get("status")
            },
            "subjects": subjects,
            "exams": exams,
            "notices": notices,
            "events": events,
            "attendance": attendance_summary
        }

    finally:
        conn.close()


def get_subjects_by_year(year_of_study: str, department: str = "Computer Science") -> list:
    """Returns subjects for a specific year and department."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    dept_aliases = _resolve_department_aliases(department)
    dept_placeholders = ",".join(["?"] * len(dept_aliases))
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM subjects
            WHERE (year_of_study = ? OR year_of_study = 'All')
              AND (department IN ({dept_placeholders}) OR department = 'All')
            ORDER BY semester ASC, id ASC
        """, (year_of_study, *dept_aliases))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_exams_by_year(year_of_study: str, department: str = "Computer Science") -> list:
    """Returns upcoming exams for a specific year and department."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    dept_aliases = _resolve_department_aliases(department)
    dept_placeholders = ",".join(["?"] * len(dept_aliases))
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM exams
            WHERE (year_of_study = ? OR year_of_study = 'All')
              AND (department IN ({dept_placeholders}) OR department = 'All')
            ORDER BY exam_date ASC
        """, (year_of_study, *dept_aliases))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_notices(target_year: str = None, department: str = None) -> list:
    """Returns notices with optional filtering."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        if target_year and department:
            cursor.execute("""
                SELECT * FROM notices
                WHERE (target_year = ? OR target_year = 'All')
                  AND (department = ? OR department = 'All')
                ORDER BY created_at DESC
            """, (target_year, department))
        elif target_year:
            cursor.execute("""
                SELECT * FROM notices
                WHERE (target_year = ? OR target_year = 'All')
                ORDER BY created_at DESC
            """, (target_year,))
        else:
            cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def create_notice(title: str, content: str, category: str = "Academic",
                  department: str = "All", target_year: str = "All",
                  priority: str = "Normal", published_by: str = "Campus Admin") -> dict:
    """Creates a new campus notice."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notices (title, content, category, department, target_year, priority, published_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, content, category, department, target_year, priority, published_by))
        notice_id = cursor.lastrowid
        conn.commit()
        return {
            "id": notice_id,
            "title": title,
            "category": category,
            "department": department,
            "target_year": target_year,
            "priority": priority,
            "published_by": published_by
        }
    finally:
        conn.close()


def delete_notice(notice_id: int) -> bool:
    """Deletes a notice by ID."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def create_event(title: str, description: str, category: str = "Workshop",
                 venue: str = "Campus Auditorium", event_date: str = None,
                 organizer: str = "Student Council", registration_link: str = "") -> dict:
    """Creates a new campus event."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        if not event_date:
            event_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO events (title, description, category, venue, event_date, organizer, registration_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, category, venue, event_date, organizer, registration_link))
        event_id = cursor.lastrowid
        conn.commit()
        return {
            "id": event_id,
            "title": title,
            "category": category,
            "venue": venue,
            "event_date": event_date,
            "organizer": organizer
        }
    finally:
        conn.close()


def get_all_events() -> list:
    """Returns all campus events."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
