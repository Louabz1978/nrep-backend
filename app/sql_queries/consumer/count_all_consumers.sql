SELECT COUNT(*) AS total
FROM consumers c
WHERE
    (:role = 'admin')
    OR
    (:role = 'realtor' AND c.created_by = :user_id)
    OR
    (:role = 'broker' AND (
        c.created_by = :user_id
        OR c.created_by IN (
            SELECT u1.user_id FROM users u1 WHERE u1.created_by = :user_id
        )
    ));
