SELECT
  u.user_id, u.first_name, u.last_name, u.email, u.phone_number, u.role_id, u.address_id, u.created_by, u.created_at,
  r.admin, r.broker, r.realtor, r.buyer, r.seller , r.tenant
FROM users u
JOIN roles r ON u.role_id = r.roles_id
WHERE u.user_id = :user_id;
