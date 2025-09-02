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

from ..counties.county_create import CountyCreate
from ..counties.county_out import CountyOut

from ..areas.area_create import AreaCreate
from ..areas.area_out import AreaOut

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

@router.get("/{city_id:int}", status_code=status.HTTP_200_OK)
def get_ciy_by_id(
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
        counties=[]
    )
    counties_map = {}

    for row in rows:
        if row["county_id"] is not None:
            if row["county_id"] not in counties_map:
                county = CountyOut(
                    county_id=row["county_id"],
                    title=row["county_title"],
                    city_id=city.city_id,
                    created_at=row["county_created_at"],
                    created_by=row["county_created_by"],
                    updated_at=row["county_updated_at"],
                    updated_by=row["county_updated_by"],
                    areas=[]
                )
                counties_map[row["county_id"]] = county
                city.counties.append(county)

            # Add areas under the right county
            if row["area_id"] is not None:
                counties_map[row["county_id"]].areas.append(
                    AreaOut(
                        area_id=row["area_id"],
                        title=row["area_title"],
                        county_id=row["county_id"],
                        created_at=row["area_created_at"],
                        created_by=row["area_created_by"],
                        updated_at=row["area_updated_at"],
                        updated_by=row["area_updated_by"]
                    )
                )

    return {"city": city}
