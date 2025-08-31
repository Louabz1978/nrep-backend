SELECT 
    c.*,
    
    a.area_id,
    a.title As area_title

FROM counties c

LEFT JOIN areas a ON c.county_id = a.county_id

WHERE c.county_id = :county_id;
