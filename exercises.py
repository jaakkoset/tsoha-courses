from app import db
from sqlalchemy.sql import text
import courses


def add_exercise(course_name, name, type, question, answer, choices):
    try:
        course_id = courses.course_id(course_name)
        print(course_id)
        sql = """
                INSERT INTO 
                    exercises (course_id,name,type,question,answer,choices)
                VALUES
                    (:course_id,:name,:type,:question,:answer,:choices)"""
        db.session.execute(
            text(sql),
            {
                "course_id": course_id,
                "name": name,
                "type": type,
                "question": question,
                "answer": answer,
                "choices": choices,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def course_exercises(course_name):
    course_id = courses.course_id(course_name)
    sql = """
            SELECT name
            FROM exercises
            WHERE course_id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    exercises = result.fetchall()
    # exercises = [e[0] for e in exercises]
    return exercises
