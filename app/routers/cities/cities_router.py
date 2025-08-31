from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .city_create import CityCreate
from .city_out import CityOut

router = APIRouter(
    prefix="/cities",
    tags=["Cities"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_city(
    city: CityCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_roles = [key for key, value in role_result.items() if value]

    if "admin" not in current_user_roles:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_city_by_title.sql")
    exist_city = db.execute(text(sql), {"title": city.title}).scalar()
    
    if exist_city:
        raise HTTPException(status_code=400, detail="City already exists!")

    params = {
        "title": city.title,
        "created_by": current_user.user_id
    }

    sql = load_sql("city/create_city.sql")
    new_city = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("city/get_city_by_id.sql")
    created_city = db.execute(text(sql), {"city_id": new_city}).mappings().first()

    city_details = CityOut(**created_city, counties=None)

    return {
        "message": "City created successfully",
        "city": city_details  
    }
