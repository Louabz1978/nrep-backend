from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from ...models.user_model import User

from ..addresses.address_out import AddressOut

from ..addresses.address_create import AddressCreate


router = APIRouter(
    prefix="/address",
    tags=["Adresses"]
)

@router.post("", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
def create_address(
    address: AddressCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]

    if "realtor" in current_user_role or "broker" in current_user_role or "admin" in current_user_role:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    address_data = address.model_dump()
    address_data["created_by"] = current_user.user_id
    address_data["created_at"] = datetime.now(timezone.utc)

    address_sql = load_sql("address/create_address.sql")
    address_result = db.execute(text(address_sql), address_data)
    new_address_id = address_result.scalar()

    db.commit()

    sql = load_sql("address/get_address.sql")
    created_address = db.execute(text(sql), {"address_id": new_address_id}).mappings().first()
    
    address_out_data = dict(created_address)
    address_out_data["created_by"] = current_user.user_id

    address_details = AddressOut(**address_out_data)

    return address_details

@router.get("", status_code=status.HTTP_200_OK)
def get_address(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("address/get_address.sql")
    result = db.execute(text(sql), {'address_id': current_user.address_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    address = AddressOut(**row)
    return address