from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional

from .roles_enum import UserRole

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: UserRole
    phone_number: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
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

        # agency_id only for realtor
        if role == 'realtor':
            if not agency_id:
                raise ValueError("agency_id is required for realtor role and cannot be 0 or None")
        else:
            if agency_id is not None:
                raise ValueError("agency_id should NOT be provided for roles other than realtor")

        # lic_num required for broker and realtor
        if role in ('broker', 'realtor'):
            if not lic_num:
                raise ValueError("lic_num is required for broker and realtor roles")
        else:
            # lic_num should not be provided for others
            if lic_num:
                raise ValueError("lic_num should NOT be provided for roles other than broker and realtor")

        return values


    model_config = {
        "from_attributes": True
    }
