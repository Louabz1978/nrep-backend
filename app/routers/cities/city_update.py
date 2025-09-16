from pydantic import BaseModel
from typing import Optional


class CityUpdate(BaseModel):
    title: Optional[str] = None
    county_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
