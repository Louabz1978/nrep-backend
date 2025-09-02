from pydantic import BaseModel

from typing import Optional

class LicenseOut(BaseModel):
    license_id: Optional[int]
    lic_num: Optional[int]
    lic_status: Optional[str]
    lic_type: Optional[str]
    
    user: Optional[object]
    agency: Optional[object]

    model_config = {
        "from_attributes": True
    }
