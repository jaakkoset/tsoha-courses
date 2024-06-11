from app import db
from sqlalchemy.sql import text
import courses


def add_exercise(course_id, name, type, question, answer, choices) -> bool:
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


def course_exercises(course_id: int) -> list | None:
    sql = """
            SELECT id, name
            FROM exercises
            WHERE course_id=:course_id"""
    result = db.session.execute(text(sql), {"course_id": course_id})
    exercises = result.fetchall()
    return exercises


def exercise_info(exercise_id: int) -> tuple | None:
    sql = """
            SELECT id, course_id, name, type, question, choices, answer
            FROM exercises
            WHERE id=:exercise_id"""
    result = db.session.execute(text(sql), {"exercise_id": exercise_id})
    data = result.fetchone()
    return data


def submit(exercise_id, user_id, answer) -> bool:
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


def submission_data(exercise_id, user_id) -> tuple | None:
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


def completed_exercises(user_id: int, course_id: list) -> dict:
    sql = """
            SELECT 
                DISTINCT(S.exercise_id),
                S.correct
            FROM 
                submissions S, 
                exercises E
            WHERE 
                E.course_id=:course_id AND
                E.id=S.exercise_id AND
                S.student_id=:user_id AND
                S.correct=1"""
    result = db.session.execute(text(sql), {"course_id": course_id, "user_id": user_id})
    completed = result.fetchall()
    completed = {i[0]: i[1] for i in completed}
    return completed


def last_submission(user_id, exercise_id) -> tuple | None:
    sql = """
            SELECT 
                answer, 
                correct
            FROM 
                submissions
            WHERE 
                student_id=:user_id AND
                exercise_id=:exercise_id
            ORDER BY
                time DESC
            LIMIT 1"""
    result = db.session.execute(
        text(sql), {"user_id": user_id, "exercise_id": exercise_id}
    )
    last = result.fetchone()
    return last


def exercise_solved(user_id, exercise_id) -> tuple | None:
    sql = """
            SELECT 
                id
            FROM 
                submissions
            WHERE 
                student_id=:user_id AND
                exercise_id=:exercise_id AND
                correct=1"""
    result = db.session.execute(
        text(sql), {"user_id": user_id, "exercise_id": exercise_id}
    )
    solved = result.fetchone()
    return solved
