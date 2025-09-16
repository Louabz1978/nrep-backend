from pydantic import BaseModel, field_validator
from typing import Optional, List
from fastapi import Form
from datetime import date

from ...utils.enums import PropertyStatus, PropertyTypes, PropertyTransactionType

class PropertyCreate(BaseModel):
    sellers: List[int]
    description: str
    show_inst: str
    price: int
    property_type: PropertyTypes
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: PropertyStatus
    trans_type: PropertyTransactionType
    exp_date: date
    livable: Optional[bool]

    @field_validator("sellers", mode="before")
    @classmethod
    def parse_sellers(cls, value):
        if isinstance(value, str):
            return [int(v) for v in value.split(",") if v.strip()]
        return value
    
    @classmethod
    def as_form(
        cls,
        sellers: str = Form(...),
        description: str = Form(...),
        show_inst: str = Form(...),
        price: int = Form(...),
        property_type: PropertyTypes = Form(...),
        bedrooms: int = Form(...),
        bathrooms: float = Form(...),
        property_realtor_commission: float = Form(...),
        buyer_realtor_commission: float = Form(...),
        area_space: int = Form(...),
        year_built: int = Form(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
        status: PropertyStatus = Form(...),
        trans_type: PropertyTransactionType = Form(...),
        exp_date: date = Form(...),
        livable: Optional[bool] = Form(None)
    ):
        return cls(
            sellers = sellers,
            description = description,
            show_inst = show_inst,
            price = price,
            property_type = property_type,
            bedrooms = bedrooms,
            bathrooms = bathrooms,
            property_realtor_commission = property_realtor_commission,
            buyer_realtor_commission = buyer_realtor_commission,
            area_space = area_space,
            year_built = year_built,
            latitude = latitude,
            longitude = longitude,
            status = status,
            trans_type = trans_type,
            exp_date = exp_date, 
            livable = livable
        )
    
    # @model_validator(mode='before')
    # def validate_roles(cls, values):
    #     owner_id = values.get('owner_id')
    #     # Treat 0 as no seller_id provided
    #     if owner_id == 0:
    #         owner_id = None
    #         values['owner_id'] = None
    #     #seller_id is required
    #     if not owner_id:
    #         raise ValueError("owner_id is required")

    #     return values
