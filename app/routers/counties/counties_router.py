from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .county_create import CountyCreate
from .county_out import CountyOut

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
