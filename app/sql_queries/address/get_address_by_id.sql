SELECT 
    a.address_id, a.floor, a.apt, a.area, a.city, a.county, a.created_at, a.created_by, a.building_num, a.street
FROM addresses a
WHERE address_id = :address_id;