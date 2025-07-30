from pydantic import BaseModel, model_validator
from typing import Optional
from fastapi import Form
from .properties_type_enum import PropertyTypes
from .properties_status_enum import PropertyStatus

class PropertyCreate(BaseModel):
    owner_id: int
    description: str
    price: int
    property_type: Optional[ PropertyTypes ] = None
    bedrooms: int
    bathrooms: float
    property_realtor_commission: float
    buyer_realtor_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: PropertyStatus

    @classmethod
    def as_form(
        cls,
        owner_id: int = Form(...),
        description: str = Form(...),
        price: int = Form(...),
        property_type: Optional[ PropertyTypes ] = Form(...),
        bedrooms: int = Form(...),
        bathrooms: float = Form(...),
        property_realtor_commission: float = Form(...),
        buyer_realtor_commission: float = Form(...),
        area_space: int = Form(...),
        year_built: int = Form(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
        status: PropertyStatus = Form(...)
    ):
        return cls(
            owner_id = owner_id,
            description = description,
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
            status = status
        )
    
    @model_validator(mode='before')
    def validate_roles(cls, values):
        owner_id = values.get('owner_id')
        # Treat 0 as no seller_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        #seller_id is required
        if not owner_id:
            raise ValueError("owner_id is required")

        return values
    

