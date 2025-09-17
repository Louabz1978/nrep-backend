INSERT INTO
    counties (title, created_by)
VALUES
    (:title, :created_by)
RETURNING *;
