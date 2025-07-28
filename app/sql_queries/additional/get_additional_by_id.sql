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

    WHERE additional_id = :additional_id;