from pydantic import BaseModel, model_validator
from datetime import date, datetime
from typing import Optional

class PropertyCreate(BaseModel):
    seller_id: int
    realtor_id: Optional[ int ]
    address: str
    neighborhood: str
    city: str
    county: str
    description: str
    price: int
    property_type: Optional[ str ] = None
    floor: Optional[ int ] = None
    bedrooms: int
    bathrooms: float
    property_agent_commission: float
    buyer_agent_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: str
    listed_date: date
    last_updated: datetime
    image_url: Optional[str]

    @model_validator(mode='before')
    def validate_roles(cls, values):
        realtor_id = values.get('realtor_id')
        seller_id = values.get('seller_id')
        # Treat 0 as no realtor_id provided
        if realtor_id == 0:
            realtor_id = None
            values['realtor_id'] = None
        # Treat 0 as no seller_id provided
        if seller_id == 0:
            seller_id = None
            values['seller_id'] = None
        #seller_id is required
        if not seller_id:
            raise ValueError("seller_id is required")

        return values
