from pydantic import BaseModel

class RolesCreate(BaseModel):
    admin: bool
    broker: bool
    realtor: bool
    seller: bool
    buyer: bool
    tenant: bool