SELECT 
    u.*, 
    r.admin, 
    r.broker, 
    r.realtor,
    r.buyer,
    r.seller,
    r.tenant
FROM users u
LEFT JOIN roles r ON r.user_id = u.user_id
WHERE
    (:role = 'admin')
    OR
    (:role = 'realtor' AND u.created_by = :user_id)
    OR
    (:role = 'broker' AND (
        u.created_by = :user_id
        OR u.created_by IN (
            SELECT u1.user_id FROM users u1 WHERE u1.created_by = :user_id
        )
    ));
