from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from datetime import date

from app.routers.users.user_out import UserOut
from app.routers.consumers.consumer_out import ConsumerOut
from ..additional.additional_out import AdditionalOut
from app.routers.addresses.address_out import AddressOut

from ...utils.enums import PropertyStatus, PropertyTypes, PropertyTransactionType

class PropertyOut(BaseModel):
    property_id: int
    description: str
    show_inst: str
    price: int
    property_type: PropertyTypes
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: PropertyStatus
    trans_type: PropertyTransactionType
    exp_date: date
    created_at: datetime
    last_updated: datetime
    images_urls: Optional[List[Dict]]
    mls_num: Optional[int] = None

    created_by_user: Optional[UserOut]
    owner: Optional[ConsumerOut]
    address: Optional[AddressOut] = None
    additional: Optional[AdditionalOut] = None

    model_config = {
        "from_attributes": True
    }
    