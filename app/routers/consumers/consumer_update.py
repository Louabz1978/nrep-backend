from fastapi import Form
from pydantic import BaseModel, EmailStr, model_validator, StringConstraints, Field, field_validator
from typing import Optional, Annotated
from datetime import date
import re

name_pattern = re.compile(r'^[A-Za-z\u0600-\u06FF\s]+$')
phone_number_pattern = re.compile(r'^\d{7,15}$')
class ConsumerUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(None)
    ]
    father_name: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(None)
    ]
    surname: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(None)
    ]
    mother_name_surname: Annotated[
        Optional[str],
        StringConstraints(strip_whitespace=True, min_length=2),
        Field(None)
    ]
    place_birth: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=100),
        Field(None)
    ]
    date_birth: Optional[date] = None
    registry: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(None)
    ]
    national_number: Optional[int] = None
    email: Optional[EmailStr] = None
    phone_number: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True),
        Field(None)
    ]

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        father_name: Optional[str] = Form(None),
        surname: Optional[str] = Form(None),
        mother_name_surname: Optional[str] = Form(None),
        place_birth: Optional[str] = Form(None),
        date_birth: Optional[date] = Form(None),
        registry: Optional[str] = Form(None),
        national_number: Optional[int] = Form(None),
        email: Optional[EmailStr] = Form(None),
        phone_number: Optional[str] = Form(None),
    ):
        return cls(
            name=name,
            father_name=father_name,
            surname=surname,
            mother_name_surname=mother_name_surname,
            place_birth=place_birth,
            date_birth=date_birth,
            registry=registry,
            national_number=national_number,
            email=email,
            phone_number=phone_number
        )

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
    
    @field_validator("date_birth")
    def validate_date_birth(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date Birth must be in the past")
        return v

    @field_validator("national_number")
    def validate_national_number(cls, v: int) -> int:
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
