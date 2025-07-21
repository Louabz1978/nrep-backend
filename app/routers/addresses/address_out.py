from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional

class AddressOut(BaseModel):
    address_id: int
    address: Optional[str]
    floor: str
    apt: str
    area: str
    city: Optional[str]
    county: Optional[str]
    created_at: datetime
    created_by: int

    model_config = {
        "from_attributes": True
    }
    
    @field_validator("created_at", mode="before")
    @classmethod
    def ensure_datetime(cls, v):
        if isinstance(v, time):
            return datetime.combine(date.today(), v)
        return v

    model_config = {
        "from_attributes": True
    }