from fastapi import Form
from pydantic import BaseModel
from typing import Optional

class AddressUpdate(BaseModel):
    floor: Optional[int] = None
    apt: Optional[int] = None
    area: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    building_num: Optional[str] = None
    street: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        floor: Optional[int] = Form(None),
        apt: Optional[int] = Form(None),
        area: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        county: Optional[str] = Form(None),
        building_num: Optional[str] = Form(None),
        street: Optional[str] = Form(None)
    ):

        return cls(
            floor=floor,
            apt=apt,
            area=area,
            city=city,
            county=county,
            building_num=building_num,
            street=street
        )

    
    model_config = {
        "from_attributes": True
    }
    