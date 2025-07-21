from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database
from .address_create import AddressCreate
from .address_out import AddressOut
from .address_update import AddressUpdate
from app.models.user_model import User
from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

router = APIRouter(
    prefix="/address",
    tags=["addresses"]
)

@router.put("/address")
def update_address(
    address : AddressUpdate,
    db : Session = Depends(database.get_db),
    current_user : User = Depends(get_current_user)
):
    sql = load_sql("user/get_user_by_id.sql")
    user_data = db.execute(text(sql), {"user_id": current_user.user_id}).mappings().first()

    if not user_data:
        raise HTTPException(status_code=404, detail="user not found")
    
    get_sql = load_sql("address/get_address_by_id.sql")
    address_data = db.execute(text(get_sql), {"address_id":user_data["address_id"]}).mappings().first()

    if not address_data:
        raise HTTPException(status_code=404, detail="address not found")
    
    #update address
    db_address = address.model_dump(exclude_unset=True)
    db_address["address_id"] = user_data["address_id"]
    set_clause = ", ".join(f"{k} = :{k}" for k in db_address)
    sql = f"UPDATE ADDRESSES SET {set_clause} WHERE address_id = :address_id RETURNING address_id;"
    updated_address_id = db.execute(text(sql), db_address).scalar()
    db.commit()

    #fetch address data
    updated_address = db.execute(text(get_sql),{"address_id":updated_address_id}).mappings().first()
    address_details = AddressOut(**updated_address)

    return {"message" : "address updated successfully", "address" : address_details}


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

@router.get("/{address_id}", status_code=status.HTTP_200_OK)
def get_address_by_id(
    address_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("address/get_address_by_id.sql")
    result = db.execute(text(sql), {'address_id': address_id})
    row = result.mappings().first()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    address = AddressOut(**row)
    return address