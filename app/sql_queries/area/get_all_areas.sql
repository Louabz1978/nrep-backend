SELECT
    a.area_id,
    a.title,
    a.county_id,
    a.created_at,
    a.updated_at,
    a.created_by,
    a.updated_by
FROM areas a
WHERE (:title IS NULL OR title ILIKE :title)
ORDER BY a.{sort_by} {sort_order}
LIMIT :limit OFFSET :offset;
