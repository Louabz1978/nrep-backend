SELECT 
    p.*,

    -- Owner fields
    u1.user_id AS owner_user_id,
    u1.first_name AS owner_first_name,
    u1.last_name AS owner_last_name,
    u1.email AS owner_email,
    u1.phone_number AS owner_phone_number,
    u1.address AS owner_address,
    u1.neighborhood AS owner_neighborhood,
    u1.city AS owner_city,
    u1.county AS owner_county,
    u1.lic_num AS owner_lic_num,
    u1.role AS owner_role,
    u1.is_active AS owner_is_active,
    a1.agency_id AS owner_agency_id,
    a1.name AS owner_agency_name,
    a1.phone_number AS owner_agency_phone_number,

    -- Agent fields
    u2.user_id AS realtor_user_id,
    u2.first_name AS realtor_first_name,
    u2.last_name AS realtor_last_name,
    u2.email AS realtor_email,
    u2.phone_number AS realtor_phone_number,
    u2.address AS realtor_address,
    u2.neighborhood AS realtor_neighborhood,
    u2.city AS realtor_city,
    u2.county AS realtor_county,
    u2.lic_num AS realtor_lic_num,
    u2.role AS realtor_role,
    u2.is_active AS realtor_is_active,
    a2.agency_id AS realtor_agency_id,
    a2.name AS realtor_agency_name,
    a2.phone_number AS realtor_agency_phone_number

FROM properties p
LEFT JOIN users u1 ON p.seller_id = u1.user_id
LEFT JOIN agencies a1 ON u1.agency_id = a1.agency_id

LEFT JOIN users u2 ON p.realtor_id = u2.user_id
LEFT JOIN agencies a2 ON u2.agency_id = a2.agency_id

WHERE p.property_id = :property_id;
