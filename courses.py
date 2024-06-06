from app import db
from flask import abort
from sqlalchemy.sql import text


def create_course(course_name, description, id):
    try:
        sql = """INSERT INTO courses 
                    (name, teacher_id, course_open, visible, description) 
                VALUES 
                    (:name,:teacher_id,:course_open,:visible,:description)"""
        db.session.execute(
            text(sql),
            {
                "name": course_name,
                "teacher_id": id,
                "course_open": 0,
                "visible": 1,
                "description": description,
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
                id,
                name, 
                (SELECT username FROM users WHERE id=C.teacher_id) 
            FROM courses C 
            WHERE course_open=1
            ORDER BY name"""
    result = db.session.execute(text(sql))
    courses = result.fetchall()
    return courses


def my_courses_teacher(user_id):
    sql = """
            SELECT 
                id,
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
                course_id,
                (SELECT name FROM courses WHERE id=E.course_id) course_name,
                (SELECT course_open FROM courses WHERE id=E.course_id)
            FROM enrollment E
            WHERE student_id=:user_id
            ORDER BY course_name"""
    result = db.session.execute(text(sql), {"user_id": user_id})
    courses = result.fetchall()
    return courses


def enroll(course_name, user_id):
    c_id = course_id(course_name)
    try:
        sql = """INSERT INTO enrollment 
                    (course_id, student_id) 
                VALUES 
                    (:course_id,:student_id)"""
        db.session.execute(
            text(sql),
            {
                "course_id": c_id,
                "student_id": user_id,
            },
        )
        db.session.commit()
    except:
        return False
    return True


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
                id
            FROM 
                courses 
            WHERE 
                name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    exist = result.fetchone()
    if not exist:
        abort(404)


def course_open(course_name):
    sql = """SELECT course_open FROM courses WHERE name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    open = result.fetchone()[0]
    return open


def description(course_name):
    sql = """SELECT description FROM courses WHERE name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    description = result.fetchone()[0]
    return description


def update_course(course_name):
    try:
        sql = """
                    UPDATE courses 
                    SET course_open=course_open+1
                    WHERE name=:course_name"""
        db.session.execute(
            text(sql),
            {
                "course_name": course_name,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def course_id(course_name):
    sql = """SELECT id FROM courses WHERE name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    id = result.fetchone()[0]
    return id


def course_name(course_id):
    sql = """SELECT name FROM courses WHERE id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    id = result.fetchone()[0]
    return id
