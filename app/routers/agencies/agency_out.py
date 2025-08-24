from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.routers.addresses.address_out import AddressOut
from app.routers.users.user_out import UserOut

class AgencyOut(BaseModel):
    agency_id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    created_at: datetime
    created_by: int
    broker: Optional[UserOut]
    address: Optional[AddressOut] = None

    model_config = {
        "from_attributes": True
    }
