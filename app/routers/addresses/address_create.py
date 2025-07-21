from pydantic import BaseModel

class AddressCreate(BaseModel):
    address: str
    floor: str
    apt: str
    area: str
    city: str
    county: str

    model_config = {
        "from_attributes": True
    }
