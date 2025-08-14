SELECT
    c.consumer_id,
    c.name,
    c.father_name,
    c.surname,
    c.mother_name_surname,
    c.place_birth,
    c.date_birth,
    c.registry,
    c.national_number,
    c.email,
    c.phone_number,
    c.created_at,
    c.created_by,
    r.role_id,
    r.role_name
FROM consumers c
LEFT JOIN roles r ON r.consumer_id = c.consumer_id
WHERE c.consumer_id = :consumer_id;
