from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime ,timezone

from app import database

from .address_out2 import AddressOut2
from typing import List
from app.routers.users.user_out import UserOut


from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from app.models.user_model import User

from .address_out import AddressOut

from .address_create import AddressCreate
from .address_update import AddressUpdate

router = APIRouter(
    prefix="/address",
    tags=["addresses"]
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
def get_user_address(
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

@router.get("/{address_id:int}", status_code=status.HTTP_200_OK)
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

@router.get("/all", response_model=List[AddressOut2], status_code=status.HTTP_200_OK)
def get_all_addresses(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
  
    if current_user.roles.admin is False :
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("address/get_all_addresses.sql")
    result = db.execute(text(sql)).mappings().all()
    addresses = []
    for row in result:
        # نفصل بيانات اليوزر يلي أنشأ الادريس
        created_by_user_data = {
            key.replace("created_by_user_", ""): value
            for key, value in row.items()
            if key.startswith("created_by_user_")
        }

        # نبني الكائن
        roles = [role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"] if created_by_user_data.get(role)]
        created_by_user_data["role"] = roles
        created_by_user = UserOut(**created_by_user_data)

        # نفصل باقي البيانات تبع الادريس
        address_data = {
            k: v for k, v in row.items()
            if not k.startswith("created_by_user_")
        }

        # نضيف created_by_user للديكشنري
        address_data["created_by_user"] = created_by_user

        # نعمل كائن AddressOut2
        addr = AddressOut2(**address_data)
        addresses.append(addr)

    return addresses

@router.put("")
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

@router.put("/{address_id}")
def update_address_by_id(
    address_id: int,
    address: AddressUpdate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    
    #get address and created_by_user data
    get_sql = load_sql("address/get_address_by_id.sql")
    address_data = db.execute(text(get_sql), {"address_id": address_id}).mappings().first()
    sql = load_sql("user/get_user_by_id.sql")
    created_by_user = db.execute(text(sql), {"user_id": address_data["created_by"]}).mappings().first()

    if not address_data:
        raise HTTPException(status_code=404, detail="address not found")
    if not created_by_user:
        raise HTTPException(status_code=404, detail="creator not found")
    
    #Authorization
    sql = load_sql("role/get_user_roles.sql")
    user_roles = db.execute(text(sql), {"user_id": current_user.user_id}).mappings().first()
    if not (
        user_roles["admin"] == True
        or (user_roles["broker"] == True and current_user.user_id in (address_data["created_by"], created_by_user["created_by"]))
        or (user_roles["realtor"] == True and current_user.user_id == address_data["created_by"])
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_address = address.model_dump(exclude_unset=True)
    db_address["address_id"] = address_id
    set_clause = ", ".join(f"{k} = :{k}" for k in db_address)
    sql = f"UPDATE ADDRESSES SET {set_clause} WHERE address_id = :address_id RETURNING address_id;"
    updated_address_id = db.execute(text(sql), db_address).scalar()
    db.commit() 

    #fetch address data
    updated_address = db.execute(text(get_sql),{"address_id":updated_address_id}).mappings().first()
    address_details = AddressOut(**updated_address)

    return {"message" : "address updated successfully", "address" : address_details}

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("address/get_address_by_id.sql")
    address = db.execute(text(sql), {"address_id": address_id}).mappings().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    delete_sql = load_sql("address/delete_address.sql")
    db.execute(text(delete_sql), {"address_id": address_id})
    
    db.commit()
    return {"message": "Address deleted successfully"}
