from pydantic import BaseModel

from typing import Optional, Dict, Any

class LicenseOut(BaseModel):
    license_id: Optional[int]
    lic_num: Optional[str]
    lic_status: Optional[Dict[str, Any]]
    lic_type: Optional[Dict[str, Any]]
    
    user: Optional[object]
    agency: Optional[object]

    model_config = {
        "from_attributes": True
    }
