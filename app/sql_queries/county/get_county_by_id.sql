SELECT 
    c.*

FROM counties c

WHERE c.county_id = :county_id;
