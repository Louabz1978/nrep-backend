from pydantic import BaseModel
from fastapi import Form

class AddressCreate(BaseModel):
    floor: int = Form(...)
    apt: int = Form(...)
    area: str = Form(...)
    city: str = Form(...)
    county: str = Form(...)
    building_num: int = Form(...)
    street: str = Form(...)

    @classmethod
    def as_form(
        cls,
        floor: int = Form(...),
        apt: int = Form(...),
        area: str = Form(...),
        city: str = Form(...),
        county: str = Form(...),
        building_num: int = Form(...),
        street: str = Form(...)
    ):
        return cls(
            floor = floor,
            apt = apt,
            area = area,
            city = city,
            county = county,
            building_num = building_num,
            street = street
        )
    
    model_config = {
        "from_attributes": True
    }
