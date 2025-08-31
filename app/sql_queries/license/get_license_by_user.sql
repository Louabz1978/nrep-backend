SELECT 
    l.license_id,
    l.lic_num,
    l.lic_status,
    l.lic_type,
    l.user_id,

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
    l.user_id = :user_id
