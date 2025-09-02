from pydantic import BaseModel
from typing import Optional


class CityUpdate(BaseModel):
    title: Optional[str] = None
