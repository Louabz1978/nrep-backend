SELECT
    c.city_id,
    c.title AS city_title,
    c.created_at AS city_created_at,
    c.updated_at AS city_updated_at,
    c.created_by AS city_created_by,
    c.updated_by AS city_updated_by

FROM cities c
ORDER BY c.city_id;
