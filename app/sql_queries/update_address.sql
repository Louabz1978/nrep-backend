UPDATE addresses SET 
    address = :address,
    floor = :floor,
    apt = :apt,
    area = :area,
    city = :city,
    county = :county
WHERE address_id = :address_id;