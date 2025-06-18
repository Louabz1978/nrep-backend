from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session , joinedload
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from passlib.hash import bcrypt
from enum import Enum
from app import database,models
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



class UserRole(str, Enum):
    admin = "admin"
    agent = "agent"
    buyer = "buyer"
    seller = "seller"
    broker="broker"

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
    agency_id: Optional[int] = None
    lic_num: Optional[str] = None

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
    lic_num: Optional[str] = None
    agency_id: Optional[int] = None
    agency: Optional[AgencyOut]
    is_active: Optional[bool]

    model_config = {
        "from_attributes": True
    }
    


# GET /users – Admins only
@router.get("", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).options(joinedload(models.User.agency)).all()



# POST /users – Admins only
@router.post("", status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = bcrypt.hash(user.password)

    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        phone_number=user.phone_number,
        address=user.address,
        lic_num=user.lic_num,
        agency_id=user.agency_id,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully", "user_id": db_user.user_id}

from fastapi import Path

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
    return {"message": "User deleted"}

@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash password if it's being updated
    user.password_hash = bcrypt.hash(user_data.password)
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.email = user_data.email
    user.phone_number = user_data.phone_number
    user.address= user_data.address
    user.lic_num = user_data.lic_num
    user.agency_id = user_data.agency_id
    user.role = user_data.role

    db.commit()
    db.refresh(user)
    return {"message": "User updated", "user_id": user.user_id}

@router.get("/agencies/{agency_lic}")
def get_agency_id_by_name(
    agency_lic: str = Path(..., description="Agency's Lic#"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized")
    
    agency = db.query(models.Agency).filter(models.Agency.agency_lic == agency_lic).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    return {"agency_id": agency.agency_id, "agency_name":agency.name}
