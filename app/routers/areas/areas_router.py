from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .area_create import AreaCreate
from .area_out import AreaOut

router = APIRouter(
    prefix="/areas",
    tags=["Areas"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_area(
    area: AreaCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_roles = [key for key, value in role_result.items() if value]

    if "admin" not in current_user_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("county/get_county_by_id.sql")
    exist_county = db.execute(text(sql), {"county_id": area.county}).mappings().first()

    if not exist_county:
        raise HTTPException(status_code=400, detail="County is not exist!")

    params = {
        "title": area.title,
        "county_id": area.county,
        "created_by": current_user.user_id
    }

    sql = load_sql("area/create_area.sql")
    new_area = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("area/get_area_by_id.sql")
    created_area = db.execute(text(sql), {"area_id": new_area}).mappings().first()

    area_details = AreaOut(**created_area)

    return {
        "message": "Area created successfully",
        "area": area_details  
    }
