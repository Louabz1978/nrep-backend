from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional, List
from passlib.hash import bcrypt
from enum import Enum
from app.utils.file_helper import load_sql
from sqlalchemy import text

from app import database, models
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ----- Enums & Schemas -----

class UserRole(str, Enum):
    admin = "admin"
    agent = "agent"
    buyer = "buyer"
    seller = "seller"
    broker = "broker"
    realtor = "realtor"  # added realtor

    model_config = {
        "from_attributes": True
    }

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

class AgencyOut(BaseModel):
    agency_id: int
    name: str
    phone_number: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    lic_num: Optional[str] = None
    agency: Optional[AgencyOut]
    is_active: Optional[bool]

    model_config = {
        "from_attributes": True
    }

# ----- Routes -----

@router.get("", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).options(joinedload(models.User.agency)).all()


@router.get("/{user_id}", response_model=UserOut)
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


@router.post("", status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if email exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Validate agency only if realtor
    if user.role == 'realtor':
        agency = db.query(models.Agency).filter(models.Agency.agency_id == user.agency_id).first()
        if not agency:
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

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully", "user_id": db_user.user_id}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.put("/{user_id}")
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

    # Update fields
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.email = user_data.email
    user.password_hash = bcrypt.hash(user_data.password)
    user.role = user_data.role
    user.phone_number = user_data.phone_number
    user.address = user_data.address
    user.neighborhood = user_data.neighborhood
    user.city = user_data.city
    user.county = user_data.county
    user.lic_num = user_data.lic_num
    user.agency_id = user_data.agency_id

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully", "user_id": user.user_id}






