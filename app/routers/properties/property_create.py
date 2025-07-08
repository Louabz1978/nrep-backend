from pydantic import BaseModel, model_validator
from datetime import date, datetime
from typing import Optional

class PropertyCreate(BaseModel):
    owner_id: int
    agent_id: Optional[ int ]
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
    listing_agent_commission: float
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
        agent_id = values.get('agent_id')
        owner_id = values.get('owner_id')
        # Treat 0 as no agent_id provided
        if agent_id == 0:
            agent_id = None
            values['agent_id'] = None
        # Treat 0 as no owner_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        #owner_id is required
        if not owner_id:
            raise ValueError("owner_id is required")

        return values
