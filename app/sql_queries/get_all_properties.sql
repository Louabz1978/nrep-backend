    SELECT 
        p.*,

        owner.user_id AS owner_user_id,
        owner.first_name AS owner_first_name,
        owner.last_name AS owner_last_name,
        owner.email AS owner_email,
        owner.phone_number AS owner_phone_number,
        owner.address AS owner_address,
        owner.neighborhood AS owner_neighborhood,
        owner.city AS owner_city,
        owner.county AS owner_county,
        owner.lic_num AS owner_lic_num,
        owner.role AS owner_role,
        owner.is_active AS owner_is_active,
        user_agency.agency_id AS owner_agency_id,
        user_agency.name AS owner_agency_name,
        user_agency.phone_number AS owner_agency_phone_number,

        agent.user_id AS realtor_user_id,
        agent.first_name AS realtor_first_name,
        agent.last_name AS realtor_last_name,
        agent.email AS realtor_email,
        agent.phone_number AS realtor_phone_number,
        agent.address AS realtor_address,
        agent.neighborhood AS realtor_neighborhood,
        agent.city AS realtor_city,
        agent.county AS realtor_county,
        agent.lic_num AS realtor_lic_num,
        agent.role AS realtor_role,
        agent.is_active AS realtor_is_active,
        agent_agencies.agency_id AS realtor_agency_id,
        agent_agencies.name AS realtor_agency_name,
        agent_agencies.phone_number AS realtor_agency_phone_number

    FROM properties p
    LEFT JOIN users owner ON p.seller_id = owner.user_id
    LEFT JOIN agencies user_agency ON owner.agency_id = user_agency.agency_id

    LEFT JOIN users agent ON p.realtor_id = agent.user_id
    LEFT JOIN agencies agent_agencies ON agent.agency_id = agent_agencies.agency_id