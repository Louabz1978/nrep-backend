SELECT 
    address_id, floor, apt, area, city, county, created_at, created_by, building_num, street
FROM addresses
WHERE address_id = :address_id