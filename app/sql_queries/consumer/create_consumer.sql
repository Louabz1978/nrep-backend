INSERT INTO consumers (
    name,
    father_name,
    surname,
    mother_name_surname,
    place_birth,
    date_birth,
    registry,
    national_number,
    email,
    phone_number,
    created_by,
    created_at
)
VALUES (
    :name,
    :father_name,
    :surname,
    :mother_name_surname,
    :place_birth,
    :date_birth,
    :registry,
    :national_number,
    :email,
    :phone_number,
    :created_by,
    :created_at
)
RETURNING consumer_id;
