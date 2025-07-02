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
    u2.user_id AS agent_user_id,
    u2.first_name AS agent_first_name,
    u2.last_name AS agent_last_name,
    u2.email AS agent_email,
    u2.phone_number AS agent_phone_number,
    u2.address AS agent_address,
    u2.neighborhood AS agent_neighborhood,
    u2.city AS agent_city,
    u2.county AS agent_county,
    u2.lic_num AS agent_lic_num,
    u2.role AS agent_role,
    u2.is_active AS agent_is_active,
    a2.agency_id AS agent_agency_id,
    a2.name AS agent_agency_name,
    a2.phone_number AS agent_agency_phone_number

FROM properties p
LEFT JOIN users u1 ON p.owner_id = u1.user_id
LEFT JOIN agencies a1 ON u1.agency_id = a1.agency_id

LEFT JOIN users u2 ON p.agent_id = u2.user_id
LEFT JOIN agencies a2 ON u2.agency_id = a2.agency_id

WHERE p.property_id = :listing_id;
