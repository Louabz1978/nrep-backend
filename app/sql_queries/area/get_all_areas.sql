SELECT
    a.area_id,
    a.title,
    a.county_id,
    a.created_at,
    a.updated_at,
    a.created_by,
    a.updated_by
FROM areas a
ORDER BY a.area_id;
