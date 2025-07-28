from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List
import re

from .roles_enum import UserRole

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr

    password: str 
    # password: str = Field(..., min_length=8)

    role: List[UserRole]
    phone_number: str  

    model_config = {
        "from_attributes": True
    }
    
    # @validator("password")
    # def validate_password_strength(cls, v):
    #     if not re.search(r"\d", v):
    #         raise ValueError("must contain at least one digit")
    #     if not re.search(r"[A-Z]", v):
    #         raise ValueError("must contain at least one uppercase letter")
    #     return v

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
