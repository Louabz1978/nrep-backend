from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

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

    #check city
    sql = load_sql("city/get_city_by_title.sql")
    exist_city = db.execute(text(sql), {"title": city.title}).scalar()
    
    if exist_city:
        raise HTTPException(status_code=400, detail="City already exists!")
    
    #check county
    sql = load_sql("county/get_county_by_id.sql")
    exist_county = db.execute(text(sql), {"county_id": city.county}).mappings().first()
    if not exist_county:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="County not exist")

    params = {
        "title": city.title,
        "county_id": city.county,
        "created_by": current_user.user_id
    }

    sql = load_sql("city/create_city.sql")
    new_city = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("city/get_city_by_id.sql")
    created_city = db.execute(text(sql), {"city_id": new_city}).mappings().first()

    city_details = CityOut(**created_city)

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

    #county check
    if "county_id" in update_data:
        sql_county = load_sql("county/get_county_by_id.sql")
        county_exists = db.execute(text(sql_county), {"county_id":update_data["county_id"]})
        if not county_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="County not exist")
        
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

@router.get("/{city_id:int}", status_code=status.HTTP_200_OK)
def get_city_by_id(
    city_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_city_by_id.sql")
    rows = db.execute(text(sql), {"city_id": city_id}).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="City not found")

    first = rows[0]
    city = CityOut(
        city_id=first["city_id"],
        title=first["title"],
        created_at=first["created_at"],
        created_by=first["created_by"],
        updated_at=first["updated_at"],
        updated_by=first["updated_by"],
    )

    return {"city": city}

@router.get("", response_model=List[CityOut], status_code=status.HTTP_200_OK)
def get_all_cities(
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # ✅ Role check
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_all_cities.sql")
    rows = db.execute(text(sql)).mappings().all()

    # ✅ Restructure into nested format
    cities_dict = {}
    for row in rows:
        city_id = row["city_id"]
        if city_id not in cities_dict:
            cities_dict[city_id] = CityOut(
                city_id=city_id,
                title=row["city_title"],
                created_at=row["city_created_at"],
                updated_at=row["city_updated_at"],
                created_by=row["city_created_by"],
                updated_by=row["city_updated_by"],
            )

    return list(cities_dict.values())

@router.get("/county/{county_id:int}", status_code=status.HTTP_200_OK)
def get_cities_by_county_id(
    county_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_cities_by_county_id.sql")
    rows = db.execute(text(sql), {"county_id": county_id}).mappings().all()

    cities_dict = {}
    for row in rows:
        city_id = row["city_id"]
        if city_id not in cities_dict:
            cities_dict[city_id] = CityOut(
                city_id=city_id,
                title=row["city_title"],
                created_at=row["city_created_at"],
                updated_at=row["city_updated_at"],
                created_by=row["city_created_by"],
                updated_by=row["city_updated_by"],
            )

    return list(cities_dict.values())

@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    city_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("city/get_city_by_id.sql")
    result = db.execute(text(sql), {"city_id": city_id})
    city = result.mappings().first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    delete_sql = load_sql("city/delete_city.sql")
    db.execute(text(delete_sql), {"city_id": city_id})
    
    db.commit()
    return {"message": "City deleted successfully"}
