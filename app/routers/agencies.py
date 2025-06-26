from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional, List
from passlib.hash import bcrypt
from enum import Enum

from app import database, models
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/agencies",
    tags=["Agencies"]
)


class AgencyOut(BaseModel):
    agency_id: int
    name: str
    phone_number: Optional[str] = None

    model_config = {
        "from_attributes": True
    }



class AgencyCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    broker_id: Optional[int] = Field(
        None,
        description="Optional broker user_id to assign as agency broker"
    )

    @model_validator(mode='before')
    def validate_broker(cls, values):
        broker_id = values.get("broker_id")
        if broker_id == 0:
            values["broker_id"] = None
        return values


@router.post("", status_code=201)
def create_agency(
    agency: AgencyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate broker_id if provided
    if agency.broker_id:
        broker = db.query(models.User).filter(models.User.user_id == agency.broker_id).first()
        if not broker:
            raise HTTPException(status_code=400, detail="Broker not found")
        if broker.role != "broker":
            raise HTTPException(status_code=400, detail="Assigned broker must have role 'broker'")

    db_agency = models.Agency(
        name=agency.name,
        email=agency.email,
        phone_number=agency.phone_number,
        address=agency.address,
        neighborhood=agency.neighborhood,
        city=agency.city,
        county=agency.county,
        broker_id=agency.broker_id,
    )

    db.add(db_agency)
    db.commit()
    db.refresh(db_agency)

    return {"message": "Agency created successfully", "agency_id": db_agency.agency_id}

@router.get("", response_model=List[AgencyOut])
def get_all_agencies(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(models.Agency).all()


