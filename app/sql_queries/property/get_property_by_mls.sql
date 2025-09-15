SELECT
    p.property_id,
    p.description,
    p.show_inst,
    p.price,
    p.property_type,
    p.bedrooms,
    p.bathrooms,
    p.property_realtor_commission,
    p.buyer_realtor_commission,
    p.area_space,
    p.year_built,
    p.latitude,
    p.longitude,
    p.status,
    p.trans_type,
    p.exp_date,
    p.created_at,
    p.last_updated,
    p.images_urls,
    p.mls_num,
    p.livable,
    
    -- Created by user fields prefixed with created_by_
    creator.user_id AS created_by_user_id,
    creator.first_name AS created_by_first_name,
    creator.last_name AS created_by_last_name,
    creator.email AS created_by_email,
    creator.phone_number AS created_by_phone_number,
    creator.created_by AS created_by_created_by,
    creator.created_at AS created_by_created_at,
    
    -- Created by roles prefixed
    creator_roles.admin AS created_by_admin,
    creator_roles.broker AS created_by_broker,
    creator_roles.realtor AS created_by_realtor,
    creator_roles.buyer AS created_by_buyer,
    creator_roles.seller AS created_by_seller,
    creator_roles.tenant AS created_by_tenant,
    
    -- Address fields
    a.address_id AS address_address_id,
    a.floor AS address_floor,
    a.apt AS address_apt,
    a.area AS address_area,
    a.city AS address_city,
    a.county AS address_county,
    a.created_at AS address_created_at,
    a.created_by AS address_created_by,
    a.building_num AS address_building_num,
    a.street AS address_street,

    -- Additional fields
    ad.additional_id,
    ad.elevator,
    ad.balcony,
    ad.ac,
    ad.fan_number, 
    ad.garage, 
    ad.garden, 
    ad.solar_system, 
    ad.water, 
    ad.jacuzzi,
    ad.pool
    
FROM properties p

LEFT JOIN users creator ON p.created_by = creator.user_id
LEFT JOIN roles creator_roles ON creator.user_id = creator_roles.user_id

LEFT JOIN addresses a ON p.property_id = a.property_id
LEFT JOIN additional ad ON p.property_id = ad.property_id

WHERE p.mls_num = :mls;
