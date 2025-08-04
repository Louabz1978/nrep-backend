from fastapi import Form
from pydantic import BaseModel, model_validator
from typing import Optional, List
from .properties_type_enum import PropertyTypes
from .properties_status_enum import PropertyStatus

from ..addresses.address_update import AddressUpdate
from ..additional.additional_update import AdditionalUpdate

class PropertyUpdate(BaseModel):
    owner_id: Optional[ int ] = None
    description: Optional[ str ] = None
    price: Optional[ int ] = None
    property_type: Optional[ PropertyTypes ] = None
    bedrooms: Optional[ int ] = None
    bathrooms: Optional[ float ] = None
    property_realtor_commission: Optional[ float ] = None
    buyer_realtor_commission: Optional[ float ] = None
    area_space: Optional[ int ] = None
    year_built: Optional[ int ] = None
    latitude: Optional[ float ] = None
    longitude: Optional[ float ] = None
    status: Optional[ PropertyStatus ] = None
    images_urls: Optional[List[str]] = None
    
    address: Optional[ AddressUpdate ] = None
    additional: Optional[ AdditionalUpdate ] = None

    @classmethod
    def as_form(
        cls,
        owner_id: Optional[int] = Form(None),
        description: Optional[str] = Form(None),
        price: Optional[int] = Form(None),
        property_type: Optional[PropertyTypes] = Form(None),
        bedrooms: Optional[int] = Form(None),
        bathrooms: Optional[float] = Form(None),
        property_realtor_commission: Optional[float] = Form(None),
        buyer_realtor_commission: Optional[float] = Form(None),
        area_space: Optional[int] = Form(None),
        year_built: Optional[int] = Form(None),
        latitude: Optional[int] = Form(None),
        longitude: Optional[int] = Form(None),
        status: Optional[PropertyStatus] = Form(None),
        images_urls: Optional[List[str]] = Form(None),
    ):

        return cls(
            owner_id=owner_id,
            description=description,
            price=price,
            property_type=property_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            property_realtor_commission=property_realtor_commission,
            buyer_realtor_commission=buyer_realtor_commission,
            area_space=area_space,
            year_built=year_built,
            latitude=latitude,
            longitude=longitude,
            status=status,
            images_urls=images_urls if images_urls not in (None, "") else None,
        )

    @model_validator(mode='before')
    def validate_roles(cls, values):
        owner_id = values.get('owner_id')
        # Treat 0 as no owner_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        
        return values
