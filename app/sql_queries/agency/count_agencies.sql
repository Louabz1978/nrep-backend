SELECT COUNT(*)

FROM agencies a

LEFT JOIN addresses addr ON addr.agency_id = a.agency_id

WHERE (:name IS NULL OR a.name ILIKE :name)
    AND (:email IS NULL OR a.email ILIKE :email)
    AND (:phone_number IS NULL OR a.phone_number ILIKE :phone_number)
    AND (:broker_id IS NULL OR a.broker_id = :broker_id)
    AND (:created_by IS NULL OR a.created_by = :created_by)
    AND (:city IS NULL OR addr.city ILIKE :city)
    