from fastapi import Form
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date

from ...utils.enums import PropertyStatus, PropertyTypes, PropertyTransactionType

from ..addresses.address_update import AddressUpdate
from ..additional.additional_update import AdditionalUpdate

class PropertyUpdate(BaseModel):
    sellers: Optional[ List[ int ] ] = None
    description: Optional[ str ] = None
    show_inst: Optional[ str ] = None
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
    trans_type: Optional[ PropertyTransactionType ] = None
    exp_date: Optional[ date ] = None
    livable: Optional[ bool ] = None
    preserve_images: Optional[ List[str] ] = None
    
    address: Optional[ AddressUpdate ] = None
    additional: Optional[ AdditionalUpdate ] = None
    
    @field_validator("sellers", mode="before")
    @classmethod
    def parse_sellers(cls, value):
        if isinstance(value, str):
            return [int(v) for v in value.split(",") if v.strip()]
        return value

    @classmethod
    def as_form(
        cls,
        sellers: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        show_inst: Optional[ str ] = Form(None),
        price: Optional[int] = Form(None),
        property_type: Optional[PropertyTypes] = Form(None),
        bedrooms: Optional[int] = Form(None),
        bathrooms: Optional[float] = Form(None),
        property_realtor_commission: Optional[float] = Form(None),
        buyer_realtor_commission: Optional[float] = Form(None),
        area_space: Optional[int] = Form(None),
        year_built: Optional[int] = Form(None),
        latitude: Optional[float] = Form(None),
        longitude: Optional[float] = Form(None),
        status: Optional[PropertyStatus] = Form(None),
        trans_type: Optional[PropertyTransactionType] = Form(None),
        exp_date: Optional[date] = Form(None),
        livable: Optional[bool] = Form(None),
        preserve_images: Optional[List[str]] = Form(None)
    ):

        return cls(
            sellers=sellers,
            description=description,
            show_inst=show_inst,
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
            trans_type=trans_type,
            exp_date=exp_date,
            livable=livable,
            preserve_images=preserve_images if preserve_images not in (None, "") else None
        )

    # @model_validator(mode='before')
    # def validate_roles(cls, values):
    #     owner_id = values.get('owner_id')
    #     # Treat 0 as no owner_id provided
    #     if owner_id == 0:
    #         owner_id = None
    #         values['owner_id'] = None
        
    #     return values
