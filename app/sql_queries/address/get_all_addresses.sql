SELECT 
    a.address_id,
    a.floor,
    a.apt,
    a.area,
    a.city,
    a.county,
    a.created_at,
    a.building_num,
    a.street,
    
    u.user_id AS created_by_user_user_id,
    u.first_name AS created_by_user_first_name,
    u.last_name AS created_by_user_last_name,
    u.email AS created_by_user_email,
    u.phone_number AS created_by_user_phone_number,
    u.created_at AS created_by_user_created_at,
    u.created_by AS created_by_user_created_by,
    r.admin AS created_by_user_admin,
    r.broker AS created_by_user_broker,
    r.realtor AS created_by_user_realtor,
    r.buyer AS created_by_user_buyer,
    r.seller AS created_by_user_seller,
    r.tenant AS created_by_user_tenant

FROM addresses a
LEFT JOIN users u ON a.created_by = u.user_id
Left join roles r On u.role_id=r.roles_id;
