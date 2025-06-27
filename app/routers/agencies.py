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
        sql = load_sql("get_user_by_id.sql")
        result = db.execute(text(sql), {"user_id" : agency.broker_id})
        broker = result.mappings().first()
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

    agency_data = {
        column.name: getattr(db_agency, column.name)
        for column in db_agency.__table__.columns
        if column.name !="agency_id"
    }

    sql = load_sql("create_agency.sql")
    result = db.execute(text(sql), agency_data)
    new_agency_id = result.scalar()

    db.commit()

    return {"message": "Agency created successfully", "agency_id": new_agency_id}


@router.get("", response_model=List[AgencyOut], status_code=status.HTTP_200_OK)
def get_all_agencies(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_all_agencies.sql")
    result = db.execute(text(sql))

    agencies = []
    for row in result.mappings():
        agency = AgencyOut(
            agency_id=row["agency_id"],
            name=row["agency_name"],
            phone_number=row["agency_phone_number"],
        )
        agencies.append(agency)
    return agencies

@router.get("/{agency_id}", response_model=AgencyOut, status_code=status.HTTP_200_OK)
def get_agency_by_id(
    agency_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_agency_by_id.sql")
    result = db.execute(text(sql), {"agency_id": agency_id})
    row = result.mappings().first()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    
    agency = AgencyOut(
        agency_id=row["agency_id"],
        name=row["agency_name"],
        phone_number=row["agency_phone_number"]
    )
    return agency

@router.delete("/{agency_id}")
def delete_agency(
    agency_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_agency_by_id.sql")
    result = db.execute(text(sql), {"agency_id": agency_id})
    agency = result.mappings().first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    delete_sql = load_sql("delete_agency.sql")
    db.execute(text(delete_sql), {"agency_id": agency_id})
    
    db.commit()
    return {"message": "Agency deleted successfully"}

