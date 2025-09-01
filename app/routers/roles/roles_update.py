from pydantic import BaseModel
from typing import Optional

class RolesUpdate(BaseModel):
    admin: Optional[bool] = None
    broker: Optional[bool] = None
    realtor: Optional[bool] = None
    seller: Optional[bool] = None
    buyer: Optional[bool] = None
    tenant: Optional[bool] = None