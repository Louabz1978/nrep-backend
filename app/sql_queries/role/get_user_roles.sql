SELECT r.*
FROM users u
JOIN roles r ON u.role_id = r.roles_id
WHERE u.user_id = :user_id;