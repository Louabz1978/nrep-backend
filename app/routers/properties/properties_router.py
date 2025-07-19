import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app import database
from app.routers.addresses.address_out import AddressOut
from ...models.user_model import User
from ...models.property_model import Property
from app.utils.out_helper import build_user_out
from app.utils.file_helper import load_sql

from ...dependencies import get_current_user

from .property_create import PropertyCreate
from .property_out import PropertyOut

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
    if current_user.role not in ("broker", "realtor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    #validate realtor_id
    realtor = property.realtor_id

    if current_user.role != "realtor":
        if realtor is None:
            raise HTTPException(status_code=400, detail="realtor_id is required")
        
        sql = load_sql("get_user_by_id.sql")
        result = db.execute(text(sql), {"user_id": realtor}).mappings().first()
        if not result :
            raise HTTPException(status_code=400, detail="invalid realtor_id")
        if result["role"] != "realtor":
            raise HTTPException(status_code=400, detail="Realtor must be realtor")
    else:
        realtor = current_user.user_id

    #validate seller_id
    sql = load_sql("get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": property.seller_id}).mappings().first()
    if not result :
        raise HTTPException(status_code=400, detail="invalid seller_id")
    if result["role"] != "seller":
        raise HTTPException(status_code=400, detail="Seller must be seller")

    db_property = property.model_dump()
    db_property["realtor_id"] = realtor

    sql = load_sql("create_property.sql")
    result = db.execute(text(sql), db_property)
    new_property_id = result.scalar()

    db.commit()

    sql = load_sql("get_property_by_id.sql")
    created_property = db.execute(text(sql), {"property_id": new_property_id}).mappings().first()
    property_details = PropertyOut(**created_property)

    return {"message" : "property created successfully","property": property_details}


@router.get("", response_model=list[PropertyOut], status_code=status.HTTP_200_OK)
def get_all_properties(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "broker", "realtor"):
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
    
    role_sql = load_sql("get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False and roles["broker"] == False and roles["realtor"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_property_by_id.sql")
    result = db.execute(text(sql), {"property_id": property_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")

    nested_prefixes = ("owner_", "created_by_", "address_")
    property_data = {
        k: v for k, v in row.items()
        if not any(k.startswith(prefix) for prefix in nested_prefixes)
    }
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}
    property = PropertyOut(
        **property_data,
        owner=build_user_out(row, "owner_"),
        created_by_user=build_user_out(row, "created_by_"),
        address=AddressOut(**address_data)
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















































































@router.put("/properties/{property_id}")
def update_property(
    property_id : int ,
    property_data: PropertyCreate ,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    #get property
    sql = load_sql("get_property_by_id.sql")
    property = db.execute(text(sql), {"property_id": property_id}).mappings().first()
    if not property:
        raise HTTPException( status_code= 404 , detail="property not found")
    
    #authorization check
    role_sql = load_sql("get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key,value in current_user_roles.items() if value]
    if not (
        "admin" in current_user_role
        or ("broker" in current_user_role and (current_user.user_id in [ property["created_by_user_id"], property["created_by_created_by"] ] ) )
        or ("realtor" in current_user_role and current_user.user_id == property["created_by_user_id"])
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    #owner_id check
    owner = db.execute(text(role_sql), {"user_id": property_data.owner_id}).mappings().first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    if owner["seller"] == False:
        raise HTTPException(status_code=404, detail="Owner is not a seller")

    #update address
    if property_data.address :
        db_property_address = property_data.address.model_dump()
        db_property_address["address_id"] = property["address_address_id"]
        sql = load_sql("update_address.sql")
        row = db.execute(text(sql), db_property_address)

    #update property
    db_property = property_data.model_dump(exclude={"address"})
    db_property["property_id"] = property_id
    sql = load_sql("update_property.sql")
    updated_property_id = db.execute(text(sql), db_property).scalar()
    db.commit()

    #fetch property data
    sql = load_sql("get_property_by_id.sql")
    row = db.execute(text(sql), {"property_id": updated_property_id}).mappings().first()
    nested_prefixes = ("owner_", "created_by_", "address_")
    property_data = {
        k: v for k, v in row.items()
        if not any(k.startswith(prefix) for prefix in nested_prefixes)
    }
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}
    property_details = PropertyOut(
        **property_data,
        owner=build_user_out(row, "owner_"),
        created_by_user=build_user_out(row, "created_by_"),
        address=AddressOut(**address_data)
    )

    return {"message": "Property updated successfully", "property details": property_details}

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
    role_sql = load_sql("get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_property_by_id.sql")
    result = db.execute(text(sql), {"property_id": property_id})
    property = result.mappings().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    delete_sql = load_sql("delete_additional.sql")
    db.execute(text(delete_sql), {"property_id": property_id})
    delete_sql = load_sql("delete_property.sql")
    db.execute(text(delete_sql), {"property_id": property_id})
    
    db.commit()
    return {"message": "Property deleted successfully"}
