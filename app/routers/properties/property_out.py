from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.routers.users.user_out import UserOut
from app.routers.addresses.address_out import AddressOut

class PropertyOut(BaseModel):
    property_id: int
    description: str
    price: int
    property_type: Optional[str]
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: str
    created_at: datetime
    last_updated: datetime
    image_url: Optional[str]
    mls_num: Optional[int] = None

    created_by_user: Optional[UserOut]
    owner: Optional[UserOut]
    address: Optional[AddressOut]

    model_config = {
        "from_attributes": True
    }