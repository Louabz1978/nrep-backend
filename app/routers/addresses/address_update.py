from fastapi import Form
from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated

class AddressUpdate(BaseModel):
    floor: Optional[int] = Field(None, ge=0, le=200, description= "Floor must be >= 0 and <= 200")
    apt: Optional[int] = Field(None, gt=0, le=100, description="apartment must be > 0 and <= 100")
    area: Annotated[
        Optional[str],
        Field(None),
        StringConstraints(strip_whitespace=True, min_length=2)
    ]
    city: Annotated[
        Optional[str],
        Field(None),
        StringConstraints(strip_whitespace=True, min_length=2)
    ]
    county: Annotated[
        Optional[str],
        Field(None),
        StringConstraints(strip_whitespace=True, min_length=2, max_length=150)
    ]
    building_num: Annotated[
        Optional[str],
        Field(None),
        StringConstraints(strip_whitespace=True, min_length=2, max_length=20)
    ]
    street: Annotated[
        Optional[str],
        Field(None),
        StringConstraints(strip_whitespace=True, min_length=2, max_length=150)
    ]

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
    