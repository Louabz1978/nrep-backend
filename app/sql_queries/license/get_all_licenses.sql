SELECT 
    l.license_id,
    l.lic_num,
    l.lic_status,
    l.lic_type,
    l.user_id,
    -- l.agency_id,

    u.user_id AS broker_user_id,
    u.first_name AS broker_first_name,
    u.last_name AS broker_last_name,
    u.email AS broker_email,
    u.phone_number AS broker_phone_number,

    a.agency_id As agency_agency_id,
    a.name As agency_name,
    a.email As agency_email,
    a.phone_number As agency_phone_number,
    a.created_at As agency_created_at

FROM licenses l

LEFT JOIN users u ON l.user_id = u.user_id
LEFT JOIN agencies a ON l.agency_id = a.agency_id

WHERE 
-- (
--     :role = 'admin'
--     OR (:role = 'broker' AND l.agency_id = (
--         SELECT agency_id FROM users WHERE user_id = :user_id
--     ))
--     OR (:role = 'realtor' AND l.user_id = :user_id)
-- )
(:lic_status IS NULL OR l.lic_status = :lic_status)
AND (:lic_type IS NULL OR l.lic_type = :lic_type)
AND (:agency_id IS NULL OR l.agency_id = :agency_id)
AND (:filter_user_id IS NULL OR l.user_id = :filter_user_id)

ORDER BY {sort_by} {sort_order}
LIMIT :limit OFFSET :offset;
