from app import app
from flask import render_template, redirect, request
import users
import courses


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if users.login(username, password):
        return redirect("/")
    return render_template("error.html", message="Väärä tunnus tai salasana")


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/register", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        role = request.form["role"]
        if len(username) == 0 or len(username) > 30:
            return render_template(
                "error.html", message="Käyttäjätunnuksen tulee olla 1-30 merkkiä pitkä"
            )
        if len(password1) < 2 or len(password1) > 30:
            return render_template(
                "error.html", message="Salasanan tulee olla 8-30 merkkiä pitkä"
            )
        if users.username_reserved(username):
            return render_template("error.html", message="Käyttäjätunnus on varattu")
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        if role != "0" and role != "1":
            return render_template("error.html", message="Tuntematon käyttäjärooli")
        if users.register(username, password1, role):
            return redirect("/")
        return render_template("error.html", message="Rekisteröinti ei onnistunut")


@app.route("/create", methods=["GET", "POST"])
def create():
    users.is_teacher()

    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":
        course_name = request.form["course_name"]
        if len(course_name) < 1 or len(course_name) > 30:
            return render_template(
                "error.html", message="Kurssin nimen tulee olla 1-30 merkkiä pitkä"
            )
        if courses.name_reserved(course_name):
            return render_template("error.html", message="Kurssin nimi on varattu")
        id = users.user_id()
        if courses.create_course(course_name, id):
            return redirect("/")
        return render_template("error.html", message="Kurssin luonti epäonnistui")


@app.route("/courses", methods=["GET"])
def courses_route():
    users.logged_in()
    course_list = courses.list_courses()
    number_of_courses = len(course_list)
    return render_template(
        "courses.html", course_list=course_list, number_of_courses=number_of_courses
    )


@app.route("/courses/<name>", methods=["GET"])
def course(name):
    users.logged_in()
    return render_template("one_course.html", course_name=name)
