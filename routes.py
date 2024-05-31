from app import app
from flask import render_template, redirect, request, abort
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
    users.required_role([1])

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

    return render_template(template, course_name=course_name, open=open)
    # if template:
    #     return render_template(template, course_name=course_name, open=open)
    # return render_template(
    #     "error.html", message="Käyttäjän käyttöoikeutta kurssille ei voitu määrittää"
    # )


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
            return redirect("/")
    return render_template("error.html", message="Kurssille liittyminen epäonnistui")


@app.route("/courses/<course_name>/update_course", methods=["POST"])
def update_course(course_name):
    update_value = request.form["update_value"]
    print()
    print(course_name)
    print(update_value)
    print()
    courses.course_exists(course_name)
    user_id = users.user_id()
    if courses.course_owner(course_name, user_id):
        if courses.update_course(course_name, update_value):
            return redirect("/courses/" + course_name)
        return render_template(
            "error.html", message="Kurssin tilan päivitys epäonnistui"
        )
    return abort(403)
