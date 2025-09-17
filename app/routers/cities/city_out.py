from pydantic import BaseModel

from typing import Optional
from datetime import datetime

class CityOut(BaseModel):
    city_id: int
    title: str
    
    created_by: int
    created_at: datetime

    updated_by: Optional[int]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
