from pydantic import BaseModel

class RolesOut(BaseModel):
    role_id: int
    admin: bool
    broker: bool
    realtor: bool
    seller: bool
    buyer: bool
    tenant: bool