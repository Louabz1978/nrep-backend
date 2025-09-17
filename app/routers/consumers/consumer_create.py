from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from typing import Optional, Annotated
from datetime import date
import re

name_pattern = re.compile(r'^[A-Za-z\u0600-\u06FF\s]+$')
phone_number_pattern = re.compile(r'^\d{7,15}$')
class ConsumerCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
    ]
    father_name: Annotated[
        str, 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
    ]
    surname: Annotated[
        str, 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
    ]
    mother_name_surname: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2)
    ]
    place_birth: Annotated[
        str, 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=100)
    ]
    date_birth: date
    registry: Annotated[
        str, 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
    ]
    national_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True),
        Field(None)
    ]

    model_config = {
        "from_attributes": True
    }
    @field_validator("name")
    def validate_name(cls,v: str) -> str:
        if not name_pattern.match(v):
            raise ValueError("Name must contain only Arabic or English letters")
        return v
    
    @field_validator("father_name")
    def validate_father_name(cls,v: str) -> str:
        if not name_pattern.match(v):
            raise ValueError("Father name must contain only Arabic or English letters")
        return v
    
    @field_validator("surname")
    def validate_surname(cls,v: str) -> str:
        if not name_pattern.match(v):
            raise ValueError("Surname must contain only Arabic or English letters")
        return v
    
    @field_validator("date_birth")
    def validate_date_birth(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date Birth must be in the past")
        return v

    @field_validator("national_number")
    def validate_national_number(cls, v: str) -> str:
        s=str(v)
        if len(s) != 11:
            raise ValueError("National number must be exactly 11 digits")
        return v
        
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