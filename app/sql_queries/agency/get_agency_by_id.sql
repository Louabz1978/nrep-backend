SELECT
    a.agency_id,
    a.name, 
    a.email,
    a.phone_number,
    a.created_at,
    a.created_by,
    a.broker_id,

  --broker fields
    broker.user_id AS broker_user_id,
    broker.first_name AS broker_first_name,
    broker.last_name AS broker_last_name,
    broker.email AS broker_email,
    broker.phone_number AS broker_phone_number,
    broker.created_at AS broker_created_at,
    broker.created_by AS broker_created_by,

  --broker roles
    broker_roles.admin AS broker_admin,
    broker_roles.broker AS broker_broker,
    broker_roles.realtor AS broker_realtor,

  --Adress fields
    ad.address_id AS address_address_id,
    ad.floor AS address_floor,
    ad.apt AS address_apt,
    ad.area AS address_area,
    ad.city AS address_city,
    ad.county AS address_county,
    ad.created_at AS address_created_at,
    ad.created_by AS address_created_by,
    ad.building_num AS address_building_num,
    ad.street AS address_street

FROM agencies a
LEFT JOIN users broker ON a.broker_id = broker.user_id
LEFT JOIN roles broker_roles ON broker.user_id = broker_roles.user_id
LEFT JOIN addresses ad ON a.agency_id = ad.agency_id

WHERE a.agency_id = :agency_id;
