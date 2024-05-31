from app import app
from flask import render_template, redirect, request, abort
import users
import courses
import exercises


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
    users.required_role([1])

    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":
        course_name = request.form["course_name"]
        description = request.form["description"]
        if len(course_name) < 1 or len(course_name) > 50:
            return render_template(
                "error.html", message="Kurssin nimen tulee olla 1-50 merkkiä pitkä"
            )
        if len(description) < 1 or len(description) > 1000:
            return render_template(
                "error.html",
                message="Kurssin kuvauksen tulee olla 1-1000 merkkiä pitkä",
            )
        if courses.name_reserved(course_name):
            return render_template("error.html", message="Kurssin nimi on varattu")
        id = users.user_id()
        if courses.create_course(course_name, description, id):
            return redirect("/courses/" + course_name)
        return render_template("error.html", message="Kurssin luonti epäonnistui")


@app.route("/courses", methods=["GET"])
def all_courses():
    users.logged_in()
    course_list = courses.all_courses()
    course_count = len(course_list)
    return render_template(
        "courses.html", course_list=course_list, course_count=course_count
    )


@app.route("/courses/<course_name>", methods=["GET"])
def course_page(course_name):
    courses.course_exists(course_name)
    users.required_role([0, 1])
    user_id = users.user_id()
    open = courses.course_open(course_name)
    description = courses.description(course_name)
    template = None

    if courses.course_owner(course_name, user_id):
        if open == 0:
            template = "course_page_t_0.html"
        elif open == 1:
            template = "course_page_t_1.html"
        elif open == 2:
            template = "course_page_t_2.html"
    elif users.is_teacher():
        if open == 1:
            template = "course_page_vt_1.html"
    elif courses.is_enrolled(course_name, user_id):
        if open == 1:
            template = "course_page_s_1.html"
        elif open == 2:
            template = "course_page_s_2.html"
    elif open == 1:
        template = "course_page_vs_1.html"
    else:
        abort(403)

    exercise_list = exercises.course_exercises(course_name)
    return render_template(
        template,
        course_name=course_name,
        open=open,
        description=description,
        exercises=exercise_list,
    )


@app.route("/my_courses", methods=["GET"])
def my_courses():
    users.logged_in()
    user_id = users.user_id()
    if users.is_teacher():
        course_list = courses.my_courses_teacher(user_id)
    elif users.is_student():
        course_list = courses.my_courses_student(user_id)
    course_count = len(course_list)
    return render_template(
        "my_courses.html", course_list=course_list, course_count=course_count
    )


@app.route("/enroll/<course_name>", methods=["GET"])
def enroll(course_name):
    courses.course_exists(course_name)
    if courses.course_open(course_name) == 1:
        users.required_role([0])
        user_id = users.user_id()
        if courses.is_enrolled(course_name, user_id):
            render_template("error.html", message="Olet jo liittynyt kurssille")
        if courses.enroll(course_name, user_id):
            return redirect("/courses/" + course_name)
    return render_template("error.html", message="Kurssille liittyminen epäonnistui")


@app.route("/courses/<course_name>/update_course", methods=["POST"])
def update_course(course_name):
    update_value = request.form["update_value"]
    courses.course_exists(course_name)
    user_id = users.user_id()
    if courses.course_owner(course_name, user_id):
        if courses.update_course(course_name, update_value):
            return redirect("/courses/" + course_name)
        return render_template(
            "error.html", message="Kurssin tilan päivitys epäonnistui"
        )
    return abort(403)


@app.route("/courses/<course_name>/add_exercise_one", methods=["GET", "POST"])
def add_exercise(course_name):
    courses.course_exists(course_name)
    user_id = users.user_id()
    if not courses.course_owner(course_name, user_id):
        abort(403)

    if request.method == "GET":
        return render_template("add_exercise_one.html", course_name=course_name)

    if request.method == "POST":
        name = request.form["name"]
        question = request.form["question"]
        answer = request.form["answer"]
        if exercises.add_exercise(course_name, name, "one", question, answer, None):
            return redirect("/courses/" + course_name)
        return render_template(
            "error.html", message="Kysymyksen lisääminen epäonnistui"
        )


@app.route("/courses/<course_name>/<exercise_id>", methods=["GET"])
def exercise_page(course_name, exercise_id):
    courses.course_exists(course_name)
    users.required_role([0, 1])
    user_id = users.user_id()
    if courses.course_owner(course_name, user_id):
        exercise = exercises.exercise_data(exercise_id)
        if exercise == None:
            abort(404)
        return render_template("exercise_page_t.html", exercise=exercise)
