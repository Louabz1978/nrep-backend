from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.routers.users.user_out import UserOut
from app.routers.addresses.address_out import AddressOut

from .properties_type_enum import PropertyTypes
from .properties_status_enum import PropertyStatus

class PropertyOut(BaseModel):
    property_id: int
    description: str
    price: int
    property_type: Optional[PropertyTypes]
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: PropertyStatus
    created_at: datetime
    last_updated: datetime
    images_urls: Optional[str]
    mls_num: Optional[int] = None

    created_by_user: Optional[UserOut]
    owner: Optional[UserOut]
    address: Optional[AddressOut]

    model_config = {
        "from_attributes": True
    }