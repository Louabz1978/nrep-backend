SELECT 
    a.agency_id,
    a.name,
    a.email,
    a.phone_number,
    a.created_at,

    addr.address_id AS address_address_id,
    addr.floor AS address_floor,
    addr.apt AS address_apt,
    addr.area AS address_area,
    addr.city AS address_city,
    addr.county AS address_county,
    addr.building_num AS address_building_num,
    addr.street AS address_street,
    addr.created_at AS address_created_at,

    u.user_id AS created_by_user_id,
    u.first_name AS created_by_first_name,
    u.last_name AS created_by_last_name,
    u.email AS created_by_email,
    u.phone_number AS created_by_phone_number,

    b.user_id AS broker_user_id,
    b.first_name AS broker_first_name,
    b.last_name AS broker_last_name,
    b.email AS broker_email,
    b.phone_number AS broker_phone_number,
    b.created_by AS broker_created_by,
    b.created_at AS broker_created_at

FROM agencies a

LEFT JOIN users u ON u.user_id = a.created_by
LEFT JOIN users b ON a.broker_id = b.user_id
LEFT JOIN addresses addr ON a.agency_id = addr.agency_id

WHERE a.agency_id = :agency_id;
