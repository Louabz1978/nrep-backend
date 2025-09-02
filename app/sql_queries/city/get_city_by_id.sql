SELECT 
    c.*,
    
    co.county_id As county_id,
    co.title As county_title,
    co.created_at As county_created_at,
    co.created_by As county_created_by,
    co.updated_at As county_updated_at,
    co.updated_by As county_updated_by,
    
    a.area_id As area_id,
    a.title As area_title,
    a.created_at As area_created_at,
    a.created_by As area_created_by,
    a.updated_at As area_updated_at,
    a.updated_by As area_updated_by

FROM cities c

LEFT JOIN counties co ON c.city_id = co.city_id
LEFT JOIN areas a ON co.county_id = a.county_id

WHERE c.city_id = :city_id;
