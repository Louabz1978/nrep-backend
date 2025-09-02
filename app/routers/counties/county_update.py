from pydantic import BaseModel
from typing import Optional


class CountyUpdate(BaseModel):
    title: Optional[str] = None
    city_id: Optional[int] = None
