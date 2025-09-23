SELECT 
    b.user_id AS broker_user_id,
    b.first_name AS broker_first_name,
    b.last_name AS broker_last_name,
    b.email AS broker_email,
    b.phone_number AS broker_phone_number,
    b.created_by AS broker_created_by,
    b.created_at AS broker_created_at
FROM agency_brokers ab
LEFT JOIN users b ON b.user_id = ab.broker_id 
WHERE ab.agency_id = :agency_id