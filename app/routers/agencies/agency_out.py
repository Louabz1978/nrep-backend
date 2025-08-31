from datetime import datetime 
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ...routers.addresses.address_out import AddressOut

class AgencyOut(BaseModel):
    agency_id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    created_at: datetime
    created_by: object
    broker: object
    address: Optional[AddressOut] = None

    model_config = {
        "from_attributes": True
    }