from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    address_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
