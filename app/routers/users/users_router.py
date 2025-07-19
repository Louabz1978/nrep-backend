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
from .user_out import UserRole

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
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
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
    raw_sql = load_sql("user/create_user.sql")
    sql = raw_sql.format(role_columns = role_columns, role_placeholders = role_placeholders)
    new_user_id = db.execute(text(sql), params).scalar()
    db.commit()

    #fetch user data
    sql = load_sql("user/get_user_by_id.sql")
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
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False and roles["broker"] == False and roles["realtor"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    if roles["admin"] == True:
        role = 'admin'
    elif roles["broker"] == True:
        role = 'broker'
    else:
        role = 'realtor'
    
    sql = load_sql("user/get_all_users.sql")
    result = db.execute(text(sql), {"user_id": current_user.user_id, "role": role})

    users = []
    for row in result.mappings():
        roles = [role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"] if row.get(role)]
        user = UserOut(**row, role=roles)
        users.append(user)
    return users

@router.get("/", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_details(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("user/get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": current_user.user_id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    roles = [role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"] if row.get(role)]

    user = UserOut(
        **row,
        role=roles
    )

    return user

@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("user/get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": user_id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    target_user_creator_id = row["created_by"]

    if current_user.roles.admin:
        pass  # admin can access any user

    elif current_user.user_id == user_id:
        pass  # user can access their own data

    elif current_user.roles.broker:
        if target_user_creator_id == current_user.user_id:
            pass # broker can access users he created
        else:
            # broker can access the users that the realtor that her created created
            realtor_ids = db.execute(
                text(
                    "SELECT user_id FROM users WHERE created_by = :broker_id AND role_id IN (SELECT roles_id FROM roles WHERE realtor = TRUE)"
                ),
                {"broker_id": current_user.user_id}
            ).scalars().all()

            if target_user_creator_id not in realtor_ids:
                raise HTTPException(status_code=403, detail="Not authorized to view this user")

    elif current_user.roles.realtor:
        if target_user_creator_id == current_user.user_id:
            pass # realtors can access users that they created
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view this user")

    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")

    roles = [role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"] if row.get(role)]

    user = UserOut(
        **row,
        role=roles
    )

    return user

@router.put("/{user_id}",status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if current_user_roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email exists
    result = db.execute(text('SELECT 1 FROM USERS WHERE email = :email'), {"email": user.email}).mappings().first()
    if user.email != user_data.email and result:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    sql = load_sql("user/update_user.sql")

    db.execute(
        text(sql),
        {
            "user_id": user_id,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "password_hash": bcrypt.hash(user_data.password),
            "phone_number": user_data.phone_number
        }
    )

    db.commit()
    
    return {"message": "User updated successfully", "user_id": user.user_id}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if current_user_roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("user/get_user_by_id.sql")
    user = db.execute(text(sql), {"user_id": user_id}).mappings().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_sql = load_sql("user/delete_user.sql")
    db.execute(text(delete_sql), {"user_id": user_id})
    
    db.commit()
    return {"message": "User deleted successfully"}
