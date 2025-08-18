from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class LicenseUpdate(BaseModel):
    lic_num: Optional[int]
    lic_status: Optional[str]
    lic_type: Optional[str]
    agency_id: Optional[int]

    @classmethod
    def as_form(
        cls,
        lic_num: Optional[int] = Form(None),
        lic_status: Optional[str] = Form(None),
        lic_type: Optional[str] = Form(None),
        agency_id: Optional[int] = Form(None)
    ):
        return cls(
            lic_num=lic_num,
            lic_status=lic_status,
            lic_type=lic_type,
            agency_id=agency_id
        )
