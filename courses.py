from app import db

from sqlalchemy.sql import text


def create_course(course_name, id):
    try:
        sql = "INSERT INTO courses (name, teacher_id, started, course_open, visible) VALUES (:name,:techer_id,:started,:course_open,:visible)"
        db.session.execute(
            text(sql),
            {
                "name": course_name,
                "techer_id": id,
                "started": 0,
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


def list_courses():
    sql = "SELECT name FROM courses"
    result = db.session.execute(text(sql))
    course_list = result.fetchall()
    course_list = [c[0] for c in course_list]
    return course_list


def course_owner(user_id, course_id):
    pass
