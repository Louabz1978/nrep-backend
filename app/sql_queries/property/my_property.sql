SELECT
    p.property_id,
    p.description,
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
    p.created_at,
    p.last_updated,
    p.images_urls,
    p.mls_num,
    
    -- Owner user fields prefixed with owner_
    owner.user_id AS owner_user_id,
    owner.first_name AS owner_first_name,
    owner.last_name AS owner_last_name,
    owner.email AS owner_email,
    owner.phone_number AS owner_phone_number,
    owner.created_by AS owner_created_by,
    owner.created_at AS owner_created_at,
    
    -- Owner roles prefixed
    owner_roles.admin AS owner_admin,
    owner_roles.broker AS owner_broker,
    owner_roles.realtor AS owner_realtor,
    owner_roles.buyer AS owner_buyer,
    owner_roles.seller AS owner_seller,
    owner_roles.tenant AS owner_tenant,
    
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
    a.street AS address_street

FROM properties p

LEFT JOIN users owner ON p.owner_id = owner.user_id
LEFT JOIN roles owner_roles ON owner.role_id = owner_roles.roles_id

LEFT JOIN users creator ON p.created_by = creator.user_id
LEFT JOIN roles creator_roles ON creator.role_id = creator_roles.roles_id

LEFT JOIN addresses a ON p.address_id = a.address_id

WHERE p.created_by = :created_by;
