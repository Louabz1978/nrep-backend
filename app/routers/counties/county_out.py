from pydantic import BaseModel

from typing import Optional, List
from datetime import datetime

from ..areas.area_out import AreaOut

class CountyOut(BaseModel):
    county_id: int
    title: str
    
    created_by: int
    created_at: datetime

    updated_at: Optional[int]
    updated_by: Optional[datetime]

    areas: Optional[List[AreaOut]] = None

    model_config = {
        "from_attributes": True
    }
