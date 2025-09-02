from pydantic import BaseModel, Field, StringConstraints, field_validator
from fastapi import Form
from typing import Annotated
import re

building_num_pattern = re.compile(r'^\d{7,15}$')
class AddressCreate(BaseModel):
    floor: int = Field(..., ge=0, le=200, description= "Floor must be >= 0 and <= 200")
    apt: int = Field(..., gt=0, le=100, description="apartment must be > 0 and <= 100")
    area: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2)
    ]
    city: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2)
    ]
    county: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=150)
    ]
    building_num: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=20)
    ]
    street: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=150)
    ]

    @classmethod
    def as_form(
        cls,
        floor: int = Form(...),
        apt: int = Form(...),
        area: str = Form(...),
        city: str = Form(...),
        county: str = Form(...),
        building_num: str = Form(...),
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

    @field_validator("building_num")
    def validate_building_num(cls, v: str) -> str:
        if not building_num_pattern.match(v):
            raise ValueError("Building number must be only digits")
        return v
