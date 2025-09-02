from pydantic import BaseModel
from typing import Optional

class AreaUpdate(BaseModel):
    title: Optional[str] = None
    county_id: Optional[int] = None
