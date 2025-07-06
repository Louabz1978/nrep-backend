from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database, models
from app.utils.file_helper import load_sql

from ...dependencies import get_current_user

from .user_out import UserOut
from ..agencies.agency_out import AgencyOut

from .user_create import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if email exists
    result = db.execute(text('SELECT 1 FROM USERS WHERE email = :email'), {"email": user.email})
    row = result.mappings().first()
    if row:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Validate agency only if realtor
    if user.role == 'realtor':
        sql = load_sql("get_agency_by_id.sql")
        result = db.execute(text(sql), {"agency_id": user.agency_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=400, detail="Invalid agency_id")

    hashed_password = bcrypt.hash(user.password)

    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        phone_number=user.phone_number,
        address=user.address,
        neighborhood=user.neighborhood,
        city=user.city,
        county=user.county,
        lic_num=user.lic_num,
        agency_id=user.agency_id,
        is_active=True
    )

    user_data = {
        column.name: getattr(db_user, column.name)
        for column in db_user.__table__.columns
        if column.name !="user_id"
    }

    sql = load_sql("create_user.sql")
    result = db.execute(text(sql), user_data)
    new_user_id = result.scalar()

    db.commit()

    return {"message": "User created successfully", "user_id": new_user_id}

@router.get("", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
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
            user_id=row["user_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            role=row["role"],
            phone_number=row["phone_number"],
            address=row["address"],
            neighborhood=row["neighborhood"],
            city=row["city"],
            county=row["county"],
            lic_num=row["lic_num"],
            agency=agency,
            is_active=row["is_active"],
        )
        users.append(user)
    return users

@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
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
        user_id=row["user_id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        role=row["role"],
        phone_number=row["phone_number"],
        address=row["address"],
        neighborhood=row["neighborhood"],
        city=row["city"],
        county=row["county"],
        lic_num=row["lic_num"],
        agency=agency,
        is_active=row["is_active"],
    )

    return user

@router.put("/{user_id}",status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate agency_id existence if provided
    if user_data.agency_id is not None:
        agency = db.query(models.Agency).filter(models.Agency.agency_id == user_data.agency_id).first()
        if not agency:
            raise HTTPException(status_code=400, detail="Invalid agency_id")

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
            "neighborhood": user_data.neighborhood,
            "city": user_data.city,
            "county": user_data.county,
            "lic_num": user_data.lic_num,
            "agency_id": user_data.agency_id,
        }
    )

    db.commit()
    
    return {"message": "User updated successfully", "user_id": user.user_id}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
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
