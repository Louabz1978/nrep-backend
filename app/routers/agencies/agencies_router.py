from fastapi import APIRouter, Depends, HTTPException, status ,Query
from sqlalchemy.orm import Session
from typing import List , Optional
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
from .agency_pagination import PaginatedAgencyOut
from app.routers.users.user_out import UserOut

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
    total_sql = """
    SELECT COUNT(*)
    FROM agencies a
    LEFT JOIN addresses addr ON addr.agency_id = a.agency_id
    WHERE (:name IS NULL OR a.name ILIKE :name)
        AND (:email IS NULL OR a.email ILIKE :email)
        AND (:phone_number IS NULL OR a.phone_number ILIKE :phone_number)
        AND (:broker_id IS NULL OR a.broker_id = :broker_id)
        AND (:created_by IS NULL OR a.created_by = :created_by)
        AND (:city IS NULL OR addr.city ILIKE :city)
    """
    total = db.execute(text(total_sql), params).scalar()
    total_pages = (total + per_page - 1) // per_page

    # load agencies
    sql = load_sql("agency/get_all_agencies.sql").format(sort_by=sort_by, sort_order=sort_order)
    result = db.execute(text(sql), params)

    agencies = []
    for row in result.mappings():
        broker_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"broker_{role}") is True
        ]
            
        broker_data = UserOut(
            user_id=row["broker_id"],
            first_name=row["broker_first_name"],
            last_name=row["broker_last_name"],
            email=row["broker_email"],
            phone_number=row["broker_phone_number"],
            roles=broker_roles,
            created_by=row["broker_created_by"],
            created_at=row["broker_created_at"]
        )

        created_by_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"created_by_{role}") is True
        ]

        created_by = UserOut(
            user_id=row["created_by_user_id"],
            first_name=row["created_by_first_name"],
            last_name=row["created_by_last_name"],
            email=row["created_by_email"],
            phone_number=row["created_by_phone_number"],
            roles=created_by_roles,
            created_by=row["created_by_created_by"], 
            created_at=row["created_by_created_at"]
        )

        address_data = AddressOut(
            address_id=row["address_id"],
            floor=row["floor"],
            apt=row["apt"],
            area=row["area"],
            city=row["city"],
            county=row["county"],
            created_at=row["address_created_at"],
            created_by=row["address_created_by"],
            building_num=row["building_num"],
            street=row["street"]
        )

        agency = AgencyOut(
            agency_id=row["agency_id"],
            name=row["agency_name"],
            email=row["agency_email"],
            phone_number=row["agency_phone_number"],
            created_at=row["agency_created_at"],
            created_by=created_by,
            broker=broker_data,
            address=address_data
        )
        agencies.append(agency)

    return {
        "data": agencies,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
    
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
