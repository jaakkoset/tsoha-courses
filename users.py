import os
from app import db
from flask import abort, session, request
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text


def login(name, password):
    sql = "SELECT id, password, role FROM users WHERE username=:name"
    result = db.session.execute(text(sql), {"name": name})
    user = result.fetchone()
    if not user:
        return False
    if check_password_hash(user[1], password):
        session["user_id"] = user[0]
        session["username"] = name
        session["role"] = user[2]
        session["csrf_token"] = os.urandom(16).hex()
        return True
    return False


def logout():
    del session["user_id"]
    del session["username"]
    del session["role"]
    del session["csrf_token"]


def register(name, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = (
            "INSERT INTO users (username,password,role) VALUES (:name,:password,:role)"
        )
        db.session.execute(
            text(sql), {"name": name, "password": hash_value, "role": role}
        )
        db.session.commit()
    except:
        return False
    return login(name, password)


def username_reserved(username):
    sql = "SELECT username FROM users WHERE username=:username"
    query = db.session.execute(text(sql), {"username": username})
    result = query.fetchone()
    if result:
        return True
    return False


def user_id():
    return session.get("user_id")


def user_role():
    return session.get("role")


def required_role(role: list):
    if session.get("role") not in role:
        abort(403)


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)


def username(user_id) -> str:
    sql = """
            SELECT username
            FROM users
            WHERE id=:user_id"""
    result = db.session.execute(text(sql), {"user_id": user_id})
    name = result.fetchone()[0]
    return name
