from pydantic import BaseModel
from typing import List

class RoleOut(BaseModel):
    admin: bool = False
    broker: bool = False
    realtor: bool = False
    buyer: bool = False
    seller: bool = False
    tenant: bool = False

    @property
    def roles(self) -> List[str]:
        return [key for key,value in self.model_dump().items() if value]