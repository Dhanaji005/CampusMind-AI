# =====================================================
# CAMPUSMIND AI - STUDENT ROUTES
# Year-aware personalized subjects, exams & notices
# =====================================================

from flask import Blueprint, jsonify, request, g
from middleware.auth_middleware import get_optional_current_user, jwt_required
from services.academic_service import (
    get_student_dashboard_data,
    get_subjects_by_year,
    get_exams_by_year,
    get_all_notices
)

student_routes = Blueprint(
    "student_routes",
    __name__
)


# -----------------------------------------------------
# STUDENT DASHBOARD ENDPOINT
# GET /api/student/dashboard
# Auto-detects student year & department from JWT or query params
# -----------------------------------------------------
@student_routes.route(
    "/api/student/dashboard",
    methods=["GET"]
)
def student_dashboard():
    current_user = get_optional_current_user()

    # Determine Year and Department
    year_of_study = request.args.get("year") or current_user.get("year_of_study") or "1st Year"
    department = request.args.get("department") or current_user.get("department") or "Computer Science"

    data = get_student_dashboard_data(
        year_of_study=year_of_study,
        department=department,
        user_id=current_user.get("user_id")
    )

    return jsonify({
        "success": True,
        "student": {
            "name": current_user.get("name", "Student"),
            "email": current_user.get("email"),
            "role": current_user.get("role", "student"),
            "department": department,
            "year_of_study": year_of_study,
            "semester": current_user.get("semester", 1),
            "student_id": current_user.get("student_id", "")
        },
        "dashboard": data
    })


# -----------------------------------------------------
# GET SUBJECTS FOR YEAR
# GET /api/student/subjects?year=3rd+Year&department=Computer+Science
# -----------------------------------------------------
@student_routes.route(
    "/api/student/subjects",
    methods=["GET"]
)
def get_subjects():
    current_user = get_optional_current_user()
    year = request.args.get("year") or current_user.get("year_of_study") or "1st Year"
    dept = request.args.get("department") or current_user.get("department") or "Computer Science"

    subjects = get_subjects_by_year(year_of_study=year, department=dept)
    return jsonify({
        "success": True,
        "year_of_study": year,
        "department": dept,
        "count": len(subjects),
        "subjects": subjects
    })


# -----------------------------------------------------
# GET EXAMS FOR YEAR
# GET /api/student/exams?year=3rd+Year&department=Computer+Science
# -----------------------------------------------------
@student_routes.route(
    "/api/student/exams",
    methods=["GET"]
)
def get_exams():
    current_user = get_optional_current_user()
    year = request.args.get("year") or current_user.get("year_of_study") or "1st Year"
    dept = request.args.get("department") or current_user.get("department") or "Computer Science"

    exams = get_exams_by_year(year_of_study=year, department=dept)
    return jsonify({
        "success": True,
        "year_of_study": year,
        "department": dept,
        "count": len(exams),
        "exams": exams
    })


# -----------------------------------------------------
# GET NOTICES FOR STUDENT
# GET /api/student/notices
# -----------------------------------------------------
@student_routes.route(
    "/api/student/notices",
    methods=["GET"]
)
def get_notices():
    current_user = get_optional_current_user()
    year = request.args.get("year") or current_user.get("year_of_study")
    dept = request.args.get("department") or current_user.get("department")

    notices = get_all_notices(target_year=year, department=dept)
    return jsonify({
        "success": True,
        "count": len(notices),
        "notices": notices
    })
