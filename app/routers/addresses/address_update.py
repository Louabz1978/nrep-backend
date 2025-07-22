from pydantic import BaseModel
from typing import Optional

class AddressUpdate(BaseModel):
    floor: Optional[str]
    apt: Optional[str]
    area: Optional[str]
    city: Optional[str]
    county: Optional[str]
    building_num: Optional[int]
    street: Optional[str]

    model_config = {
        "from_attributes": True
    }