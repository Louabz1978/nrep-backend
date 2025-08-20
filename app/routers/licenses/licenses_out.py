from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional

class LicenseOut(BaseModel):
    license_id: Optional[int]
    lic_num: Optional[int]
    lic_status: Optional[str]
    lic_type: Optional[str]
    user_id: Optional[int]
    agency_id: Optional[int]

    model_config = {
        "from_attributes": True
    }
