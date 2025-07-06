from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

from ..users.user_out import UserOut

class PropertyOut(BaseModel):
    property_id: int
    owner_id: int
    agent_id: Optional[int]
    address: str
    neighborhood: str
    city: str
    county: str
    description: str
    price: int
    property_type: Optional[str]
    floor: Optional[int]
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

    # Relationships
    owner: Optional[UserOut] = None
    agent: Optional[UserOut] = None
