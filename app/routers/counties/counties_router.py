from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...models.user_model import User

from app.utils.file_helper import load_sql
from ...dependencies import get_current_user

from .county_create import CountyCreate
from .county_out import CountyOut
from .county_update import CountyUpdate

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
    
    #check county
    sql = load_sql("county/get_county_by_title.sql")
    exist_county = db.execute(text(sql), {"title":county.title}).mappings().first()
    if exist_county:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="County already exists")

    params = {
        "title": county.title,
        "created_by": current_user.user_id
    }

    sql = load_sql("county/create_county.sql")
    new_county = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("county/get_county_by_id.sql")
    created_county = db.execute(text(sql), {"county_id": new_county}).mappings().first()

    county_details = CountyOut(**created_county)

    return {
        "message": "County created successfully",
        "county": county_details  
    }

@router.put("/{county_id}", response_model=dict)
def update_county_by_id(
    county_id: int,
    county_data: CountyUpdate,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user)
):
    sql = load_sql("county/get_county_by_id.sql")
    county_row = db.execute(text(sql), {"county_id": county_id}).mappings().first()

    if not county_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="County not found"
        )

    update_data = county_data.model_dump(exclude_unset=True)
    if not update_data:
        return {"message": "No changes provided", "county": CountyOut(**county_row)}

    # Build SET clause dynamically
    set_clause = ", ".join([f"{field} = :{field}" for field in update_data.keys()])

    update_sql = f"""
    UPDATE counties
    SET {set_clause},
        updated_at = NOW(),
        updated_by = :updated_by
    WHERE county_id = :county_id
    """

    update_data.update({"county_id": county_id, "updated_by": current_user.user_id})
    db.execute(text(update_sql), update_data)
    db.commit()

    updated_row = db.execute(text(sql), {"county_id": county_id}).mappings().first()
    return {"message": "County updated successfully", "county": CountyOut(**updated_row)}

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
        created_at=first["created_at"],
        created_by=first["created_by"],
        updated_at=first["updated_at"],
        updated_by=first["updated_by"],
    )

    return {"county": county}

@router.get("", response_model=List[CountyOut], status_code=status.HTTP_200_OK)
def get_all_counties(
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # Role check
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("county/get_all_counties.sql")
    rows = db.execute(text(sql)).mappings().all()

    counties_dict = {}
    for row in rows:
        county_id = row["county_id"]
        if county_id not in counties_dict:
            counties_dict[county_id] = CountyOut(
                county_id=county_id,
                title=row["county_title"],
                created_at=row["county_created_at"],
                updated_at=row["county_updated_at"],
                created_by=row["county_created_by"],
                updated_by=row["county_updated_by"],
            )

    return list(counties_dict.values())

@router.delete("/{county_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_county(
    county_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("county/get_county_by_id.sql")
    result = db.execute(text(sql), {"county_id": county_id})
    county = result.mappings().first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    delete_sql = load_sql("county/delete_county.sql")
    db.execute(text(delete_sql), {"county_id": county_id})
    
    db.commit()
    return {"message": "County deleted successfully"}
