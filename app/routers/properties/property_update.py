from fastapi import Form
from pydantic import BaseModel, model_validator
from typing import Optional
from .properties_type_enum import PropertyTypes
from .properties_status_enum import PropertyStatus

from ..addresses.address_update import AddressUpdate

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
    images_urls: Optional[ str ] = None
    address: Optional[ AddressUpdate ] = None
    mls_num : Optional[ int ] = None

    @classmethod
    def as_form(
        cls,
        owner_id: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        price: Optional[str] = Form(None),
        property_type: Optional[str] = Form(None),
        bedrooms: Optional[str] = Form(None),
        bathrooms: Optional[str] = Form(None),
        property_realtor_commission: Optional[str] = Form(None),
        buyer_realtor_commission: Optional[str] = Form(None),
        area_space: Optional[str] = Form(None),
        year_built: Optional[str] = Form(None),
        latitude: Optional[str] = Form(None),
        longitude: Optional[str] = Form(None),
        status: Optional[str] = Form(None),
        images_urls: Optional[str] = Form(None),
        mls_num: Optional[str] = Form(None)
    ):
        def to_optional_int(value):
            return int(value) if value not in (None, "", "null") else None

        def to_optional_float(value):
            return float(value) if value not in (None, "", "null") else None

        def to_optional_enum(enum_class, value):
            return enum_class(value) if value not in (None, "", "null") else None

        return cls(
            owner_id=to_optional_int(owner_id),
            description=description if description not in (None, "") else None,
            price=to_optional_int(price),
            property_type=to_optional_enum(PropertyTypes, property_type),
            bedrooms=to_optional_int(bedrooms),
            bathrooms=to_optional_float(bathrooms),
            property_realtor_commission=to_optional_float(property_realtor_commission),
            buyer_realtor_commission=to_optional_float(buyer_realtor_commission),
            area_space=to_optional_int(area_space),
            year_built=to_optional_int(year_built),
            latitude=to_optional_float(latitude),
            longitude=to_optional_float(longitude),
            status=to_optional_enum(PropertyStatus, status),
            images_urls=images_urls if images_urls not in (None, "") else None,
            mls_num=to_optional_int(mls_num)
        )

    @model_validator(mode='before')
    def validate_roles(cls, values):
        owner_id = values.get('owner_id')
        # Treat 0 as no owner_id provided
        if owner_id == 0:
            owner_id = None
            values['owner_id'] = None
        
        return values
