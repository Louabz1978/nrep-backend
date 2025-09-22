WITH limited_cities AS (
    SELECT *
    FROM cities
    WHERE (:title IS NULL OR title ILIKE :title)
    ORDER BY {sort_by} {sort_order}
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
ORDER BY c.{sort_by} {sort_order}, co.county_id, a.area_id ;

