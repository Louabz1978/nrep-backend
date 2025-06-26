SELECT
  u.user_id, u.first_name, u.last_name, u.email, u.role, u.phone_number,
  u.address, u.neighborhood, u.city, u.county, u.lic_num, u.is_active,
  a.agency_id AS agency_id, a.name AS agency_name, a.phone_number AS agency_phone_number
FROM users u
LEFT JOIN agencies a ON u.agency_id = a.agency_id