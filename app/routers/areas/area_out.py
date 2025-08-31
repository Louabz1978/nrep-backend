from pydantic import BaseModel

from typing import Optional

from datetime import datetime

class AreaOut(BaseModel):
    area_id: int
    title: str

    created_by: int
    created_at: datetime

    updated_at: Optional[int]
    updated_by: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
