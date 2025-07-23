from pydantic import BaseModel, model_validator
from typing import Optional

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
