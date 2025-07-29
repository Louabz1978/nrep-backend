SELECT COUNT(*) FROM users u
JOIN roles r ON u.role_id = r.roles_id
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
