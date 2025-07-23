from pydantic import BaseModel, EmailStr
from typing import List

from .roles_enum import UserRole

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str 
    role: List[UserRole]
    phone_number: str  

    model_config = {
        "from_attributes": True
    }
    