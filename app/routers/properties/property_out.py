from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

from ..users.user_out import UserOut

class PropertyOut(BaseModel):
    property_id: int
    seller_id: int
    realtor_id: Optional[int]
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
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: str
    listed_date: date
    last_updated: datetime
    image_url: Optional[str]

    # Relationships
    seller: Optional[UserOut] = None
    realtor: Optional[UserOut] = None
