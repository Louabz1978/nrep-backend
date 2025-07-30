INSERT INTO addresses (
    floor,
    apt,
    area,
    city,
    county,
    created_at,
    created_by,
    building_num,
    street,
    property_id
)
VALUES (
    :floor,
    :apt,
    :area,
    :city,
    :county,
    :created_at,
    :created_by,
    :building_num,
    :street,
    :property_id
)
RETURNING address_id;
