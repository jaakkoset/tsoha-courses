CREATE TABLE Users
(
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    role INTEGER
);
-- role is 0 for students and 1 for teachers