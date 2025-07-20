from pydantic import BaseModel, model_validator
from typing import Optional

from ..addresses.address_create import AddressCreate

class PropertyUpdate(BaseModel):
    owner_id: Optional[ int ] = None
    description: Optional[ str ] = None
    price: Optional[ str ] = None
    property_type: Optional[ str ] = None
    floor: Optional[ int ] = None
    bedrooms: Optional[ int ] = None
    bathrooms: Optional[ float ] = None
    property_realtor_commission: Optional[ float ] = None
    buyer_realtor_commission: Optional[ float ] = None
    area_space: Optional[ int ] = None
    year_built: Optional[ int ] = None
    latitude: Optional[ float ] = None
    longitude: Optional[ float ] = None
    status: Optional[ str ] = None
    image_url: Optional[ str ] = None
    address: Optional[ AddressCreate ] = None

    @model_validator(mode='before')
    def validate_roles(cls, values):
        owner_id = values.get('owner_id')
        # Treat 0 as no owner_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        
        return values
