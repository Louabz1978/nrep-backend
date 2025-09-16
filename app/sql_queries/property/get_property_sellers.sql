SELECT
    o.consumer_id AS consumer_id,
    o.name AS name,
    o.father_name AS father_name,
    o.surname AS surname,
    o.mother_name_surname AS mother_name_surname,
    o.place_birth AS place_birth,
    o.date_birth AS date_birth,
    o.registry AS registry,
    o.national_number AS national_number,
    o.email AS email,
    o.phone_number AS phone_number,
    o.created_by AS created_by,
    o.created_by_type AS created_by_type,
    o.created_at AS created_at

FROM property_owners op
LEFT JOIN consumers o ON op.seller_id = o.consumer_id
WHERE op.property_id = :property_id
