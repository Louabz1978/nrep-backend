import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app import database
from ...models.user_model import User
from ...models.property_model import Property
from app.utils.out_helper import build_user_out
from app.utils.file_helper import load_sql

from ...dependencies import get_current_user

from .property_create import PropertyCreate
from .property_out import PropertyOut

from ..addresses.address_out import AddressOut
from ..users.user_out import UserOut
from ..users.roles_enum import UserRole
router = APIRouter(
    prefix="/property",
    tags=["Properties"]
)

# Defines a POST HTTP endpoint at the path '/property'
# Creates a new property property
# Returns HTTP 201 Created with a JSON message confirming success and the new_property_id
# Raises HTTP 403 Forbidden if the user is not authorized (admin, broker, or realtor)
# Raises HTTP 400 Bad Request if:
#   - The user role is 'realtor' and realtor_id is missing, invalid, or not a realtor
#   - The seller_id does not exist
#   - The specified user is not a seller
@router.post("", status_code=status.HTTP_201_CREATED)
def create_property(
    property: PropertyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]

    if "realtor" in current_user_role or "broker" in current_user_role:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    #validate seller_id

    sql = load_sql("get_user_by_id.sql")
    owner_result = db.execute(text(sql), {"user_id": property.owner_id}).mappings().first()
    if not owner_result :
        raise HTTPException(status_code=400, detail="invalid owner_id")
    
    if not owner_result["seller"]:
        raise HTTPException(status_code=400, detail="Owner must be seller")
    
    address_data = property.address.model_dump()
    address_data["created_at"] = datetime.now(timezone.utc)
    address_data["created_by"] = current_user.user_id
    address_sql = load_sql("create_address.sql")
    address_result = db.execute(text(address_sql),address_data)
    address_id = address_result.scalar()

    db_property = property.model_dump()
    db_property["created_by"] = current_user.user_id
    db_property["address_id"] = address_id

    property_sql = load_sql("create_property.sql")
    property_result = db.execute(text(property_sql), db_property)
    new_property_id = property_result.scalar()

    db.commit()
    
    sql = load_sql("get_property_by_id.sql")
    created_property = db.execute(text(sql), {"property_id": new_property_id}).mappings().first()

    address_dict = {
        "address_id": created_property.get("address_address_id"),
        "address": created_property.get("address_address"),
        "floor": created_property.get("address_floor"),
        "apt": created_property.get("address_apt"),
        "area": created_property.get("address_area"),
        "city": created_property.get("address_city"),
        "county": created_property.get("address_county"),
        "created_at": created_property.get("address_created_at"),
        "created_by": created_property.get("address_created_by"),
    }
    address_obj = AddressOut(**address_dict) if address_dict else None
    
    user_sql = load_sql("get_user_by_id.sql")
    roles_sql = load_sql("get_user_roles.sql")

    owner_id = property.owner_id
    owner_result = db.execute(text(user_sql), {"user_id": owner_id}).mappings().first()
    owner_roles_result = db.execute(text(role_sql), {"user_id": owner_id}).mappings().first()
    owner_roles = [key for key, value in owner_roles_result.items() if value is True and key in UserRole.__members__] if owner_roles_result else []
    if owner_result:
        owner_data = dict(owner_result)
        owner_data["role"] = owner_roles
        owner_obj = UserOut(**owner_data)
    else:
        owner_obj = None

    created_by_id = current_user.user_id
    created_by_result = db.execute(text(user_sql), {"user_id": created_by_id}).mappings().first()
    created_by_roles_result = db.execute(text(role_sql), {"user_id": created_by_id}).mappings().first()
    created_by_roles = [key for key, value in created_by_roles_result.items() if value is True and key in UserRole.__members__] if created_by_roles_result else []
    
    if created_by_result:
        created_by_data = dict(created_by_result)
        created_by_data["role"] = created_by_roles
        created_by_obj = UserOut(**created_by_data)
    else:
        created_by_obj = None

    property_out_data = dict(created_property)
    property_out_data["address"] = address_obj
    property_out_data["owner_id"] = owner_obj
    property_out_data["created_by"] = created_by_obj

    property_details = PropertyOut(**property_out_data)

    return {
        "message": "property created successfully",
        "property": property_details
    }


@router.get("", response_model=list[PropertyOut], status_code=status.HTTP_200_OK)
def get_all_properties(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.roles not in ("admin", "broker", "realtor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_all_properties.sql")
    result = db.execute(text(sql))

    properties = []
    for row in result.mappings():
        property = PropertyOut(
            **row,
            seller=build_user_out(row, "seller_"),
            realtor=build_user_out(row, "realtor_")
        )
        properties.append(property)
    return properties

# Defines a GET HTTP endpoint at the path '/property/{property_id}'
# GET the resource identified by 'property_id'
# Returns HTTP status code 200 with a JSON PropertyOut
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the property does not exist
@router.get("/{property_id}", response_model=PropertyOut, status_code=status.HTTP_200_OK)
def get_property_by_id(
    property_id: int, 
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    
    if current_user.role not in ("admin", "broker", "realtor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_property_by_id.sql")
    result = db.execute(text(sql), {"property_id": property_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")

    property = PropertyOut(
        **row,
        seller=build_user_out(row, "seller_"),
        realtor=build_user_out(row, "realtor_")
    )
    return property

@router.post("/my-properties")
async def my_properties(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    properties = db.query(Property).filter(Property.realtor_id == current_user.user_id).all()
    if not properties:
        return {"message": "No Properties Found"}

    property_list = []
    for prop in properties:
        images_folder = f"property_images/{prop.property_id}"
        if os.path.exists(images_folder):
            images = sorted(
            [f"/{images_folder}/{img}" 
             for img in os.listdir(images_folder) if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
)

        else:
            images = []

        property_list.append({
            "property_id": prop.property_id,
            "address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "price": prop.price,
            "bedrooms": prop.bedrooms,
            "bathrooms": prop.bathrooms,
            "property_realtor_commission":prop.property_realtor_commission,
            "buyer_realtor_commission":prop.buyer_realtor_commission,
            "area_sqft": prop.area_sqft,
            "images": images,  
        })

    return property_list

@router.post("/upload-property")
async def upload_property(
    description: str = Form(...),
    price: float = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    property_type: str = Form(...),
    bedrooms: int = Form(...),
    bathrooms: float = Form(...),
    property_realtor_commission: float = Form(...),
    buyer_realtor_commission: float = Form(...),
    area_sqft: int = Form(...),
    lot_size_sqft: int = Form(...),
    year_built: int = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "realtor": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload a property. Realtor role required."
        )

    new_property = Property(
        realtor_id=current_user.user_id,
        title="New Property",
        description=description,
        price=price,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        property_realtor_commission=property_realtor_commission,
        buyer_realtor_commission=buyer_realtor_commission,
        area_sqft=area_sqft,
        lot_size_sqft=lot_size_sqft,
        year_built=year_built,
        latitude=25.7617,
        longitude=-80.1918,
        image_url="",
        listed_date=datetime.now(timezone.utc),
        status="available"
    )

    db.add(new_property)
    db.commit()
    db.refresh(new_property)

    property_folder = f"property_images/{new_property.property_id}"
    os.makedirs(property_folder, exist_ok=True)

    image_paths = []

    for idx, image in enumerate(images):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        filename = f"{timestamp}_{idx}_{image.filename}"
        file_path = os.path.join(property_folder, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_paths.append(f"/{file_path}")

    if image_paths:
        new_property.image_url = image_paths[0]
        db.commit()

    return {"message": "Property listed successfully", "property_id": new_property.property_id, "images": image_paths}

# Defines a DELETE HTTP endpoint at the path '/property/{property_id}'
# Deletes the resource identified by 'property_id'
# Returns HTTP status code 204 with a JSON message confirming successful deletion
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the property does not exist
@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_property_by_id.sql")
    result = db.execute(text(sql), {"property_id": property_id})
    property = result.mappings().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    delete_sql = load_sql("delete_property.sql")
    db.execute(text(delete_sql), {"property_id": property_id})
    
    db.commit()
    return {"message": "Property deleted successfully"}
