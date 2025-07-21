from pydantic import BaseModel
from typing import Optional

class AddressUpdate(BaseModel):
    address: Optional[ str ] = None
    floor: Optional[ str ] = None
    apt: Optional[ str ] = None
    area: Optional[ str ] = None
    city: Optional[ str ] = None
    county: Optional[ str ] = None

    model_config = {
        "from_attributes": True
    }