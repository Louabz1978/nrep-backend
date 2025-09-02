INSERT INTO
    cities (title, created_by)
VALUES
    (:title, :created_by)
RETURNING *;
