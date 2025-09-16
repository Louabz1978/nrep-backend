from pydantic import BaseModel

from typing import Optional
from datetime import datetime

class CountyOut(BaseModel):
    county_id: int
    title: str
    
    created_by: int
    created_at: datetime

    updated_by: Optional[int]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
