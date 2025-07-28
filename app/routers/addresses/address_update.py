from pydantic import BaseModel
from typing import Optional

class AddressUpdate(BaseModel):
    floor: Optional[int] = None
    apt: Optional[int] = None
    area: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    building_num: Optional[int] = None
    street: Optional[str] = None

    model_config = {
        "from_attributes": True
    }