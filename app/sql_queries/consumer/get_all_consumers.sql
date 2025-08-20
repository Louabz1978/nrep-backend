SELECT 
    *
FROM consumers
WHERE
    (:role = 'admin')
    OR
    (:role = 'realtor' AND created_by = :user_id)
    OR
    (:role = 'broker' AND (
        created_by = :user_id
        OR created_by IN (
            SELECT u1.user_id FROM users u1 WHERE u1.created_by = :user_id
        )
    ))
LIMIT :limit OFFSET :offset;
