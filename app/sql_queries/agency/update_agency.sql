UPDATE agencies
SET
    name = :name,
    email = :email,
    phone_number = :phone_number,
    broker_id = :broker_id
WHERE agency_id = :agency_id