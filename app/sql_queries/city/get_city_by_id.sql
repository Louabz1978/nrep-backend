SELECT 
    c.*,
    
    co.county_id,
    co.title As county_title,
    
    a.area_id,
    a.title As area_title

FROM cities c

LEFT JOIN counties co ON c.city_id = co.city_id
LEFT JOIN areas a ON co.county_id = a.county_id

WHERE c.city_id = :city_id;
