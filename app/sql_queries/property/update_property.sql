UPDATE properties SET 
    owner_id = :owner_id,
    description = :description,
    show_inst = :show_inst,
    price = :price,
    property_type = :property_type,
    bedrooms = :bedrooms,
    bathrooms = :bathrooms,
    property_realtor_commission = :property_realtor_commission,
    buyer_realtor_commission = :buyer_realtor_commission,
    area_space = :area_space,
    year_built = :year_built,
    latitude = :latitude,
    longitude = :longitude,
    status = :status,
    exp_date = :exp_date,
    last_updated = CURRENT_TIMESTAMP,
    images_urls = :images_urls
WHERE property_id = :property_id
RETURNING property_id;
