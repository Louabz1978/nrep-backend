INSERT INTO
    areas (title, county_id, created_by)
VALUES
    (:title, :county_id, :created_by)
RETURNING *;
