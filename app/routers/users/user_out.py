from pydantic import BaseModel, EmailStr
from typing import Optional

from ..agencies.agency_out import AgencyOut

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    lic_num: Optional[str] = None
    agency: Optional[AgencyOut]
    is_active: Optional[bool]

    model_config = {
        "from_attributes": True
    }
