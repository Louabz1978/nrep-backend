from pydantic import BaseModel, EmailStr, field_validator, StringConstraints, Field
from typing import Annotated
import re

phone_number_pattern = re.compile(r'^\d{7,15}$')
class AgencyCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
    ]
    email: EmailStr
    phone_number: Annotated[
        str,
        StringConstraints(strip_whitespace=True)
    ]
    broker_id: int = Field(..., gt=0)

    @field_validator("phone_number")
    def validate_and_convert_phone(cls, v):
        # Optional: remove '+' if exists
        v = v.strip()
        if v.startswith('+'):
            v = v[1:]

        # Validate
        if not phone_number_pattern.match(v):
            raise ValueError("must be a valid phone number")

        return int(v)