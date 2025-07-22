from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional

from ..addresses.address_create import AddressCreate

class PropertyCreate(BaseModel):
    owner_id: int
    description: str
    price: int
    property_type: Optional[ str ] = None
    floor: Optional[ int ] = None
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: str
    created_at : datetime
    last_updated: datetime
    image_url: Optional[str]
    mls_num: Optional[ int ]
    address: Optional[AddressCreate] = None

    @model_validator(mode='before')
    def validate_roles(cls, values):
        owner_id = values.get('owner_id')
        # Treat 0 as no seller_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        #seller_id is required
        if not owner_id:
            raise ValueError("owner_id is required")

        return values
