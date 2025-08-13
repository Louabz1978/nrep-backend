SELECT COUNT(*)
FROM properties p
LEFT JOIN addresses a ON p.property_id = a.property_id
WHERE
    p.created_by = :created_by
    AND (:city IS NULL OR a.city ILIKE :city)
    AND (:area IS NULL OR a.area ILIKE :area)
    AND (:min_price IS NULL OR p.price >= :min_price)
    AND (:max_price IS NULL OR p.price <= :max_price)
    AND (:mls_num IS NULL OR p.mls_num = :mls_num)
    AND (:status IS NULL OR p.status = :status);
