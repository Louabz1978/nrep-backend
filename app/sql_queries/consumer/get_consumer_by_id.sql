SELECT 
    c.*
FROM consumers AS c
WHERE c.consumer_id = :consumer_id;