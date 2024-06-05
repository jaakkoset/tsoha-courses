-- role is 0 for students and 1 for teachers.
CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

-- This table contains all courses. Courses can only be made by teachers.
-- course_open is 0 before the course has been started. During this time teachers 
-- can modify questions. course_open is 1 when course is open and ongoing. During 
-- this time stundets can enroll in the courses, but teachers cannot anymore modify 
-- questions. course_open is 2 when the course is over. Enrollment and modifications 
-- are not possible anymore, but statistics can be viewed.
-- visible is 1 normally and 0 when the course is deleted.
CREATE TABLE courses
(
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    teacher_id INTEGER REFERENCES users,
    course_open INTEGER,
    visible INTEGER,
    description TEXT
);

-- This table tells the courses each student has enrolled.
CREATE TABLE enrollment
(
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    student_id INTEGER REFERENCES users
);

-- Contains all exercises. Each exercise is associated with one course.
-- type is "multiple" for multiple choice questions and "one" for questions without choices.
-- choices is Null for other than multiple choice questions.
CREATE TABLE exercises
(
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    name TEXT,
    type TEXT,
    question TEXT,
    answer TEXT,
    choices TEXT
);

-- Contains exercise submissions by students.
-- correct is 0 for wrong answers and 1 for right answers.
CREATE TABLE submissions
(
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users,
    exercise_id INTEGER REFERENCES exercises,
    answer TEXT,
    correct INTEGER,
    time TIMESTAMP
);