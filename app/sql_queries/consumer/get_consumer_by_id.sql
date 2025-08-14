SELECT 
    c.*,
  r.admin, r.broker, r.realtor, r.buyer, r.seller, r.tenant
FROM consumers AS c
LEFT JOIN roles r ON r.consumer_id = c.consumer_id
WHERE c.consumer_id = :consumer_id;