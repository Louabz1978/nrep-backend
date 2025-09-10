from pydantic import BaseModel, Field
from fastapi import Form
from typing import Optional

from ...utils.enums import LicenseStatus, LicenseType

class LicenseUpdate(BaseModel):
    lic_status: Optional[LicenseStatus] = None
    lic_type: Optional[LicenseType] = None
    user_id: Optional[int] = Field(None, ge=0)
    agency_id: Optional[int] = Field(None, ge=0)

    @classmethod
    def as_form(
        cls,
        lic_status: Optional[LicenseStatus] = Form(None),
        lic_type: Optional[LicenseType] = Form(None),
        user_id: Optional[int] = Form(None),
        agency_id: Optional[int] = Form(None)
    ):
        return cls(
            lic_status=lic_status,
            lic_type=lic_type,
            user_id=user_id,
            agency_id=agency_id
        )
