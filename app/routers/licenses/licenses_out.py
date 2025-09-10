from pydantic import BaseModel

from typing import Optional

from ...utils.enums import LicenseStatus, LicenseType

class LicenseOut(BaseModel):
    license_id: Optional[int]
    lic_num: Optional[int]
    lic_status: Optional[LicenseStatus]
    lic_type: Optional[LicenseType]
    
    user: Optional[object]
    agency: Optional[object]

    model_config = {
        "from_attributes": True
    }
