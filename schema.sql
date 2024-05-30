-- role is 0 for students and 1 for teachers.
CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    role INTEGER
);

-- This table contains all courses. Courses can only be made by teachers.
-- started is 1 after the course has begun and 0 before that.
-- After a course has been started the teacher cannot modify the questions.
-- course_open is 1 when the course is open and 0 when the course is closed.
-- When the course is closed enrollment is not possible and exercises cannot be made.
-- visible is 1 normally and 0 when the course is deleted.
CREATE TABLE courses
(
    id SERIAL PRIMARY KEY,
    name TEXT,
    teacher_id INTEGER REFERENCES users,
    started INTEGER,
    course_open INTEGER,
    visible INTEGER
);

-- Contains all exercises. Each exercise is associated with one course.
-- type is "multiple" for multiple choice questions and "one" for questions without choices.
-- choices is Null for other than multiple choice questions.
CREATE TABLE exercises
(
    id SERIAL PRIMARY KEY,
    name TEXT,
    course_id INTEGER REFERENCES courses,
    type TEXT,
    question TEXT,
    answer TEXT,
    choices TEXT
);

-- Contains all submissions on all courses by a student.
-- correct is 0 for wrong answers and 1 for right answers.
CREATE TABLE submissions
(
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER REFERENCES exercises,
    answer TEXT,
    correct INTEGER,
    time TIMESTAMP
);