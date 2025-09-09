from pydantic import BaseModel, Field, field_validator
from fastapi import Form
from typing import Dict, Any
from .license_type_enum import LicenseType
from .license_status_enum import LicenseStatus
class LicenseCreate(BaseModel):
    lic_status: Dict[str, Any]
    lic_type: Dict[str, Any]
    user_id: int = Field(..., gt=0)
    agency_id: int = Field(..., gt=0)

    @classmethod
    def as_form(
        cls,
        lic_status: str = Form(...),
        lic_type: str = Form(...),
        user_id: int = Form(...),
        agency_id: int = Form(...)
    ):
        return cls(
            lic_status=lic_status,
            lic_type=lic_type,
            user_id=user_id,
            agency_id=agency_id
        )

    @field_validator("lic_status")
    def validate_staus(cls, value):
        LicenseStatus.validate_dict(value)
        return value
    
    @field_validator("lic_type")
    def validate_type(cls, value):
        LicenseType.validate_dict(value)
        return value