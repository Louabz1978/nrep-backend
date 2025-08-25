SELECT l.license_id,
       l.lic_num,
       l.lic_status,
       l.lic_type,
       l.user_id,
       l.agency_id
FROM licenses l
WHERE l.license_id = :license_id
AND (
    :role = 'admin'
    OR (:role = 'broker' AND l.agency_id = (
        SELECT agency_id FROM users WHERE user_id = :user_id
    ))
    OR (:role = 'realtor' AND l.user_id = :user_id)
)
