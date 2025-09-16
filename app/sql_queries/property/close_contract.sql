UPDATE properties
SET status = 'closed'
WHERE mls_num = :mls
RETURNING property_id, mls_num, status;