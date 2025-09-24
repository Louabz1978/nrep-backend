from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .area_create import AreaCreate
from .area_out import AreaOut
from .area_update import AreaUpdate

from .area_pagination import PaginatedAreas


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
    
    sql = load_sql("area/get_area_by_title.sql")
    exist_area = db.execute(text(sql), {"title": area.title}).mappings().first()
    if exist_area:
        raise HTTPException(status_code=400, detail="Area already exists!")
    
    sql = load_sql("city/get_city_by_id.sql")
    exist_city = db.execute(text(sql), {"city_id": area.city}).mappings().first()

    if not exist_city:
        raise HTTPException(status_code=400, detail="City not exist!")

    params = {
        "title": area.title,
        "city_id": area.city,
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

@router.put("/{area_id}", status_code=status.HTTP_200_OK)
def update_area_by_id(
    area_id: int,
    area_data: AreaUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # 1. Check if area exists
    sql = load_sql("area/get_area_by_id.sql")
    area_row = db.execute(text(sql), {"area_id": area_id}).mappings().first()
    if not area_row:
        raise HTTPException(status_code=404, detail="Area not found")

    # 2. Check user roles
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(
        text(role_sql), {"user_id": current_user.user_id}
    ).mappings().first()
    current_user_role_list = [key for key, value in current_user_roles.items() if value]

    if not "admin" in current_user_role_list:
        raise HTTPException(status_code=403, detail="Not authorized to update this area")

    update_data = area_data.model_dump(exclude_unset=True)
    if not update_data:
        return {"message": "No changes provided", "area": AreaOut(**area_row)}

    # ✅ Validate city_id if provided
    if "city_id" in update_data:
        city_check = db.execute(
            text("SELECT city_id FROM cities WHERE city_id = :city_id"),
            {"city_id": update_data["city_id"]}
        ).first()

        if not city_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City with id {update_data['city_id']} does not exist"
            )
    
    # 3. Prepare update data
    db_area_update = {
        k: v for k, v in area_data.model_dump(exclude_unset=True).items()
        if v is not None
    }
    db_area_update["area_id"] = area_id
    db_area_update["updated_by"] = current_user.user_id

    if not db_area_update:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    set_clause = ", ".join(f"{k} = :{k}" for k in db_area_update if k != "area_id")
    sql = f"""
        UPDATE areas
        SET {set_clause}, updated_at = NOW()
        WHERE area_id = :area_id
        RETURNING area_id;
    """
    updated_area_id = db.execute(text(sql), db_area_update).scalar()
    db.commit()

    # 4. Fetch updated area
    sql = load_sql("area/get_area_by_id.sql")
    row = db.execute(text(sql), {"area_id": updated_area_id}).mappings().first()
    area_out = AreaOut(**row)

    return {"message": "Area updated successfully", "area": area_out}

@router.get("/{area_id:int}", status_code=status.HTTP_200_OK)
def get_area_by_id(
    area_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("area/get_area_by_id.sql")
    row = db.execute(text(sql), {"area_id": area_id}).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Area not found")

    return {"area": AreaOut(**row)}


@router.get("/", response_model=PaginatedAreas, status_code=status.HTTP_200_OK)
def get_all_areas(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    sort_by: str = Query("area_id", regex="^(area_id|title|updated_at|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    title : Optional[str]=Query(None),
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # Role check
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    filtering ={
         "title": f"%{title}%" if title else None,
    }
    params={  
        "limit": per_page,
        "offset": (page - 1) * per_page
        }
    params={**filtering,**params}
    total_sql = load_sql("area/count_all_areas.sql")
    total = db.execute(text(total_sql),filtering).scalar()
    total_pages = (total + per_page - 1) // per_page


    sql = load_sql("area/get_all_areas.sql").format(sort_by=sort_by,sort_order=sort_order)
    rows = db.execute(text(sql),params).mappings().all()
    areas=[AreaOut(**row) for row in rows]

    return {
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "data": areas
    }
    

@router.get("/city/{city_id:int}", response_model=List[AreaOut], status_code=status.HTTP_200_OK)
def get_areas_by_city_id(
    city_id: int,

    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # Role check
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("area/get_areas_by_city_id.sql")
    areas_dict = db.execute(text(sql), {"city_id": city_id}).mappings().all()

    return [AreaOut(**row) for row in areas_dict]

@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(
    area_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("area/get_area_by_id.sql")
    result = db.execute(text(sql), {"area_id": area_id})
    area = result.mappings().first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    delete_sql = load_sql("area/delete_area.sql")
    db.execute(text(delete_sql), {"area_id": area_id})
    
    db.commit()
    return {"message": "Area deleted successfully"}
