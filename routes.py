from app import app
from flask import render_template, redirect, request, abort
import users
import courses
import exercises
import random


@app.route("/")
def index():
    return render_template("index.html", error_login=None)


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if users.login(username, password):
        return redirect("/")
    error_login = "Väärä tunnus tai salasana"
    return render_template("index.html", error_login=error_login)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/register", methods=["get", "post"])
def register():
    error_name_length = None
    error_name_reserved = None
    error_spaces = None
    error_password_length = None
    error_differing_passwords = None

    if request.method == "GET":
        return render_template(
            "register.html",
            error_name_length=error_name_length,
            error_name_reserved=error_name_reserved,
            error_spaces=error_spaces,
            error_password_length=error_password_length,
            error_differing_passwords=error_differing_passwords,
        )
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        role = request.form["role"]
        error = False
        if len(username) == 0 or len(username) > 30:
            error_name_length = "Käyttäjätunnuksen tulee olla 1-30 merkkiä pitkä"
            error = True
        if users.username_reserved(username):
            error_name_reserved = "Käyttäjätunnus on varattu"
            error = True
        if len(username) > 0:
            if username[0] == " " or username[-1] == " ":
                error_spaces = "Ei välilyontejä käyttäjätunnuksen alkuun tai loppuun"
                error = True
        if len(password1) < 8 or len(password1) > 30:
            error_password_length = "Salasanan tulee olla 8-30 merkkiä pitkä"
            error = True
        if password1 != password2:
            error_differing_passwords = "Salasanat eroavat"
            error = True
        if role != "0" and role != "1":
            return render_template("error.html", message="Tuntematon käyttäjärooli")

        if error:
            return render_template(
                "register.html",
                error_name_length=error_name_length,
                error_name_reserved=error_name_reserved,
                error_spaces=error_spaces,
                error_password_length=error_password_length,
                error_differing_passwords=error_differing_passwords,
            )
        if users.register(username, password1, role):
            return redirect("/")
        return render_template("error.html", message="Rekisteröinti ei onnistunut")


# Creates a new course.
@app.route("/create", methods=["GET", "POST"])
def create():
    users.required_role([1])
    error_name_length = None
    error_name_reserved = None
    error_spaces = None
    error_description = None
    display_description = ""

    if request.method == "GET":
        return render_template(
            "create.html",
            error_name_length=error_name_length,
            error_name_reserved=error_name_reserved,
            error_spaces=error_spaces,
            error_description=error_description,
            display_description=display_description,
        )

    if request.method == "POST":
        users.check_csrf()
        course_name = request.form["course_name"]
        description = request.form["description"]
        error = False

        if len(course_name) < 1 or len(course_name) > 50:
            error_name_length = "Kurssin nimen tulee olla 1-50 merkkiä pitkä"
            error = True
        if courses.name_reserved(course_name):
            error_name_reserved = "Kurssin nimi on varattu"
            error = True
        if len(course_name) > 0:
            if course_name[0] == " " or course_name[-1] == " ":
                error_spaces = "Ei välilyöntejä nimen alkuun tai loppuun"
                error = True
        if len(description) < 1 or len(description) > 1000:
            error_description = "Kurssin kuvauksen tulee olla 1-1000 merkkiä pitkä"
            error = True

        if error:
            display_description = description
            return render_template(
                "create.html",
                error_name_length=error_name_length,
                error_name_reserved=error_name_reserved,
                error_spaces=error_spaces,
                error_description=error_description,
                display_description=display_description,
            )

        teacher_id = users.user_id()
        if courses.create_course(course_name, description, teacher_id):
            course_id = courses.course_id(course_name)
            return redirect("/courses/" + str(course_id))
        return render_template("error.html", message="Kurssin luonti epäonnistui")


# Lists all ongoing courses.
@app.route("/courses", methods=["GET", "POST"])
def open_courses():
    users.required_role([0, 1])
    if request.method == "GET":
        page_nro = 1
        search_type = "page"
    if request.method == "POST":
        search_type = request.form["search_type"]
        if search_type == "page":
            page_nro = int(request.form["page"])

    if search_type == "page":
        search_by_name = False
        searched_name = None
        course_count = courses.count_open_courses()
        if course_count % 20 == 0:
            pages = course_count // 20
        else:
            pages = course_count // 20 + 1

        if page_nro < 1:
            page_nro = 1
        if page_nro > pages:
            page_nro = pages
        offset = page_nro - 1
        offset = 20 * offset
        # [0 id, 1 course_name, 2 teacher_name]
        course_list = courses.open_courses(offset)

    if search_type == "course_name":
        search_by_name = True
        # searched_name = request.form["searched_name"]
        course_count = courses.count_open_courses()
        course_name = request.form["course_name"]
        searched_name = course_name
        # [0 id, 1 course_name, 2 teacher_name]
        course_list = courses.search_course_by_name(course_name)
        page_nro = 1
        pages = 1

    return render_template(
        "courses.html",
        course_list=course_list,
        course_count=course_count,
        page_nro=page_nro,
        pages=pages,
        search_by_name=search_by_name,
        searched_name=searched_name,
    )


# Course page for individual courses.
@app.route("/courses/<int:course_id>", methods=["GET"])
def course_page(course_id):
    users.required_role([0, 1])
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    course_info = courses.course_info(course_id)
    teacher_name = users.username(course_info[2])
    user_id = users.user_id()
    # [0 id, 1 name]
    exercise_list = exercises.course_exercises(course_id)
    nro_exercises = len(exercise_list)
    completed_exercises = None
    nro_completed = None
    # Used on course_page_exercises.html
    enrolled = None
    # role = users.user_role()
    open = course_info[3]

    if courses.course_owner(course_id, user_id):
        if open == 0:
            template = "course_page_t_0.html"
        elif open == 1:
            template = "course_page_t_1.html"
        elif open == 2:
            template = "course_page_t_2.html"
    elif courses.is_enrolled(course_id, user_id):
        # [0 id, 1 name, 2 correct]
        completed_exercises = exercises.completed_exercises(user_id, course_id)
        nro_completed = len(completed_exercises)
        enrolled = True
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
        course_name=course_info[1],
        teacher_name=teacher_name,
        nro_exercises=nro_exercises,
        completed_exercises=completed_exercises,
        nro_completed=nro_completed,
        course_id=course_id,
        open=open,
        description=course_info[5],
        exercises=exercise_list,
        enrolled=enrolled,
    )


# Page where students see the courses in which they have enrolled,
# and teachers see the courses they own.
@app.route("/my_courses", methods=["GET", "POST"])
def my_courses():
    users.required_role([0, 1])
    user_id = users.user_id()
    role = users.user_role()

    if request.method == "GET":
        page_nro = 1
        search_type = "page"
    if request.method == "POST":
        search_type = request.form["search_type"]
        if search_type == "page":
            page_nro = int(request.form["page"])

    if role == 1:
        course_count = courses.count_my_courses_teacher(user_id)
    elif role == 0:
        course_count = courses.count_my_courses_student(user_id)

    if search_type == "page":
        search_by_name = False
        searched_name = None
        if course_count % 20 == 0:
            pages = course_count // 20
        else:
            pages = course_count // 20 + 1
        if pages < 1:
            pages = 1
        if page_nro < 1:
            page_nro = 1
        if page_nro > pages:
            page_nro = pages
        offset = page_nro - 1
        offset = 20 * offset
        if role == 1:
            # [0 id, 1 course_name, 2 course_open]
            course_list = courses.my_courses_teacher(user_id, offset)
        elif role == 0:
            # [0 id, 1 course_name, 2 course_open, 3 teacher_name]
            course_list = courses.my_courses_student(user_id, offset)

    if search_type == "course_name":
        search_by_name = True
        course_name = request.form["course_name"]
        searched_name = course_name
        offset = 0
        page_nro = 1
        pages = 1
        if role == 1:
            # [0 id, 1 course_name, 2 course_open]
            course_list = courses.search_my_course_by_name_teacher(course_name, user_id)
        elif role == 0:
            # [0 id, 1 course_name, 2 course_open, 3 teacher_name]
            course_list = courses.search_my_course_by_name_student(course_name, user_id)

    return render_template(
        "my_courses.html",
        course_list=course_list,
        course_count=course_count,
        page_nro=page_nro,
        pages=pages,
        search_by_name=search_by_name,
        searched_name=searched_name,
    )


# Allows students to enroll in courses.
@app.route("/enroll/<int:course_id>", methods=["GET", "POST"])
def enroll(course_id):
    users.required_role([0])
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    info = courses.course_info(course_id)
    open = info[3]
    users.check_csrf()
    if open == 1:
        user_id = users.user_id()
        if courses.is_enrolled(course_id, user_id):
            render_template("error.html", message="Olet jo liittynyt kurssille")
        if courses.enroll(course_id, user_id):
            return redirect("/courses/" + str(course_id))
    return render_template("error.html", message="Kurssille liittyminen epäonnistui")


# Changes the state of a course. First state is before the course has been started,
# second state is when the course is ongoing and the last state is when the course has
# been concluded. Changing the state cannot be reversed.
@app.route("/update_course", methods=["POST"])
def update_course():
    users.required_role([1])
    course_id = request.form["course_id"]
    courses.course_info(course_id)
    user_id = users.user_id()
    users.check_csrf()
    if courses.course_owner(course_id, user_id):
        if courses.update_course(course_id):
            return redirect("/courses/" + str(course_id))
        return render_template(
            "error.html", message="Kurssin tilan päivitys epäonnistui"
        )
    abort(403)


# Adds an exercise without answer choices.
@app.route("/add_exercise_one/<int:course_id>", methods=["GET", "POST"])
def add_exercise_one(course_id):
    user_id = users.user_id()
    if not courses.course_owner(course_id, user_id):
        abort(403)
    error_name = None
    error_name_reserved = None
    error_question = None
    error_answer = None

    if request.method == "GET":
        return render_template(
            "add_exercise_one.html",
            course_id=course_id,
            error_name=error_name,
            error_name_reserved=error_name_reserved,
            error_question=error_question,
            error_answer=error_answer,
            display_name="",
            display_question="",
            display_answer="",
        )

    if request.method == "POST":
        users.check_csrf()
        name = request.form["name"]
        question = request.form["question"]
        answer = request.form["answer"]
        error = False

        if exercises.exercise_name_reserved(course_id, name):
            error_name_reserved = "Nimi on varattu"
            error = True

        if name == "":
            error_name = "Lisää tehtävälle nimi"
            error = True
        if question == "":
            error_question = "Lisää tehtävälle kysymys"
            error = True
        if answer == "":
            error_answer = "Lisää tehtävälle vastaus"
            error = True
        if error:
            display_name = name
            display_question = question
            display_answer = answer
            return render_template(
                "add_exercise_one.html",
                course_id=course_id,
                error_name=error_name,
                error_name_reserved=error_name_reserved,
                error_question=error_question,
                error_answer=error_answer,
                display_name=display_name,
                display_question=display_question,
                display_answer=display_answer,
            )

        if exercises.add_exercise(course_id, name, "one", question, answer):
            return redirect("/courses/" + str(course_id))
        return render_template(
            "error.html", message="Kysymyksen lisääminen epäonnistui"
        )


# Adds an multiple choice question.
@app.route("/add_exercise_multiple/<int:course_id>", methods=["GET", "POST"])
def add_exercise_multiple(course_id):
    user_id = users.user_id()
    if not courses.course_owner(course_id, user_id):
        abort(403)

    if request.method == "GET":
        return render_template(
            "add_exercise_multiple.html",
            course_id=course_id,
            nro_choices=1,
            choices=[],
            exercise_name="",
            question="",
            correct_answer="",
        )

    if request.method == "POST":
        users.check_csrf()
        error_name = None
        error_question = None
        error_answer = None
        error_choices = None
        submit = request.form["submit"]
        exercise_name = request.form["exercise_name"]
        question = request.form["question"]
        correct_answer = request.form["correct_answer"]
        nro_choices = int(request.form["nro_choices"])
        choices = []
        for c in range(1, nro_choices + 1):
            name = "choice" + str(c)
            input = request.form[name]
            if input != "":
                choices.append(input)

        if submit == "Luo tehtävä":
            if exercise_name == "":
                error_name = "Lisää tehtävälle nimi"
                submit = "Lisää vaihtoehto"
            if question == "":
                error_question = "Lisää tehtävälle kysymys"
                submit = "Lisää vaihtoehto"
            if correct_answer == "":
                error_answer = "Lisää tehtävälle oikea vastaus"
                submit = "Lisää vaihtoehto"
            if len(choices) == 0:
                error_choices = "Lisää ainakin yksi vaihtoehto"
                submit = "Lisää vaihtoehto"

        if submit == "Lisää vaihtoehto":
            nro_choices = len(choices) + 1
            choices.append("")
            return render_template(
                "add_exercise_multiple.html",
                course_id=course_id,
                nro_choices=nro_choices,
                choices=choices,
                exercise_name=exercise_name,
                question=question,
                correct_answer=correct_answer,
                error_name=error_name,
                error_question=error_question,
                error_answer=error_answer,
                error_choices=error_choices,
            )

        if submit == "Luo tehtävä":
            if exercises.exercise_name_reserved(course_id, exercise_name):
                return render_template(
                    "error.html", message="Harjoituksen nimi on jo varattu"
                )

            if not exercises.add_exercise(
                course_id, exercise_name, "multiple", question, correct_answer
            ):
                return render_template(
                    "error.html", message="Harjoituksen luominen epäonnistui"
                )
            exercise_id = exercises.exercise_id(course_id, exercise_name)

            if not exercises.add_choices(exercise_id, choices):
                return render_template(
                    "error.html", message="Vaihtoehtojen lisääminen epäonnistui"
                )

            return redirect("/courses/" + str(course_id))


@app.route("/courses/<int:course_id>/<int:exercise_id>", methods=["GET"])
def exercise_page(course_id, exercise_id):
    users.required_role([0, 1])
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    course_info = courses.course_info(course_id)
    course_open = course_info[3]
    user_id = users.user_id()
    # [0 id, 1 course_id, 2 name, 3 type, 4 question, 5 answer]
    exercise_info = exercises.exercise_info(exercise_id)
    course_name = course_info[1]
    if exercise_info[3] == "multiple":
        choices = exercises.exercise_choices(exercise_id)
    else:
        choices = None

    if courses.course_owner(course_id, user_id):
        return render_template(
            "exercise_page_t.html",
            exercise_info=exercise_info,
            course_name=course_name,
            course_id=course_id,
            course_open=course_open,
            choices=choices,
        )

    if courses.is_enrolled(course_id, user_id):
        open = course_info[3]
        # Change tuple into list
        exercise_info = list(exercise_info)
        # exercise_id = exercise_info[0]

        if exercise_info[3] == "one":
            # Don't send the answer to students
            # [0 id, 1 course_id, 2 name, 3 type, 4 question]
            exercise_info.pop()
            last_submission = exercises.last_submission(user_id, exercise_id)
            solved = exercises.exercise_solved(user_id, exercise_id)
            return render_template(
                "exercise_page_s.html",
                exercise_info=exercise_info,
                course_name=course_name,
                course_id=course_id,
                last_submission=last_submission,
                open=open,
                solved=solved,
            )

        if exercise_info[3] == "multiple":
            choices.append([exercise_info[5]])
            random.shuffle(choices)
            # Don't send the answer to students
            # [0 id, 1 course_id, 2 name, 3 type, 4 question]
            exercise_info.pop()
            answered = exercises.question_answered(user_id, exercise_id)
            solved = exercises.exercise_solved(user_id, exercise_id)
            last_submission = exercises.last_submission(user_id, exercise_id)
            return render_template(
                "exercise_page_s.html",
                exercise_info=exercise_info,
                course_name=course_name,
                course_id=course_id,
                answered=answered,
                last_submission=last_submission,
                open=open,
                solved=solved,
                choices=choices,
            )
    return "Vain kurssille liittyneet voivat nähdä kysymykset"


# Checks the answer sent by a student to a question without choices.
@app.route("/answer_one", methods=["POST"])
def answer_one():
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    exercise_id = request.form["exercise_id"]
    user_id = users.user_id()
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    course_info = courses.course_info(course_id)
    open = course_info[3]
    if open != 1:
        return render_template(
            "error.html",
            message="Kurssi ei ole auki. Tehtävien palauttaminen ei ole mahdollista.",
        )
    if courses.is_enrolled(course_id, user_id):
        users.check_csrf()
        if exercises.submit(exercise_id, user_id, answer):
            return redirect(
                f"/courses/{course_id}/{exercise_id}",
            )
        return render_template("error.html", message="Palautus epäonnistui")
    abort(403)


# Checks the answer to a multiple choice question sent by a stude.
@app.route("/answer_multiple", methods=["POST"])
def answer_multiple():
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    exercise_id = request.form["exercise_id"]
    user_id = users.user_id()
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    course_info = courses.course_info(course_id)
    open = course_info[3]
    if open != 1:
        return render_template(
            "error.html",
            message="Kurssi ei ole auki. Tehtävien palauttaminen ei ole mahdollista.",
        )
    if exercises.question_answered(user_id, exercise_id):
        return render_template(
            "error.html",
            message="Olet jo vastannut. Uudelleen vastaaminen ei ole mahdolista",
        )
    if courses.is_enrolled(course_id, user_id):
        users.check_csrf()
        if exercises.submit(exercise_id, user_id, answer):
            return redirect(
                f"/courses/{course_id}/{exercise_id}",
            )
        return render_template("error.html", message="Palautus epäonnistui")
    abort(403)


@app.route("/courses/<int:course_id>/students", methods=["GET"])
def students(course_id):
    user_id = users.user_id()
    if courses.course_owner(course_id, user_id):
        students = courses.students(course_id)
        nro_students = len(students)
        return render_template(
            "students.html",
            students=students,
            nro_students=nro_students,
            course_id=course_id,
        )


@app.route("/courses/<int:course_id>/students/<int:student_id>", methods=["GET"])
def student_statistics(course_id, student_id):
    user_id = users.user_id()
    if courses.course_owner(course_id, user_id):
        exercise_list = exercises.course_exercises(course_id)
        nro_exercises = len(exercise_list)
        completed_exercises = exercises.completed_exercises(student_id, course_id)
        nro_completed = len(completed_exercises)
        student_name = users.username(student_id)
        return render_template(
            "student_statistics.html",
            student_name=student_name,
            student_id=student_id,
            exercise_list=exercise_list,
            nro_exercises=nro_exercises,
            completed_exercises=completed_exercises,
            nro_completed=nro_completed,
            course_id=course_id,
        )


@app.route(
    "/courses/<int:course_id>/students/<int:student_id>/submissions/<int:exercise_id>",
    methods=["GET"],
)
def submissions(course_id, student_id, exercise_id):
    user_id = users.user_id()

    if courses.course_owner(course_id, user_id):
        # (0 id, 1 answer, 2 correct, 3 time)
        submissions = exercises.submissions_by_student(student_id, exercise_id)
        return render_template(
            "submissions.html",
            submissions=submissions,
            course_id=course_id,
            exercise_id=exercise_id,
            student_id=student_id,
        )

    if courses.is_enrolled(course_id, user_id):
        # (0 id, 1 answer, 2 correct, 3 time)
        submissions = exercises.submissions_by_student(user_id, exercise_id)

        return render_template(
            "submissions.html",
            submissions=submissions,
            course_id=course_id,
            exercise_id=exercise_id,
            student_id=None,
        )


@app.route("/delete_exercise", methods=["POST"])
def delete_exercise():
    exercise_id = request.form["exercise_id"]
    course_id = request.form["course_id"]
    user_id = users.user_id()
    # (0 id, 1 name, 2 teacher_id, 3 course_open, 4 visible, 5 description)
    open = courses.course_info(course_id)[3]
    if open != 0:
        return render_template(
            "error.html", message="Tehtäviä ei voi poistaa kurssi aloittamisen jälkeen"
        )
    if not courses.course_owner(course_id, user_id):
        abort(403)
    users.check_csrf()
    if exercises.delete_exercise(exercise_id):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Harjoituksen poisto epäonnistui")
