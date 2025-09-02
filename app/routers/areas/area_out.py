from pydantic import BaseModel

from typing import Optional

from datetime import datetime

class AreaOut(BaseModel):
    area_id: int
    title: str

    created_by: int
    created_at: datetime

    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
