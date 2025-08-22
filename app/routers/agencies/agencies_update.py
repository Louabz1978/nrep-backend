from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional

from app.routers.addresses.address_update import AddressUpdate

class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[AddressUpdate] = None
    broker_id: Optional[int] = Field(
        None,
        description="Optional broker user_id to assign as agency broker"
    )

    @model_validator(mode='before')
    def validate_broker(cls, values):
        broker_id = values.get("broker_id")
        if broker_id == 0:
            values["broker_id"] = None
        return values
