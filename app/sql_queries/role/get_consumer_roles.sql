SELECT r.*
FROM consumers c
LEFT JOIN roles r ON r.consumer_id = c.consumer_id
WHERE c.consumer_id = :consumer_id;