    SELECT 
        p.*,

        seller.user_id AS seller_user_id,
        seller.first_name AS seller_first_name,
        seller.last_name AS seller_last_name,
        seller.email AS seller_email,
        seller.phone_number AS seller_phone_number,
        seller.address AS seller_address,
        seller.neighborhood AS seller_neighborhood,
        seller.city AS seller_city,
        seller.county AS seller_county,
        seller.lic_num AS seller_lic_num,
        seller.role AS seller_role,
        seller.is_active AS seller_is_active,
        user_agency.agency_id AS seller_agency_id,
        user_agency.name AS seller_agency_name,
        user_agency.phone_number AS seller_agency_phone_number,

        realtor.user_id AS realtor_user_id,
        realtor.first_name AS realtor_first_name,
        realtor.last_name AS realtor_last_name,
        realtor.email AS realtor_email,
        realtor.phone_number AS realtor_phone_number,
        realtor.address AS realtor_address,
        realtor.neighborhood AS realtor_neighborhood,
        realtor.city AS realtor_city,
        realtor.county AS realtor_county,
        realtor.lic_num AS realtor_lic_num,
        realtor.role AS realtor_role,
        realtor.is_active AS realtor_is_active,
        realtor_agencies.agency_id AS realtor_agency_id,
        realtor_agencies.name AS realtor_agency_name,
        realtor_agencies.phone_number AS realtor_agency_phone_number

    FROM properties p
    LEFT JOIN users seller ON p.seller_id = seller.user_id
    LEFT JOIN agencies user_agency ON seller.agency_id = user_agency.agency_id

    LEFT JOIN users realtor ON p.realtor_id = realtor.user_id
    LEFT JOIN agencies realtor_agencies ON realtor.agency_id = realtor_agencies.agency_id