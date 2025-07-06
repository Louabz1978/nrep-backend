from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional

class AgencyCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
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
