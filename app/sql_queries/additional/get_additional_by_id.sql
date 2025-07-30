SELECT 
    elevator,
    balcony,
    ac,
    fan_number, 
    garage, 
    garden, 
    solar_system, 
    water, 
    jacuzzi, 
    pool

    FROM additional 

    WHERE property_id = :property_id;