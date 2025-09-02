SELECT
    co.county_id,
    co.title AS county_title,
    co.created_at AS county_created_at,
    co.updated_at AS county_updated_at,
    co.created_by AS county_created_by,
    co.updated_by AS county_updated_by,

    a.area_id,
    a.title AS area_title,
    a.created_at AS area_created_at,
    a.updated_at AS area_updated_at,
    a.created_by AS area_created_by,
    a.updated_by AS area_updated_by

FROM counties co
LEFT JOIN areas a ON co.county_id = a.county_id
ORDER BY co.county_id, a.area_id;
