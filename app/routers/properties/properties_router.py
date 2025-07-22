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
from .property_update import PropertyUpdate

from ..addresses.address_out import AddressOut

from ..users.user_out import UserOut

from ..addresses.address_out import AddressOut
from ..users.user_out import UserOut
from ..users.roles_enum import UserRole
router = APIRouter(
    prefix="/property",
    tags=["Properties"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_property(
    property: PropertyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]

    if "realtor" in current_user_role or "broker" in current_user_role:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    #validate seller_id

    sql = load_sql("user/get_user_by_id.sql")
    owner_result = db.execute(text(sql), {"user_id": property.owner_id}).mappings().first()
    if not owner_result :
        raise HTTPException(status_code=400, detail="invalid owner_id")
    
    if not owner_result["seller"]:
        raise HTTPException(status_code=400, detail="Owner must be seller")
    
    address_data = property.address.model_dump()
    address_data["created_at"] = datetime.now(timezone.utc)
    address_data["created_by"] = current_user.user_id
    address_sql = load_sql("address/create_address.sql")
    address_result = db.execute(text(address_sql),address_data)
    address_id = address_result.scalar()

    db_property = property.model_dump()
    db_property["created_by"] = current_user.user_id
    db_property["address_id"] = address_id

    property_sql = load_sql("property/create_property.sql")
    property_result = db.execute(text(property_sql), db_property)
    new_property_id = property_result.scalar()

    db.commit()
    
    sql = load_sql("property/get_property_by_id.sql")
    created_property = db.execute(text(sql), {"property_id": new_property_id}).mappings().first()

    address_dict = {
        "address_id": created_property.get("address_address_id"),
        "floor": created_property.get("address_floor"),
        "apt": created_property.get("address_apt"),
        "area": created_property.get("address_area"),
        "city": created_property.get("address_city"),
        "county": created_property.get("address_county"),
        "created_at": created_property.get("address_created_at"),
        "created_by": created_property.get("address_created_by"),
        "building_num": created_property.get("address_building_num"),
        "street" : created_property.get("address_street")
    }
    address_obj = AddressOut(**address_dict) if address_dict else None
    
    user_sql = load_sql("user/get_user_by_id.sql")
    role_sql = load_sql("role/get_user_roles.sql")

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
    property_out_data["owner"] = owner_obj
    property_out_data["created_by_user"] = created_by_obj

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
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("property/get_all_properties.sql")
    result = db.execute(text(sql))

    properties = []
    for row in result.mappings():
        created_by_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"created_by_{role}") is True
        ]

        created_by = UserOut(
            user_id=row["created_by_user_id"],
            first_name=row["created_by_first_name"],
            last_name=row["created_by_last_name"],
            email=row["created_by_email"],
            phone_number=row["created_by_phone_number"],
            role=created_by_roles,
            created_by=row["created_by_created_by"], 
            created_at=row["created_by_created_at"] 
        )

        owner_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"owner_{role}") is True
        ]

        owner = UserOut(
            user_id=row["owner_user_id"],
            first_name=row["owner_first_name"],
            last_name=row["owner_last_name"],
            email=row["owner_email"],
            phone_number=row["owner_phone_number"],
            role=owner_roles,
            created_by=row["owner_created_by"],  # from users.created_by
            created_at=row["owner_created_at"] 
        )
            
        property = PropertyOut(
            property_id=row["property_id"],
            description=row["description"],
            price=row["price"],
            property_type=row["property_type"],
            floor=row["floor"],
            bedrooms=row["bedrooms"],
            bathrooms=row["bathrooms"],
            property_realtor_commission=row["property_realtor_commission"],
            buyer_realtor_commission=row["buyer_realtor_commission"],
            area_space=row["area_space"],
            year_built=row["year_built"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            status=row["status"],
            created_at=row["created_at"],
            last_updated=row["last_updated"],
            image_url=row["image_url"],
            
            created_by_user=created_by,
            owner=owner,
            address= AddressOut (
                address_id=row["address_id"],
                floor=row["floor"],
                apt=row["apt"],
                area=row["area"],
                city=row["city"],
                county=row["county"],
                created_at=row["address_created_at"],
                created_by=row["address_created_by"],
                building_num=row["building_num"],
                street=row["street"],
            )
        )
        properties.append(property)

    return properties

@router.get("/{property_id}", response_model=PropertyOut, status_code=status.HTTP_200_OK)
def get_property_by_id(
    property_id: int, 
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False and roles["broker"] == False and roles["realtor"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("property/get_property_by_id.sql")
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
    property_data: PropertyUpdate ,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    #get property
    sql = load_sql("property/get_property_by_id.sql")
    property = db.execute(text(sql), {"property_id": property_id}).mappings().first()
    if not property:
        raise HTTPException( status_code= 404 , detail="property not found")
    
    #authorization check
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key,value in current_user_roles.items() if value]
    if not (
        "admin" in current_user_role
        or ("broker" in current_user_role and (current_user.user_id in [ property["created_by_user_id"], property["created_by_created_by"] ] ) )
        or ("realtor" in current_user_role and current_user.user_id == property["created_by_user_id"])
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    #owner_id check
    if property_data.owner_id:
        owner = db.execute(text(role_sql), {"user_id": property_data.owner_id}).mappings().first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        if owner["seller"] == False:
            raise HTTPException(status_code=404, detail="Owner is not a seller")

    #update address
    if property_data.address :
        db_property_address = property_data.address.model_dump()
        db_property_address["address_id"] = property["address_address_id"]
        sql = load_sql("address/update_address.sql")
        row = db.execute(text(sql), db_property_address)

    #update property
    db_property = property_data.model_dump(exclude_unset=True, exclude={"address"})
    db_property["property_id"] = property_id
    if property_data.status != property["status"]:
        db_property["last_updated"] = datetime.now()
    set_clause = ", ".join(f"{k} = :{k}" for k in db_property)
    sql = f"UPDATE PROPERTIES SET {set_clause} WHERE property_id= :property_id RETURNING property_id;"
    updated_property_id = db.execute(text(sql), db_property).scalar()
    db.commit()

    #fetch property data
    sql = load_sql("property/get_property_by_id.sql")
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
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("property/get_property_by_id.sql")
    result = db.execute(text(sql), {"property_id": property_id})
    property = result.mappings().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    delete_sql = load_sql("additional/delete_additional.sql")
    db.execute(text(delete_sql), {"property_id": property_id})
    delete_sql = load_sql("property/delete_property.sql")
    db.execute(text(delete_sql), {"property_id": property_id})
    
    db.commit()
    return {"message": "Property deleted successfully"}
