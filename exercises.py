from app import db
from sqlalchemy.sql import text
import courses


def add_exercise(course_id, name, type, question, answer, choices):
    try:
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


def course_exercises(course_id):
    sql = """
            SELECT id, name
            FROM exercises
            WHERE course_id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    exercises = result.fetchall()
    exercises = [[e[0], e[1], None] for e in exercises]
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
        return 1
    return 0


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
    return submission


def completed_exercises(user_id, completed_exercises):
    exercises = [[c[0], c[1], 0] for c in completed_exercises]
    for row in exercises:
        sql = """
                SELECT id,correct
                FROM submissions
                WHERE 
                    exercise_id=:exercise_id AND
                    student_id=:user_id AND
                    correct=1"""
        result = db.session.execute(
            text(sql), {"exercise_id": row[0], "user_id": user_id}
        )
        completed = result.fetchone()
        if completed:
            row[2] = 1

    return exercises
