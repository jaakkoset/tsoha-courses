from app import app
from flask import render_template, redirect, request, abort
import users
import courses
import exercises

# URL quoting is to be implemented some day
# import urllib.parse
# urllib.parse.quote_plus(string, safe='', encoding=None, errors=None)
# URL = urllib.parse.quote_plus(course_name)
# urllib.parse.unquote_plus(string, encoding='utf-8', errors='replace')


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


# Creates a new course.
@app.route("/create", methods=["GET", "POST"])
def create():
    users.required_role([1])

    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":
        users.check_csrf()
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


# Lists all ongoing courses.
@app.route("/courses", methods=["GET"])
def all_courses():
    users.logged_in()
    course_list = courses.all_courses()
    course_count = len(course_list)
    return render_template(
        "courses.html", course_list=course_list, course_count=course_count
    )


# Course page for individual courses.
@app.route("/courses/<string:course_name>", methods=["GET"])
def course_page(course_name):
    courses.course_exists(course_name)
    users.required_role([0, 1])
    user_id = users.user_id()
    open = courses.course_open(course_name)
    description = courses.description(course_name)
    exercise_list = exercises.course_exercises(course_name)
    # [0 id, 1 name, correct]
    template = None
    teacher = users.is_teacher()

    if courses.course_owner(course_name, user_id):
        if open == 0:
            template = "course_page_t_0.html"
        elif open == 1:
            template = "course_page_t_1.html"
        elif open == 2:
            template = "course_page_t_2.html"
    elif courses.is_enrolled(course_name, user_id):
        exercise_list = exercises.completed_exercises(user_id, exercise_list)
        # [0 id, 1 name, 2 correct]
        if open == 1:
            template = "course_page_s_1.html"
        elif open == 2:
            template = "course_page_s_2.html"
    elif open == 1:
        template = "course_page_v_1.html"
    else:
        abort(403)

    return render_template(
        template,
        course_name=course_name,
        open=open,
        description=description,
        exercises=exercise_list,
        teacher=teacher,
    )


# Page where students see the courses in which they have enrolled,
# and teachers see the courses they own.
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


# Allows students to enroll in courses.
@app.route("/enroll/<string:course_name>", methods=["GET"])
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


# Changes the state of a course. First from not-yet-started to ongoing and
# then from ongoing to concluded. Changing the state cannot be reversed.
@app.route("/update_course", methods=["POST"])
def update_course():
    course_name = request.form["course_name"]
    courses.course_exists(course_name)
    user_id = users.user_id()
    users.check_csrf()
    if courses.course_owner(course_name, user_id):
        if courses.update_course(course_name):
            return redirect("/courses/" + course_name)
        return render_template(
            "error.html", message="Kurssin tilan päivitys epäonnistui"
        )
    return abort(403)


# Adds an exercise without answer choices.
@app.route("/add_exercise_one/<string:course_name>", methods=["GET", "POST"])
def add_exercise(course_name):
    courses.course_exists(course_name)
    user_id = users.user_id()
    if not courses.course_owner(course_name, user_id):
        abort(403)

    if request.method == "GET":
        return render_template("add_exercise_one.html", course_name=course_name)

    if request.method == "POST":
        users.check_csrf()
        name = request.form["name"]
        question = request.form["question"]
        answer = request.form["answer"]
        if exercises.add_exercise(course_name, name, "one", question, answer, None):
            return redirect("/courses/" + course_name)
        return render_template(
            "error.html", message="Kysymyksen lisääminen epäonnistui"
        )


@app.route("/courses/<string:course_name>/<int:exercise_id>", methods=["GET"])
def exercise_page(course_name, exercise_id):
    courses.course_exists(course_name)
    users.required_role([0, 1])
    user_id = users.user_id()
    exercise = exercises.exercise_data(exercise_id)
    # [0 id, 1 course_id, 2 name, 3 type, 4 question, 5 choices, 6 answer]
    if exercise == None:
        abort(404)
    if courses.course_owner(course_name, user_id):
        return render_template(
            "exercise_page_t.html", exercise=exercise, course_name=course_name
        )

    open = courses.course_open(course_name)
    if courses.is_enrolled(course_name, user_id):
        exercise = [i for i in exercise]
        exercise.pop()  # Don't send the answer to students
        # [0 id, 1 course_id, 2 name, 3 type, 4 question, 5 choices]
        return render_template(
            "exercise_page_s.html",
            exercise=exercise,
            course_name=course_name,
            show_result=0,
            submission=None,
            open=open,
        )
    return "Vain kurssin omistaja ja kursille liittyneet voivat tällä hetkellä nähdä kysymykset"


# Checks the answer sent by a student.
@app.route("/answer", methods=["POST"])
def answer():
    answer = request.form["answer"]
    course_name = request.form["course_name"]
    exercise_id = request.form["exercise_id"]
    user_id = users.user_id()
    open = courses.course_open(course_name)
    if open != 1:
        return render_template(
            "error.html",
            message="Kurssi ei ole auki. Palauttaminen ei ole mahdollista.",
        )
    if courses.is_enrolled(course_name, user_id):
        users.check_csrf()
        if not exercises.submit(exercise_id, user_id, answer):
            return render_template("error.html", message="Palautus epäonnistui")

        exercise = exercises.exercise_data(exercise_id)
        exercise = [i for i in exercise]
        exercise.pop()  # Don't send the answer to students
        # [0 id, 1 course_id, 2 name, 3 type, 4 question, 5 choices]
        submission = exercises.submission_data(exercise_id, user_id)
        # (0 id, 1 student_id , 2 exercise_id, 3 answer, 4 correct, 5 time)
        return render_template(
            "exercise_page_s.html",
            exercise=exercise,
            course_name=course_name,
            show_result=1,
            submission=submission,
            open=open,
        )
    abort(403)
