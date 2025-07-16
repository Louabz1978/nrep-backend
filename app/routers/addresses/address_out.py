from pydantic import BaseModel
from datetime import datetime

class AddressOut(BaseModel):
    address_id: int
    address: str
    floor: str
    apt:str
    area:str
    city:str
    county:str
    created_at: datetime
    created_by: int
    
    model_config = {
        "from_attributes": True
    }