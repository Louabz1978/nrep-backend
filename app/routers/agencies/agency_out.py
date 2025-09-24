from datetime import datetime 
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ...routers.addresses.address_out import AddressOut

class AgencyOut(BaseModel):
    agency_id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    created_at: datetime
    created_by: object
    brokers: List[object]
    address: Optional[AddressOut] = None

    model_config = {
        "from_attributes": True
    }