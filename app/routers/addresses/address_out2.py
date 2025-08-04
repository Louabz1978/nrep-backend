from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional
from app.routers.users.user_out import UserOut

class AddressOut2(BaseModel):
    address_id: int
    floor: int
    apt: int
    area: str
    city: Optional[str]
    county: Optional[str]
    created_at: datetime
    created_by_user: UserOut
    building_num: Optional[str] = None
    street: Optional[str] = None
    
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
