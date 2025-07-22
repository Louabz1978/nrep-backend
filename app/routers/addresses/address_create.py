from pydantic import BaseModel

class AddressCreate(BaseModel):
    floor: str
    apt: str
    area: str
    city: str
    county: str
    building_num: int
    street: str

    model_config = {
        "from_attributes": True
    }
