from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone

from app import database
from ...dependencies import get_current_user
from ...models.user_model import User
from ...utils.file_helper import load_sql

from app.routers.licenses.licenses_create import LicenseCreate
from app.routers.licenses.licenses_out import LicenseOut
from app.routers.licenses.licenses_update import LicenseUpdate

router = APIRouter(prefix="/licenses", tags=["Licenses"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_license(
    license: LicenseCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_roles = [key for key, value in role_result.items() if value]

    if "admin" in current_user_roles:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_sql = load_sql("license/get_license_by_user.sql")  # make SQL that checks by user_id
    existing_license = db.execute(text(existing_sql), {"user_id": current_user.user_id}).mappings().first()
    if existing_license:
        raise HTTPException(status_code=400, detail="User already has a license")

    
    license_data = license.model_dump()

    license_sql = load_sql("license/create_license.sql")
    license_result = db.execute(text(license_sql), license_data)
    new_license_id = license_result.scalar()

    db.commit()

    sql = load_sql("license/get_license_by_id.sql")
    created_license = db.execute(text(sql), {"license_id": new_license_id}).mappings().first()

    license_out_data = dict(created_license)

    license_details = LicenseOut(**license_out_data)

    return license_details

@router.post("/{license_id}", status_code=status.HTTP_200_OK)
def update_license(
    license_id: int,
    license_in: LicenseUpdate = Depends(LicenseUpdate.as_form),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    # Check user role
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]
    if "admin" not in current_user_role:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch existing license
    get_sql = load_sql("license/get_license_by_id.sql")
    license_db = db.execute(text(get_sql), {"license_id": license_id}).mappings().first()
    if not license_db:
        raise HTTPException(status_code=404, detail="License not found")

    # Only update fields provided in form
    update_data = {k: v for k, v in license_in.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")
    update_data["license_id"] = license_id

    # Build SQL dynamically
    set_clause = ", ".join(f"{k} = :{k}" for k in update_data if k != "license_id")
    sql = f"UPDATE licenses SET {set_clause} WHERE license_id = :license_id RETURNING license_id;"
    updated_license_id = db.execute(text(sql), update_data).scalar()
    db.commit()

    # Fetch updated license
    updated_license = db.execute(text(get_sql), {"license_id": updated_license_id}).mappings().first()
    return {"message": "License updated successfully", "license": updated_license}

@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_license(
    license_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("license/get_license_by_id.sql")
    license_existing = db.execute(text(sql), {"license_id": license_id}).mappings().first()
    if not license_existing:
        raise HTTPException(status_code=404, detail="license not found")
    
    delete_sql = load_sql("license/delete_license.sql")
    db.execute(text(delete_sql), {"license_id": license_id})

    db.commit()
    return {"message": "license deleted successfully"}