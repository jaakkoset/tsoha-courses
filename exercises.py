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
