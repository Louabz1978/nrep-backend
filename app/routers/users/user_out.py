from pydantic import BaseModel, EmailStr
from typing import Optional,List
from datetime import datetime

from .roles_enum import UserRole

from ..addresses.address_out import AddressOut

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: List[UserRole]
    address: Optional[AddressOut] = None
    created_by: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
