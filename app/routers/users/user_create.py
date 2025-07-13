from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional

from .roles_enum import UserRole

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str 
    role: UserRole
    phone_number: str  
    address_id: int 
    created_by: int  

    agency_id: Optional[int] = Field(None,nullable=True,description="Required only for realtor role",example=None,)
    lic_num: Optional[str] = Field(None,description="Required for broker and realtor roles",example=None,)

    @model_validator(mode='before')
    def validate_roles_and_fields(cls, values):
        role = values.get('role')
        agency_id = values.get('agency_id')
        lic_num = values.get('lic_num')

        # Treat 0 as no agency_id provided
        if agency_id == 0:
            agency_id = None
            values['agency_id'] = None

        # realtor: needs agency_id
        if role == 'realtor':
            if not agency_id:
                raise ValueError("agency_id is required for realtor role")
        else:
            if agency_id is not None:
                raise ValueError("agency_id should not be provided for roles other than realtor")

        # broker and realtor: need lic_num
        if role in ('broker', 'realtor'):
            if not lic_num:
                raise ValueError("lic_num is required for broker and realtor roles")
        else:
            if lic_num:
                raise ValueError("lic_num should not be provided for roles other than broker and realtor")

        return values

    model_config = {
        "from_attributes": True
    }
    