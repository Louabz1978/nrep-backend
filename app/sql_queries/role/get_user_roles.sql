SELECT r.*
FROM users u
LEFT JOIN roles r ON r.user_id = u.user_id
WHERE u.user_id = :user_id;