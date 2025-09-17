from pydantic import BaseModel, EmailStr, model_validator, Field, StringConstraints, field_validator
from typing import Optional, Annotated
import re
from app.routers.addresses.address_update import AddressUpdate

phone_number_pattern = re.compile(r'^\d{7,15}$')
class AgencyUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        StringConstraints(strip_whitespace=True, min_length=2, max_length=50),
        Field(None)
    ]
    email: Optional[EmailStr] = None
    phone_number: Annotated[
        Optional[str], 
        StringConstraints(strip_whitespace=True),
        Field(None)
    ]
    address: Optional[AddressUpdate] = None
    broker_id: Optional[int] = Field(
        None,
        gt=0,
        description="Optional broker user_id to assign as agency broker"
    )

    @field_validator("phone_number")
    def validate_and_convert_phone(cls, v):
        # Optional: remove '+' if exists
        v = v.strip()
        if v.startswith('+'):
            v = v[1:]

        # Validate
        if not phone_number_pattern.match(v):
            raise ValueError("must be a valid phone number")

        return v
    
    @model_validator(mode='before')
    def validate_broker(cls, values):
        broker_id = values.get("broker_id")
        if broker_id == 0:
            values["broker_id"] = None
        return values
