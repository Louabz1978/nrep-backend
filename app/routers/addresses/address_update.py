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
        floor: Optional[str] = Form(None),
        apt: Optional[str] = Form(None),
        area: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        county: Optional[str] = Form(None),
        building_num: Optional[str] = Form(None),
        street: Optional[str] = Form(None)
    ):
        def to_optional_int(value):
            return int(value) if value not in (None, "", "null") else None

        def clean_str(value):
            return value if value not in (None, "", "null") else None

        return cls(
            floor=to_optional_int(floor),
            apt=to_optional_int(apt),
            area=clean_str(area),
            city=clean_str(city),
            county=clean_str(county),
            building_num=to_optional_int(building_num),
            street=clean_str(street)
        )

    
    model_config = {
        "from_attributes": True
    }