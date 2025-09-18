WITH limited_cities AS (
    SELECT *
    FROM cities
    ORDER BY city_id
    LIMIT :limit OFFSET :offset
)
SELECT
    c.city_id,
    c.title AS city_title,
    c.created_at AS city_created_at,
    c.updated_at AS city_updated_at,
    c.created_by AS city_created_by,
    c.updated_by AS city_updated_by


FROM limited_cities c
LEFT JOIN counties co ON c.city_id = co.city_id
LEFT JOIN areas a ON co.county_id = a.county_id
ORDER BY c.city_id, co.county_id, a.area_id;

