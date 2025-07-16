from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .roles_enum import UserRole
from ..agencies.agency_out import AgencyOut

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: UserRole

    address_id: int
    created_by: int
    created_at: datetime

    agency_id: Optional[int] = None
    lic_num: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
