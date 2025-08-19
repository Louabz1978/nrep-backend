from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
from ..users.roles_enum import UserRole

class ConsumerCreate(BaseModel):
    name: str = Field(..., max_length=50)
    father_name: str = Field(..., max_length=50)
    surname: str = Field(..., max_length=50)
    mother_name_surname: str
    place_birth: str
    date_birth: date
    registry: str
    national_number: Optional[int] = None

    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)

    model_config = {
        "from_attributes": True
    }

