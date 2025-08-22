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
from .agencies_update import AgencyUpdate

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
def update_agency_by_id(
    agency_id: int,
    agency_data: AgencyUpdate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    # Authorization: only admin
    if not current_user.roles.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check agency exists
    agency_sql = load_sql("agency/get_agency_by_id.sql")
    agency_row = db.execute(text(agency_sql), {"agency_id": agency_id}).mappings().first()
    if not agency_row:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Validate broker if provided
    if agency_data.broker_id is not None:
        broker_sql = load_sql("user/get_user_by_id.sql")
        broker = db.execute(text(broker_sql), {"user_id": agency_data.broker_id}).mappings().first()
        if not broker or not broker["broker"]:
            raise HTTPException(status_code=400, detail="Invalid broker_id or user is not a broker")

    # ---- Update Agency ----
    db_agency_update = {
        k: v for k, v in agency_data.model_dump(exclude_unset=True).items()
        if k != "address" and v is not None
    }
    db_agency_update["agency_id"] = agency_id

    if len(db_agency_update) > 1:  # has fields besides agency_id
        set_clause = ", ".join(f"{k} = :{k}" for k in db_agency_update if k != "agency_id")
        sql = f"""
            UPDATE agencies
            SET {set_clause}
            WHERE agency_id = :agency_id
        """
        db.execute(text(sql), db_agency_update)

    if agency_data.address:
        db_address_update = {
            k: v for k, v in agency_data.address.model_dump(exclude_unset=True).items()
            if v is not None
        }

        if db_address_update:
            db_address_update["address_id"] = agency_row["address_id"]
            set_clause = ", ".join(f"{k} = :{k}" for k in db_address_update if k != "address_id")
            sql = f"""
                UPDATE addresses
                SET {set_clause}
                WHERE address_id = :address_id
            """
            db.execute(text(sql), db_address_update)

    db.commit()

    sql = load_sql("agency/get_agency_by_id.sql")
    row = db.execute(text(sql), {"agency_id": agency_id}).mappings().first()

    agency_out = {
        "agency_id": row["agency_id"],
        "name": row["name"],
        "email": row["email"],
        "phone_number": row["phone_number"],
        "created_at": row["created_at"],
        "created_by": row["created_by"],
        "broker_id": row["broker_id"],
        "address": {
            "address_id": row["address_id"],
            "floor": row["floor"],
            "apt": row["apt"],
            "area": row["area"],
            "city": row["city"],
            "county": row["county"],
            "building_num": row["building_num"],
            "street": row["street"],
            "created_at": row["address_created_at"],
        }
    }

    return {"message": "Agency updated successfully", "agency": agency_out}

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
