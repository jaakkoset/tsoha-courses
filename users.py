from app import db
from flask import session
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
        return True
    return False


def logout():
    del session["user_id"]
    del session["username"]


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
        print("users.register() False")
        return False
    return login(name, password)


def user_id():
    return session.get("user_id", 0)


def username_reserved(username):
    sql = "SELECT username FROM users WHERE username=(:username)"
    query = db.session.execute(text(sql), {"username": username})
    result = query.fetchone()
    if result:
        return True
    return False
