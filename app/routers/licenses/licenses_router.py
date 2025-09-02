from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from .license_pagination import PaginatedLicenses

from app import database
from ...dependencies import get_current_user
from ...models.user_model import User
from ...utils.file_helper import load_sql

from ...routers.licenses.licenses_create import LicenseCreate
from ...routers.licenses.licenses_out import LicenseOut
from ...routers.licenses.licenses_update import LicenseUpdate

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

    if "admin" not in current_user_roles:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("user/get_user_by_id.sql")
    user_result = db.execute(text(sql), {"user_id": license.user_id}).mappings().first()
    if not user_result:
        raise HTTPException(status_code=400, detail="No user exist!")
    elif "broker" in user_result and user_result["broker"] == False:
        raise HTTPException(status_code=400, detail="User should be broker!")
    
    existing_sql = load_sql("license/get_license_by_user.sql")  # make SQL that checks by user_id
    existing_license = db.execute(text(existing_sql), {"user_id": license.user_id}).mappings().first()
    if existing_license:
        raise HTTPException(status_code=400, detail="User already has a license")
    
    license_data = license.model_dump()

    license_sql = load_sql("license/create_license.sql")
    license_result = db.execute(text(license_sql), license_data)
    new_license_id = license_result.scalar()

    db.commit()

    role_result = db.execute(text(role_sql), {"user_id": license.user_id}).mappings().first()
    current_user_roles = [key for key, value in role_result.items() if value]

    sql = load_sql("license/get_license_by_id.sql")
    created_license = db.execute(text(sql), {"license_id": new_license_id}).mappings().first()

    broker_data = {k.replace("broker_", ""): v for k, v in created_license.items() if k.startswith("broker_")}
    agency_data = {k[len("agency_"):]: v for k, v in created_license.items() if k.startswith("agency_")}

    license_details = LicenseOut(
        **created_license,
        user=broker_data,
        agency=agency_data
    )

    return license_details

@router.put("/{license_id}", status_code=status.HTTP_200_OK)
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

    broker_data = {k.replace("broker_", ""): v for k, v in updated_license.items() if k.startswith("broker_")}
    agency_data = {k[len("agency_"):]: v for k, v in updated_license.items() if k.startswith("agency_")}

    license = LicenseOut(
        **updated_license,
        user=broker_data,
        agency=agency_data
    )

    return {"message": "License updated successfully", "license": license}

@router.get("/me", response_model=LicenseOut, status_code=status.HTTP_200_OK)
def get_license_by_id(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    # Check user roles
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()

    if not (roles.get("broker") or roles.get("realtor")):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Load query for license by id
    sql = load_sql("license/get_license_by_user.sql")
    result = db.execute(text(sql), {"user_id": current_user.user_id}).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="License not found")

    broker_data = {k.replace("broker_", ""): v for k, v in result.items() if k.startswith("broker_")}
    agency_data = {k[len("agency_"):]: v for k, v in result.items() if k.startswith("agency_")}

    return LicenseOut(
        **result,
        user=broker_data,
        agency=agency_data
    )

@router.get("", response_model=PaginatedLicenses, status_code=status.HTTP_200_OK)
def get_all_licenses(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),

    sort_by: str = Query("license_id", regex="^(license_id|lic_num|lic_status|lic_type|user_id|agency_id)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),

    lic_status: Optional[str] = Query(None),
    lic_type: Optional[str] = Query(None),
    agency_id: Optional[int] = Query(None),
    filter_user_id: Optional[int] = Query(None),

    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()

    if not roles["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    if roles["admin"]:
        role = "admin"
    elif roles["broker"]:
        role = "broker"
    else:
        role = "realtor"

    params = {
        "user_id": current_user.user_id,
        "role": role,
        "lic_status": lic_status,
        "lic_type": lic_type,
        "agency_id": agency_id,
        "filter_user_id": filter_user_id,
    }

    # total count
    total_sql = load_sql("license/count_licenses.sql")
    total = db.execute(text(total_sql), params).scalar()
    total_pages = (total + per_page - 1) // per_page

    sql = load_sql("license/get_all_licenses.sql").format(sort_by=sort_by, sort_order=sort_order)
    params.update({"limit": per_page, "offset": (page - 1) * per_page})
    query_result = db.execute(text(sql), params)

    licenses = []
    for result in query_result.mappings():
        broker_data = {k.replace("broker_", ""): v for k, v in result.items() if k.startswith("broker_")}
        agency_data = {k[len("agency_"):]: v for k, v in result.items() if k.startswith("agency_")}

        licenses.append(
            LicenseOut(
                **result,
                user=broker_data,
                agency=agency_data
            )
        )

    return {
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "data": licenses
    }

@router.get("/{license_id}", response_model=LicenseOut, status_code=status.HTTP_200_OK)
def get_license_by_id(
    license_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    # Check user roles
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()

    if not roles["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    if roles["admin"]:
        role = "admin"
    elif roles["broker"]:
        role = "broker"
    else:
        role = "realtor"

    # Load query for license by id
    sql = load_sql("license/get_license_by_id.sql")
    result = db.execute(text(sql),
        {"user_id": current_user.user_id, "role": role, "license_id": license_id}
    ).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="License not found")

    broker_data = {k.replace("broker_", ""): v for k, v in result.items() if k.startswith("broker_")}
    agency_data = {k[len("agency_"):]: v for k, v in result.items() if k.startswith("agency_")}

    return LicenseOut(
        **result,
        user=broker_data,
        agency=agency_data
    )

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
