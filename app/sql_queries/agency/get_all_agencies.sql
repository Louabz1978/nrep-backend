SELECT
    a.agency_id,
    a.name AS agency_name,
    a.phone_number AS agency_phone_number,
    a.email AS agency_email,
    a.created_at AS agency_created_at,
    a.created_by AS agency_created_by,
    a.broker_id,

    addr.address_id,
    addr.floor,
    addr.apt,
    addr.area,
    addr.city,
    addr.county,
    addr.created_at AS address_created_at,
    addr.created_by AS address_created_by,
    addr.building_num,
    addr.street,

    u.user_id AS created_by_user_id,
    u.first_name AS created_by_first_name,
    u.last_name AS created_by_last_name,
    u.email AS created_by_email,
    u.phone_number AS created_by_phone_number,
    u.created_by AS created_by_created_by,
    u.created_at AS created_by_created_at,

    rcb.admin AS created_by_admin,
    rcb.broker AS created_by_broker,
    rcb.realtor AS created_by_realtor,
    rcb.buyer AS created_by_buyer,
    rcb.seller AS created_by_seller,
    rcb.tenant AS created_by_tenant,

    b.user_id AS broker_id,
    b.first_name AS broker_first_name,
    b.last_name AS broker_last_name,
    b.email AS broker_email,
    b.phone_number AS broker_phone_number,
    b.created_by AS broker_created_by,
    b.created_at AS broker_created_at,

    rb.admin AS broker_admin,
    rb.broker AS broker_broker,
    rb.realtor AS broker_realtor,
    rb.buyer AS broker_buyer,
    rb.seller AS broker_seller,
    rb.tenant AS broker_tenant

FROM agencies a
LEFT JOIN addresses addr ON addr.agency_id = a.agency_id
LEFT JOIN users u ON u.user_id = a.created_by
LEFT JOIN roles rcb ON u.user_id = rcb.user_id
LEFT JOIN users b ON a.broker_id = b.user_id
LEFT JOIN roles rb ON b.user_id = rb.user_id
WHERE
    (:name IS NULL OR a.name ILIKE :name)
    AND (:email IS NULL OR a.email ILIKE :email)
    AND (:phone_number IS NULL OR a.phone_number ILIKE :phone_number)
    AND (:broker_id IS NULL OR a.broker_id = :broker_id)
    AND (:created_by IS NULL OR a.created_by = :created_by)
    AND (:city IS NULL OR addr.city ILIKE :city)
ORDER BY {sort_by} {sort_order}
LIMIT :limit OFFSET :offset;