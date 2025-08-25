SELECT 
    a.agency_id AS agency_agency_id,
    a.name AS agency_name,
    a.email AS agency_email,
    a.phone_number AS agency_phone_number,
    a.created_at AS agency_created_at,
    a.created_by AS agency_created_by,
    u.user_id AS broker_user_id,
    u.first_name AS broker_first_name,
    u.last_name AS broker_last_name,
    u.email AS broker_email,
    u.phone_number AS broker_phone_number,
    u.created_by AS broker_created_by,
    u.created_at AS broker_created_at,
    r.admin AS roles_admin, 
    r.broker AS roles_broker, 
    r.realtor AS roles_realtor,
    r.buyer AS roles_buyer,
    r.seller AS roles_seller,
    r.tenant AS roles_tenant ,
    ad.address_id AS address_address_id,
    ad.floor AS address_floor,
    ad.apt AS address_apt,
    ad.area AS address_area,
    ad.city AS address_city,
    ad.county AS address_county,
    ad.building_num AS address_building_num,
    ad.street AS address_street,
    ad.created_at AS address_created_at
FROM agencies a
LEFT JOIN users u ON a.broker_id = u.user_id
LEFT JOIN roles r ON u.user_id = r.user_id
LEFT JOIN addresses ad ON a.address_id = ad.address_id
WHERE agency_id=:agency_id

