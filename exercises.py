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
            SELECT id, name
            FROM exercises
            WHERE course_id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    exercises = result.fetchall()
    return exercises


def exercise_data(exercise_id):
    sql = """
            SELECT id, course_id, name, type, question, choices, answer
            FROM exercises
            WHERE id=:exercise_id"""
    result = db.session.execute(text(sql), {"exercise_id": exercise_id})
    data = result.fetchone()
    return data


def submit(exercise_id, user_id, answer):
    correct = check_answer(exercise_id, answer)
    try:
        sql = """INSERT INTO submissions 
                    (student_id ,exercise_id,answer,correct,time) 
                VALUES 
                    (:student_id,:exercise_id,:answer,:correct,CURRENT_TIMESTAMP)"""
        db.session.execute(
            text(sql),
            {
                "student_id": user_id,
                "exercise_id": exercise_id,
                "answer": answer,
                "correct": correct,
            },
        )
        db.session.commit()
    except:
        return False
    return True


def check_answer(exercise_id, answer):
    sql = """
            SELECT answer
            FROM exercises
            WHERE id=:exercise_id"""
    result = db.session.execute(text(sql), {"exercise_id": exercise_id})
    exercises = result.fetchone()[0]
    if exercises == answer:
        return True
    return False


def submission_data(exercise_id, user_id):
    sql = """
            SELECT id,student_id ,exercise_id,answer,correct,time
            FROM submissions
            WHERE 
                exercise_id=:exercise_id AND
                student_id=:student_id
            ORDER BY time DESC"""
    result = db.session.execute(
        text(sql), {"exercise_id": exercise_id, "student_id": user_id}
    )
    submission = result.fetchone()
    print(submission)
    return submission
