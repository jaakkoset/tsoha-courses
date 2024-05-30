from app import db

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


def my_courses_teacher(teacher_id):
    sql = """
            SELECT 
                name, 
                course_open
            FROM courses
            WHERE teacher_id=:teacher_id AND visible=1
            ORDER BY name"""
    result = db.session.execute(text(sql), {"teacher_id": teacher_id})
    courses = result.fetchall()
    return courses


def my_courses_student():
    pass


def course_owner(user_id, course_id):
    pass
