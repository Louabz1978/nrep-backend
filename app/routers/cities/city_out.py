from pydantic import BaseModel

from typing import Optional, List
from datetime import datetime

from ..counties.county_out import CountyOut

class CityOut(BaseModel):
    city_id: int
    title: str
    
    created_by: int
    created_at: datetime

    updated_at: Optional[int]
    updated_by: Optional[datetime]

    counties: Optional[List[CountyOut]] = None

    model_config = {
        "from_attributes": True
    }
