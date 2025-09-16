SELECT
    co.county_id,
    co.title AS county_title,
    co.created_at AS county_created_at,
    co.updated_at AS county_updated_at,
    co.created_by AS county_created_by,
    co.updated_by AS county_updated_by

FROM counties co
ORDER BY co.county_id;
