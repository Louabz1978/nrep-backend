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
    c.created_by,
    c.created_by_type,
    c.created_at
FROM consumers c
WHERE
    (
        :role = 'admin'
        OR (:role = 'realtor' AND c.created_by = :user_id)
        OR (:role = 'broker' AND (
            c.created_by = :user_id
            OR c.created_by IN (SELECT u1.user_id FROM users u1 WHERE u1.created_by = :user_id)
        ))
    )
    AND (:name IS NULL OR c.name ILIKE :name)
    AND (:father_name IS NULL OR c.father_name ILIKE :father_name)
    AND (:surname IS NULL OR c.surname ILIKE :surname)
    AND (:mother_name_surname IS NULL OR c.mother_name_surname ILIKE :mother_name_surname)
    AND (:place_birth IS NULL OR c.place_birth ILIKE :place_birth)
    AND (:date_birth IS NULL OR c.date_birth = :date_birth)
    AND (:registry IS NULL OR c.registry ILIKE :registry)
    AND (:national_number IS NULL OR c.national_number::TEXT ILIKE :national_number)
    AND (:email IS NULL OR c.email ILIKE :email)
    AND (:phone_number IS NULL OR c.phone_number ILIKE :phone_number)
    AND (:created_by IS NULL OR c.created_by = :created_by)
    AND (:created_by_type IS NULL OR c.created_by_type ILIKE :created_by_type)
    AND (:created_at IS NULL OR c.created_at::date = :created_at)
ORDER BY {sort_by} {sort_order}
LIMIT :limit OFFSET :offset;
