from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .county_create import CountyCreate
from .county_out import CountyOut

from ..areas.area_out import AreaOut

router = APIRouter(
    prefix="/counties",
    tags=["Counties"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_county(
    county: CountyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_roles = [key for key, value in role_result.items() if value]

    if "admin" not in current_user_roles:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_city_by_id.sql")
    exist_city = db.execute(text(sql), {"city_id": county.city}).mappings().first()

    if not exist_city:
        raise HTTPException(status_code=400, detail="City is not exist!")

    params = {
        "title": county.title,
        "city_id": county.city,
        "created_by": current_user.user_id
    }

    sql = load_sql("county/create_county.sql")
    new_county = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("county/get_county_by_id.sql")
    created_county = db.execute(text(sql), {"county_id": new_county}).mappings().first()

    county_details = CountyOut(**created_county, areas=None)

    return {
        "message": "County created successfully",
        "county": county_details  
    }

@router.get("/{county_id:int}", status_code=status.HTTP_200_OK)
def get_county_by_id(
    county_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("county/get_county_by_id.sql")
    rows = db.execute(text(sql), {"county_id": county_id}).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="County not found")

    first = rows[0]
    county = CountyOut(
        county_id=first["county_id"],
        title=first["title"],
        city_id=first["city_id"],
        created_at=first["created_at"],
        created_by=first["created_by"],
        updated_at=first["updated_at"],
        updated_by=first["updated_by"],
        areas=[]
    )

    for row in rows:
        if row["area_id"] is not None:
            county.areas.append(
                AreaOut(
                    area_id=row["area_id"],
                    title=row["area_title"],
                    county_id=county.county_id,
                    created_at=row["area_created_at"],
                    created_by=row["area_created_by"],
                    updated_at=row["area_updated_at"],
                    updated_by=row["area_updated_by"]
                )
            )

    return {"county": county}