from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

from app import database
from ...models.user_model import User
from ...models.agency_model import Agency
from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .agency_create import AgencyCreate
from .agency_out import AgencyOut

router = APIRouter(
    prefix="/agencies",
    tags=["Agencies"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_agency(
    agency: AgencyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate broker_id if provided
    if agency.broker_id:
        sql = load_sql("user/get_user_by_id.sql")
        broker = db.execute(text(sql), {"user_id" : agency.broker_id}).mappings().first()
        if not broker:
            raise HTTPException(status_code=400, detail="Broker not found")
        if broker.role != "broker":
            raise HTTPException(status_code=400, detail="Assigned broker must have role 'broker'")

    db_agency = agency.model_dump()

    sql = load_sql("agency/create_agency.sql")
    result = db.execute(text(sql), db_agency)
    new_agency_id = result.scalar()

    db.commit()

    sql = load_sql("agency/get_agency_by_id.sql")
    created_agency = db.execute(text(sql), {"agency_id": new_agency_id}).mappings().first()
    agency_details = AgencyOut(**created_agency, name = created_agency["agency_name"])

    return {"message": "Agency created successfully", "agency": agency_details}

@router.get("", response_model=List[AgencyOut], status_code=status.HTTP_200_OK)
def get_all_agencies(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("agency/get_all_agencies.sql")
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
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("agency/get_agency_by_id.sql")
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

@router.put("/{agency_id}")
def update_agency(
    agency_id: int,
    agency_data: AgencyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    agency = db.query(Agency).filter(Agency.agency_id == agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    if agency_data.broker_id is not None:
        broker = db.query(User).filter(User.user_id == agency_data.broker_id).first()
        if not broker or broker.role != "broker":
            raise HTTPException(status_code=400, detail="Invalid broker_id or user is not a broker")

    sql = load_sql("agency/update_agency.sql")

    db.execute(
        text(sql),
        {
            "agency_id": agency_id,
            "name": agency_data.name,
            "email": agency_data.email,
            "phone_number": agency_data.phone_number,
            "address": agency_data.address,
            "neighborhood": agency_data.neighborhood,
            "city": agency_data.city,
            "county": agency_data.county,
            "broker_id": agency_data.broker_id,
        }
    )
    db.commit()

    return {"message": "Agency updated successfully", "agency_id": agency_id}

@router.delete("/{agency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agency(
    agency_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("agency/get_agency_by_id.sql")
    result = db.execute(text(sql), {"agency_id": agency_id})
    agency = result.mappings().first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    delete_sql = load_sql("agency/delete_agency.sql")
    db.execute(text(delete_sql), {"agency_id": agency_id})
    
    db.commit()
    return {"message": "Agency deleted successfully"}
