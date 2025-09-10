from pydantic import BaseModel, Field
from fastapi import Form

from ...utils.enums import LicenseStatus, LicenseType

class LicenseCreate(BaseModel):
    lic_status: LicenseStatus
    lic_type: LicenseType
    user_id: int = Field(..., gt=0)
    agency_id: int = Field(..., gt=0)

    @classmethod
    def as_form(
        cls,
        lic_status: LicenseStatus = Form(...),
        lic_type: LicenseType = Form(...),
        user_id: int = Form(...),
        agency_id: int = Form(...)
    ):
        return cls(
            lic_status=lic_status,
            lic_type=lic_type,
            user_id=user_id,
            agency_id=agency_id
        )
