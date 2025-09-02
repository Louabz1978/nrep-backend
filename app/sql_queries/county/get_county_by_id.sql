SELECT 
    c.*,
    
    a.area_id,
    a.title As area_title,
    a.created_at As area_created_at,
    a.created_by As area_created_by,
    a.updated_at As area_updated_at,
    a.updated_by As area_updated_by

FROM counties c

LEFT JOIN areas a ON c.county_id = a.county_id

WHERE c.county_id = :county_id;
