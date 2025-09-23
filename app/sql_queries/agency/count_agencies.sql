SELECT COUNT(DISTINCT a.agency_id)

FROM agencies a

LEFT JOIN addresses addr ON addr.agency_id = a.agency_id
LEFT JOIN agency_brokers ab ON ab.agency_id = a.agency_id

WHERE (:name IS NULL OR a.name ILIKE :name)
    AND (:email IS NULL OR a.email ILIKE :email)
    AND (:phone_number IS NULL OR a.phone_number ILIKE :phone_number)
    AND (:created_by IS NULL OR a.created_by = :created_by)
    AND (:city IS NULL OR addr.city ILIKE :city)
    AND (:broker_id IS NULL OR a.agency_id IN (
      SELECT ab.agency_id
      FROM agency_brokers ab
      WHERE ab.broker_id = :broker_id
  ))
    