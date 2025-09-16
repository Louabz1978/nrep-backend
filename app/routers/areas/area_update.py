from pydantic import BaseModel
from typing import Optional

class AreaUpdate(BaseModel):
    title: Optional[str] = None
    city_id: Optional[int] = None
