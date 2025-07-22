from pydantic import BaseModel

class AddressCreate(BaseModel):
    floor: int
    apt: int
    area: str
    city: str
    county: str
    building_num: int
    street: str

    model_config = {
        "from_attributes": True
    }
