SELECT
  a.*,
  d.address_id,
  d.floor,
  d.apt,
  d.area,
  d.city,
  d.county,
  d.building_num,
  d.street,
  d.created_at AS address_created_at
FROM agencies a
LEFT JOIN addresses d ON d.address_id = a.address_id
WHERE a.agency_id = :agency_id;
