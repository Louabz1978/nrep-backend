INSERT INTO addresses (
    floor,
    apt,
    area,
    city,
    county,
    created_at,
    created_by,
    building_num,
    street
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
    :street
)
RETURNING address_id;