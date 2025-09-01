from pydantic import BaseModel, EmailStr, Field, field_validator, StringConstraints
from typing import List,Annotated
import re

from .roles_enum import UserRole

name_pattern = re.compile(r'^[A-Za-z\u0600-\u06FF\s]+$')
phone_number_pattern = re.compile(r'^\d{7,15}$')

class UserCreate(BaseModel):
    first_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(description="First name in Arabic or English, 2–50 chars")
    ]

    last_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(description="Last name in Arabic or English, 2–50 chars")
    ]

    email: Annotated[
        EmailStr,
        Field(description="Valid email address")
    ]

    password: str
    # password: Annotated[
    #     str,
    #     StringConstraints(min_length=8),
    #     Field(description="At least 8 chars, must include an uppercase letter and a digit")
    # ]

    role: List[UserRole]
    
    phone_number: Annotated[
        str,
        StringConstraints(strip_whitespace=True),
        Field(description="Must be a valid phone number")
    ] 

    model_config = {
        "from_attributes": True
    }
    
    @field_validator("first_name")
    def validate_first_name(cls,v: str) -> str:
        if not name_pattern.match(v):
            raise ValueError("First name must contain only Arabic or English letters")
        return v
    
    @field_validator("last_name")
    def validate_last_name(cls,v: str) -> str:
        if not name_pattern.match(v):
            raise ValueError("Last name must contain only Arabic or English letters")
        return v

    # @field_validator("password")
    # def validate_password_strength(cls, v):
    #     if ( not re.search(r"\d", v) ) or ( not re.search(r"[A-Z]",v) ):
    #         raise ValueError("must contain at least one uppercase letter and one digit")
    #     return v

    @field_validator("phone_number")
    def validate_and_convert_phone(cls, v: str) -> str:
        # Optional: remove '+' if exists
        v = v.strip()
        if v.startswith('+'):
            v = v[1:]

        # Validate
        if not phone_number_pattern.match(v):
            raise ValueError("must be a valid phone number")

        return v
