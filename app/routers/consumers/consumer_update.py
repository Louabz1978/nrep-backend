from fastapi import Form
from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import date


class ConsumerUpdate(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    surname: Optional[str] = None
    mother_name_surname: Optional[str] = None
    place_birth: Optional[str] = None
    date_birth: Optional[date] = None
    registry: Optional[str] = None
    national_number: Optional[int] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

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
        email: Optional[str] = Form(None),
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

    @model_validator(mode="before")
    def clean_fields(cls, values):
        # Example rule: Treat empty strings as None
        for field, value in values.items():
            if isinstance(value, str) and value.strip() == "":
                values[field] = None
        return values
