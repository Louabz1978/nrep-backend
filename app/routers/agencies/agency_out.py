from pydantic import BaseModel
from typing import Optional

class AgencyOut(BaseModel):
    agency_id: int
    name: str
    phone_number: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
