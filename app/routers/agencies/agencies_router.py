from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
from datetime import datetime, timezone

from app import database
from ...models.user_model import User
from ...models.agency_model import Agency
from app.utils.file_helper import load_sql
from ...dependencies import get_current_user
from ...utils.out_helper import build_user_out

from .agency_create import AgencyCreate
from .agency_out import AgencyOut
from app.routers.addresses.address_out import AddressOut
from .agencies_update import AgencyUpdate
from app.models.addresses_model import Address

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
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate broker_id if provided
    if agency.broker_id:
        broker = db.execute(text(role_sql), {"user_id" : agency.broker_id}).mappings().first()
        if not broker:
            raise HTTPException(status_code=400, detail="Broker not found")
        if broker["broker"] == False:
            raise HTTPException(status_code=400, detail="Assigned broker must have role 'broker'")

    db_agency = agency.model_dump()
    db_agency["created_at"] = datetime.now(timezone.utc)
    db_agency["created_by"] = current_user.user_id

    sql = load_sql("agency/create_agency.sql")
    result = db.execute(text(sql), db_agency)
    new_agency_id = result.scalar()

    db.commit()

    sql = load_sql("agency/get_agency_by_id.sql")
    created_agency = db.execute(text(sql), {"agency_id": new_agency_id}).mappings().first()
    address_data = {k[len("address_"):]: v for k, v in created_agency.items() if k.startswith("address_")}
    agency_details = AgencyOut(
        **created_agency, 
        broker=build_user_out(created_agency, "broker_"), 
        address = AddressOut(**address_data) if address_data.get("address_id") else None,)

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
    agency_data: AgencyUpdate,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    # 1) get the agency
    agency = db.query(Agency).filter(Agency.agency_id == agency_id).first()
    if not agency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found"
        )

    # 2) update agency fields if present
    if agency_data.name is not None:
        agency.name = agency_data.name
    if agency_data.email is not None:
        agency.email = agency_data.email
    if agency_data.phone_number is not None:
        agency.phone_number = agency_data.phone_number

    # 3) update or create the address if provided
    if agency_data.address:
        if agency.address:  # already exists
            agency.address.floor = agency_data.address.floor or agency.address.floor
            agency.address.apt = agency_data.address.apt or agency.address.apt
            agency.address.area = agency_data.address.area or agency.address.area
            agency.address.city = agency_data.address.city or agency.address.city
            agency.address.county = agency_data.address.county or agency.address.county
            agency.address.building_num = (
                agency_data.address.building_num or agency.address.building_num
            )
            agency.address.street = (
                agency_data.address.street or agency.address.street
            )
        else:  # no address yet → create one
            new_address = Address(
                floor=agency_data.address.floor,
                apt=agency_data.address.apt,
                area=agency_data.address.area,
                city=agency_data.address.city,
                county=agency_data.address.county,
                building_num=agency_data.address.building_num,
                street=agency_data.address.street,
                created_by=current_user.user_id,
                agency_id=agency.agency_id,
            )
            db.add(new_address)
            agency.address = new_address

    db.commit()
    db.refresh(agency)

    return {"message": "Agency updated successfully", "agency": agency}
@router.delete("/{agency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agency(
    agency_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
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
