from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .city_create import CityCreate
from .city_out import CityOut
from .city_update import CityUpdate

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

@router.put("/{city_id}", response_model=dict)
def update_city_by_id(
    city_id: int,
    city_data: CityUpdate,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user)
):
    sql = load_sql("city/get_city_by_id.sql")
    city_row = db.execute(text(sql), {"city_id": city_id}).mappings().first()

    if not city_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    update_data = city_data.model_dump(exclude_unset=True)
    if not update_data:
        return {"message": "No changes provided", "city": CityOut(**city_row)}

    # Build SET clause dynamically
    set_clause = ", ".join([f"{field} = :{field}" for field in update_data.keys()])

    update_sql = f"""
    UPDATE cities
    SET {set_clause},
        updated_at = NOW(),
        updated_by = :updated_by
    WHERE city_id = :city_id
    """

    update_data.update({"city_id": city_id, "updated_by": current_user.user_id})
    db.execute(text(update_sql), update_data)
    db.commit()

    updated_row = db.execute(text(sql), {"city_id": city_id}).mappings().first()
    return {"message": "City updated successfully", "city": CityOut(**updated_row)}
