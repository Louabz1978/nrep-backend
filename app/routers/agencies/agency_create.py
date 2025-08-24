from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

class AgencyCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    broker_id: int

    @field_validator("phone_number")
    def validate_and_convert_phone(cls, v):
        # Optional: remove '+' if exists
        v = v.strip()
        if v.startswith('+'):
            v = v[1:]

        # Validate
        if not re.match(r"^\d{7,15}$", v):
            raise ValueError("must be a valid phone number")

        return int(v)