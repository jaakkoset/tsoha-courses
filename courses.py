from app import db
from flask import abort
from sqlalchemy.sql import text


def create_course(course_name, description, id) -> bool:
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


def name_reserved(course_name) -> bool:
    sql = "SELECT id FROM courses WHERE name=:course_name"
    result = db.session.execute(text(sql), {"course_name": course_name})
    user = result.fetchone()
    if user:
        return True
    return False


def open_courses() -> list | None:
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


def my_courses_teacher(user_id) -> list | None:
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


def my_courses_student(user_id) -> list | None:
    sql = """
            SELECT 
                C.id,
                C.name,
                C.course_open,
                U.username
            FROM 
                enrollment E, 
                courses C, 
                users U
            WHERE 
                E.student_id=:user_id AND
                E.course_id=C.id AND
                C.teacher_id=U.id
            ORDER BY 
                C.name"""
    result = db.session.execute(text(sql), {"user_id": user_id})
    courses = result.fetchall()
    return courses


def enroll(course_id, user_id) -> bool:
    try:
        sql = """INSERT INTO enrollment 
                    (course_id, student_id) 
                VALUES 
                    (:course_id,:student_id)"""
        db.session.execute(
            text(sql),
            {
                "course_id": course_id,
                "student_id": user_id,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def is_enrolled(course_id, user_id) -> bool:
    sql = """
            SELECT 
                id
            FROM 
                enrollment 
            WHERE 
                student_id=:user_id AND 
                course_id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id, "user_id": user_id})
    enrolled = result.fetchone()
    if enrolled:
        return True
    return False


def course_owner(course_id, user_id) -> bool:
    sql = """
            SELECT 
                id
            FROM 
                courses 
            WHERE 
                teacher_id=:user_id AND 
                id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id, "user_id": user_id})
    owner = result.fetchone()
    if owner:
        return True
    return False


# returns (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
def course_info(course_id: int) -> tuple | None:
    sql = """SELECT
                id, 
                name,
                teacher_id,
                course_open,
                visible,
                description
            FROM courses 
            WHERE id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    data = result.fetchone()
    return data


def course_exists(course_id):
    sql = """
            SELECT id
            FROM courses 
            WHERE id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    exist = result.fetchone()
    if not exist:
        abort(404)


def update_course(course_id) -> bool:
    try:
        sql = """
                    UPDATE courses 
                    SET course_open=course_open+1
                    WHERE id=:course_id"""
        db.session.execute(
            text(sql),
            {
                "course_id": course_id,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def course_id(course_name) -> tuple | None:
    sql = """SELECT id FROM courses WHERE name=:course_name"""
    result = db.session.execute(text(sql), {"course_name": course_name})
    id = result.fetchone()[0]
    return id
