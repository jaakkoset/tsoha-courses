from app import db
from flask import abort
from sqlalchemy.sql import text


def create_course(course_name, id):
    try:
        sql = """INSERT INTO courses 
                    (name, teacher_id, course_open, visible) 
                VALUES 
                    (:name,:teacher_id,:course_open,:visible)"""
        db.session.execute(
            text(sql),
            {
                "name": course_name,
                "teacher_id": id,
                "course_open": 0,
                "visible": 1,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def name_reserved(course_name):
    sql = "SELECT id FROM courses WHERE name=:course_name"
    result = db.session.execute(text(sql), {"course_name": course_name})
    user = result.fetchone()
    if user:
        return True
    return False


def all_courses():
    sql = """
            SELECT 
                name, 
                (SELECT username FROM users WHERE id=C.teacher_id) 
            FROM courses C 
            ORDER BY name"""
    result = db.session.execute(text(sql))
    courses = result.fetchall()
    return courses


def my_courses_teacher(user_id):
    sql = """
            SELECT 
                name, 
                course_open
            FROM courses
            WHERE teacher_id=:user_id AND visible=1
            ORDER BY name"""
    result = db.session.execute(text(sql), {"user_id": user_id})
    courses = result.fetchall()
    return courses


def my_courses_student(user_id):
    sql = """
            SELECT 
                (SELECT name FROM courses WHERE id=E.course_id) course_name,
                (SELECT course_open FROM courses WHERE id=E.course_id)
            FROM enrollment E
            WHERE student_id=:user_id
            ORDER BY course_name"""
    result = db.session.execute(text(sql), {"user_id": user_id})
    courses = result.fetchall()
    print()
    print("courses:", courses)
    return courses


def enroll(course_name, student_id):
    pass


def is_enrolled(course_name, user_id):
    sql = """
            SELECT 
                id
            FROM 
                enrollment 
            WHERE 
                student_id=:user_id AND 
                course_id=(SELECT id FROM courses WHERE name=:course_name)"""
    result = db.session.execute(
        text(sql), {"course_name": course_name, "user_id": user_id}
    )
    enrolled = result.fetchone()
    if enrolled:
        return True
    return False


def course_owner(course_name, user_id):
    sql = """
            SELECT 
                id
            FROM 
                courses 
            WHERE 
                teacher_id=:user_id AND 
                name=:course_name"""
    result = db.session.execute(
        text(sql), {"course_name": course_name, "user_id": user_id}
    )
    owner = result.fetchone()
    if owner:
        return True
    return False


def course_exists(course_name):
    sql = """
            SELECT 
                COALESCE(id, 0)
            FROM 
                courses 
            WHERE 
                name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    enrolled = result.fetchone()
    if not enrolled:
        abort(404)
