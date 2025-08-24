from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class LicenseCreate(BaseModel):
    lic_num: int
    lic_status: str
    lic_type: str
    user_id: int
    agency_id: int

    @classmethod
    def as_form(
        cls,
        lic_num: int = Form(...),
        lic_status: str = Form(...),
        lic_type: str = Form(...),
        user_id: int = Form(...),
        agency_id: int = Form(...)
    ):
        return cls(
            lic_num=lic_num,
            lic_status=lic_status,
            lic_type=lic_type,
            user_id=user_id,
            agency_id=agency_id
        )
