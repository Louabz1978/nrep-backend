UPDATE addresses SET 
    floor = :floor,
    apt = :apt,
    area = :area,
    city = :city,
    county = :county,
    building_num = :building_num,
    street = :street
WHERE address_id = :address_id;