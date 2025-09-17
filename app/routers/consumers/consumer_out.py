from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ConsumerOut(BaseModel):
    consumer_id: int
    name: str
    father_name: str
    surname: str
    mother_name_surname: str
    place_birth: str
    date_birth: datetime
    registry: str
    national_number: str
    email: Optional[ EmailStr ]
    phone_number: Optional[ str ]
    created_at: datetime
    created_by: int
    created_by_type: str

    model_config = {
        "from_attributes": True
    }