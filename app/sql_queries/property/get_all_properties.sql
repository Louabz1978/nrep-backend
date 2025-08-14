SELECT
    -- Property fields
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
    p.exp_date,
    p.created_at,
    p.last_updated,
    p.images_urls,
    p.mls_num,

    -- Created by user fields
    cb.user_id AS created_by_user_id,
    cb.first_name AS created_by_first_name,
    cb.last_name AS created_by_last_name,
    cb.email AS created_by_email,
    cb.phone_number AS created_by_phone_number,
    cb.created_at AS created_by_created_at,
    cb.created_by AS created_by_created_by,

    rcb.admin AS created_by_admin,
    rcb.broker AS created_by_broker,
    rcb.realtor AS created_by_realtor,
    rcb.buyer AS created_by_buyer,
    rcb.seller AS created_by_seller,
    rcb.tenant AS created_by_tenant,

    -- Owner (property seller) fields
    o.consumer_id AS owner_consumer_id,
    o.name AS owner_name,
    o.father_name AS owner_father_name,
    o.surname AS owner_surname,
    o.mother_name_surname AS owner_mother_name_surname,
    o.place_birth AS owner_place_birth,
    o.date_birth AS owner_date_birth,
    o.registry AS owner_registry,
    o.national_number AS owner_national_number,
    o.email AS owner_email,
    o.phone_number AS owner_phone_number,
    o.created_by AS owner_created_by,
    o.created_at AS owner_created_at,

    -- Address fields
    a.address_id,
    a.floor,
    a.apt,
    a.area,
    a.city,
    a.county,
    a.created_by AS address_created_by,
    a.created_at AS address_created_at,
    a.building_num,
    a.street,

    -- Additional fields
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
LEFT JOIN users cb ON p.created_by = cb.user_id
LEFT JOIN roles rcb ON cb.user_id = rcb.user_id

LEFT JOIN consumers o ON p.owner_id = o.consumer_id

LEFT JOIN addresses a ON p.property_id = a.property_id
LEFT JOIN additional ad ON p.property_id = ad.property_id

WHERE p.created_by = :created_by
    AND p.exp_date >= CURRENT_DATE
    AND (:city IS NULL OR a.city ILIKE :city)
    AND (:area IS NULL OR a.area ILIKE :area)
    AND (:min_price IS NULL OR p.price >= :min_price)
    AND (:max_price IS NULL OR p.price <= :max_price)
    AND (:mls_num IS NULL OR p.mls_num = :mls_num)
    AND (:status IS NULL OR p.status = :status)

ORDER BY {sort_by} {sort_order}
LIMIT :limit OFFSET :offset;
