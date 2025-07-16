from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database
from ...models.user_model import User
from ...models.agency_model import Agency
from app.utils.file_helper import load_sql

from ...dependencies import get_current_user

from .user_out import UserOut
from ..agencies.agency_out import AgencyOut
from ..roles.roles_out import RoleOut
from ..addresses.address_out import AddressOut

from .user_create import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    #authorization check
    current_user_roles = db.execute(text("select * from roles where roles_id = :roles_id;"),{"roles_id": current_user.role_id}).mappings().first()
    current_user_role = [key for key,value in current_user_roles.items() if value]
    user_roles = set(user.role)
    if not (
        "admin" in current_user_role
        or ("broker" in current_user_role and user_roles.issubset({"realtor","buyer","seller","tenant"}))
        or ("realtor" in current_user_role and user_roles.issubset({"buyer","seller","tenant"}))
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if email exists
    result = db.execute(text('SELECT 1 FROM USERS WHERE email = :email'), {"email": user.email}).mappings().first()
    if result:
        raise HTTPException(status_code=400, detail="Email already exists")

    #prepare role insert
    true_roles = {role.value: True for role in user.role}
    role_columns = ", ".join(true_roles.keys())
    role_placeholders = ", ".join([f":{key}" for key in true_roles])

    #prepare user insert
    hashed_password = bcrypt.hash(user.password)
    db_user = user.model_dump(exclude={"password", "role"})
    db_user["password_hash"] = hashed_password
    db_user["created_by"] = current_user.user_id
    params = {**db_user, **true_roles}

    #insert user
    raw_sql = load_sql("create_user.sql")
    sql = raw_sql.format(role_columns = role_columns, role_placeholders = role_placeholders)
    new_user_id = db.execute(text(sql), params).scalar()
    db.commit()

    #fetch user data
    sql = load_sql("get_user_by_id.sql")
    created_user = db.execute(text(sql), {"user_id": new_user_id}).mappings().first()
    role_fields = ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
    roles = [role for role in role_fields if created_user[role]]
    user_details = UserOut(**created_user, role= roles, address=None)

    return {"message": "User created successfully", "user": user_details}

@router.get("", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_all_users.sql")
    result = db.execute(text(sql))

    users = []
    for row in result.mappings():
        agency = None
        if row["agency_id"]:
            agency = AgencyOut(
                agency_id=row["agency_id"],
                name=row["agency_name"],
                phone_number=row["agency_phone_number"],
            )
        user = UserOut(
            **row,
            agency=agency
        )
        users.append(user)
    return users

@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": user_id})
    row = result.mappings().first()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    agency = None
    if row["agency_id"]:
        agency = AgencyOut(
            agency_id=row["agency_id"],
            name=row["agency_name"],
            phone_number=row["agency_phone_number"],
        )

    user = UserOut(
        **row,
        agency=agency
    )

    return user

@router.put("/{user_id}",status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": user_id})
    user = result.mappings().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
  
    valid=False
    result = db.execute(text(sql), {"user_id": user["created_by"]})
    creator = result.mappings().first()
    if current_user.role == "admin"  : 
        valid=True

    elif current_user.role =="realtor" :
        if current_user.user_id == creator["user_id"] : 
            valid= True
     
    elif current_user.role == "broker" :
          if current_user.user_id == creator["user_id"] or current_user.user_id==creator["created_by"]: 
            valid= True
        
          
        
    if not valid :
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("update_user.sql")

    db.execute(
        text(sql),
        {
            "user_id": user_id,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "password_hash": bcrypt.hash(user_data.password),
            "role": user_data.role,
            "phone_number": user_data.phone_number,
            "address": user_data.address,
        }
    )

    db.commit()
    
    return {"message": "User updated successfully", "user_id": user_id}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": user_id})
    user = result.mappings().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_sql = load_sql("delete_user.sql")
    db.execute(text(delete_sql), {"user_id": user_id})
    
    db.commit()
    return {"message": "User deleted successfully"}
