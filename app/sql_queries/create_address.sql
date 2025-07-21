INSERT INTO addresses (
    address,
    floor,
    apt,
    area,
    city,
    county,
    created_at,
    created_by
)
VALUES (
    :address,
    :floor,
    :apt,
    :area,
    :city,
    :county,
    :created_at,
    :created_by
)
RETURNING address_id;