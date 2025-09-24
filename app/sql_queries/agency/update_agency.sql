UPDATE agencies
SET
    name = :name,
    email = :email,
    phone_number = :phone_number,
WHERE agency_id = :agency_id