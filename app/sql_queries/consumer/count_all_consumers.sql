SELECT COUNT(*) AS total
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
    AND (:national_number IS NULL OR c.national_number = :national_number)
    AND (:email IS NULL OR c.email ILIKE :email)
    AND (:phone_number IS NULL OR c.phone_number ILIKE :phone_number)
    AND (:created_by IS NULL OR c.created_by = :created_by)
    AND (:created_by_type IS NULL OR c.created_by_type ILIKE :created_by_type)
    AND (:created_at IS NULL OR c.created_at::date = :created_at);
