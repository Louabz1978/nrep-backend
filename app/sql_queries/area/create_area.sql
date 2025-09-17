INSERT INTO
    areas (title, city_id, created_by)
VALUES
    (:title, :city_id, :created_by)
RETURNING *;
