SELECT l.license_id,
       l.lic_num,
       l.lic_status,
       l.lic_type,
       l.user_id,
       l.agency_id
FROM licenses l
WHERE (
    :role = 'admin'
    OR (:role = 'broker' AND l.agency_id = (
        SELECT agency_id FROM users WHERE user_id = :user_id
    ))
    OR (:role = 'realtor' AND l.user_id = :user_id)
)
AND (:lic_status IS NULL OR l.lic_status = :lic_status)
AND (:lic_type IS NULL OR l.lic_type = :lic_type)
AND (:agency_id IS NULL OR l.agency_id = :agency_id)
AND (:filter_user_id IS NULL OR l.user_id = :filter_user_id)

ORDER BY {sort_by} {sort_order}
LIMIT :limit OFFSET :offset;