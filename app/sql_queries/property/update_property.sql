UPDATE properties SET 
    owner_id = :owner_id,
    description = :description,
    price = :price,
    property_type = :property_type,
    floor = :floor,
    bedrooms = :bedrooms,
    bathrooms = :bathrooms,
    property_realtor_commission = :property_realtor_commission,
    buyer_realtor_commission = :buyer_realtor_commission,
    area_space = :area_space,
    year_built = :year_built,
    latitude = :latitude,
    longitude = :longitude,
    status = :status,
    last_updated = CURRENT_TIMESTAMP,
    image_url = :image_url,
    created_by = :created_by
WHERE property_id = :property_id
RETURNING property_id;
