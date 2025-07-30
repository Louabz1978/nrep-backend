SELECT
  u.*,
  d.address_id,
  d.floor,
  d.apt,
  d.area,
  d.city,
  d.county,
  d.building_num,
  d.street,
  d.created_at AS address_created_at,
  r.admin, r.broker, r.realtor, r.buyer, r.seller, r.tenant
FROM users u
LEFT JOIN roles r ON r.user_id = u.user_id
LEFT JOIN addresses d ON d.created_by = u.user_id
WHERE u.user_id = :user_id;
