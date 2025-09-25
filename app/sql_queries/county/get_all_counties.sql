WITH limited_counties AS (
    SELECT *
    FROM counties
    WHERE (:title IS NULL OR title ILIKE :title)
    ORDER by {sort_by} {sort_order}
    LIMIT :limit OFFSET :offset
)
SELECT
    co.county_id,
    co.title AS county_title,
    co.created_at AS county_created_at,
    co.updated_at AS county_updated_at,
    co.created_by AS county_created_by,
    co.updated_by AS county_updated_by

FROM limited_counties co
ORDER BY co.{sort_by} {sort_order};

