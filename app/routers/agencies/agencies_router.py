from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import text
from datetime import datetime, timezone

from app import database

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from ...models.user_model import User
from ...models.agency_model import Agency
from ...models.addresses_model import Address

from .agency_create import AgencyCreate
from .agencies_update import AgencyUpdate
from .agency_out import AgencyOut
from ..addresses.address_out import AddressOut
from .agency_pagination import PaginatedAgencyOut

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
    row = db.execute(text(sql), {"agency_id": new_agency_id}).mappings().first()

    created_by_data = {k.replace("created_by_", ""): v for k, v in row.items() if k.startswith("created_by")}
    broker_data = {k.replace("broker_", ""): v for k, v in row.items() if k.startswith("broker_")}
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

    agency_details = AgencyOut(
        **row,
        created_by=created_by_data,
        broker=broker_data,
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
    )

    return {"message": "Agency created successfully", "agency": agency_details}

@router.get("", response_model=PaginatedAgencyOut, status_code=status.HTTP_200_OK)
def get_all_agencies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    
    sort_by: str = Query("agency_id", regex="^(agency_id|name|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    broker_id: Optional[int] = Query(None),
    created_by: Optional[int] = Query(None),
    city: Optional[str] = None,
    
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    
    if not current_user.roles.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    params = {
        "name": f"%{name}%" if name else None,
        "email": f"%{email}%" if email else None,
        "phone_number": f"%{phone_number}%" if phone_number else None,
        "broker_id": broker_id,
        "created_by": created_by,
        "city": f"%{city}%" if city else None,
        "limit": per_page,
        "offset": (page - 1) * per_page
    }

    # total count
    total_sql = load_sql("agency/count_agencies.sql")
    total = db.execute(text(total_sql), params).scalar()
    total_pages = (total + per_page - 1) // per_page

    # load agencies
    sql = load_sql("agency/get_all_agencies.sql").format(sort_by=sort_by, sort_order=sort_order)
    result = db.execute(text(sql), params)

    agencies = []
    for row in result.mappings():
        created_by_data = {k.replace("created_by_", ""): v for k, v in row.items() if k.startswith("created_by")}
        broker_data = {k.replace("broker_", ""): v for k, v in row.items() if k.startswith("broker_")}
        address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

        agency = AgencyOut(
            **row,
            created_by=created_by_data,
            broker=broker_data,
            address=AddressOut(**address_data) if address_data.get("address_id") else None,
        )
        
        agencies.append(agency)

    return {
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "data": agencies,
    }

@router.get("/{agency_id}", response_model=AgencyOut, status_code=status.HTTP_200_OK)
def get_agency_by_id(
    agency_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(
        text(role_sql), {"user_id": current_user.user_id}
    ).mappings().first()
    if not roles or not roles.get("admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Fetch data
    sql = load_sql("agency/get_agency_by_id.sql")
    row = db.execute(text(sql), {"agency_id": agency_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    # Parse data
    created_by_data = {k.replace("created_by_", ""): v for k, v in row.items() if k.startswith("created_by")}
    broker_data = {k.replace("broker_", ""): v for k, v in row.items() if k.startswith("broker_")}
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

    # Build response
    agency = AgencyOut(
        **row,
        created_by=created_by_data,
        broker=broker_data,
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
    )
    
    return agency

@router.put("/{agency_id}")
def update_agency(
    agency_id: int,
    agency_data: AgencyUpdate,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    # Authorization
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(
        text(role_sql), {"user_id": current_user.user_id}
    ).mappings().first()
    if not roles or not roles.get("admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
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
