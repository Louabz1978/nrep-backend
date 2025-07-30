from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import random

from app import database

from ...utils.file_helper import load_sql
from ...utils.out_helper import build_user_out
from ...dependencies import get_current_user
from ...utils.validate_photo import save_photos

from ...models.user_model import User

from ..users.roles_enum import UserRole

from ..users.user_out import UserOut
from .property_out import PropertyOut
from .property_pagination import PaginatedProperties
from ..addresses.address_out import AddressOut
from ..addresses.address_update import AddressUpdate

from .property_create import PropertyCreate
from .property_update import PropertyUpdate
from ..additional.additional_create import AdditionalCreate
from ..additional.additional_out import AdditionalOut
from ..addresses.address_create import AddressCreate
from .properties_status_enum import PropertyStatus

router = APIRouter(
    prefix="/property",
    tags=["Properties"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_property(
    property: PropertyCreate = Depends(PropertyCreate.as_form),
    additional: AdditionalCreate = Depends(AdditionalCreate.as_form),
    address: AddressCreate = Depends(AddressCreate.as_form),
    photos: List[UploadFile] = File(...),
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

    saved_files = save_photos(address, photos)

    sql = load_sql("user/get_user_by_id.sql")
    owner_result = db.execute(text(sql), {"user_id": property.owner_id}).mappings().first()
    if not owner_result :
        raise HTTPException(status_code=400, detail="invalid owner_id")
    
    if not owner_result["seller"]:
        raise HTTPException(status_code=400, detail="Owner must be seller")
    
    # Create property
    db_property = property.model_dump()
    db_property["created_by"] = current_user.user_id
    db_property["created_at"] = datetime.now(timezone.utc)
    db_property["last_updated"] = datetime.now(timezone.utc)
    db_property["images_urls"] = saved_files
    db_property["mls_num"] = random.randint(100000, 999999)

    property_sql = load_sql("property/create_property.sql")
    property_result = db.execute(text(property_sql), db_property)
    new_property_id = property_result.scalar()

    # Create property address
    address_data = address.model_dump()
    address_data["created_at"] = datetime.now(timezone.utc)
    address_data["created_by"] = current_user.user_id
    address_data["property_id"] = new_property_id
    
    address_sql = load_sql("address/create_property_address.sql")
    address_result = db.execute(text(address_sql),address_data)
    address_id = address_result.scalar()

    # Create property additional
    db_additional = additional.model_dump()
    db_additional["property_id"] = new_property_id

    additional_sql = load_sql("additional/create_additional.sql")
    additional_result = db.execute(text(additional_sql), db_additional)
    new_additional_id = additional_result.scalar()

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
    additional_sql = load_sql("additional/get_additional_by_id.sql")

    owner_id = property.owner_id
    owner_result = db.execute(text(user_sql), {"user_id": owner_id}).mappings().first()
    owner_roles_result = db.execute(text(role_sql), {"user_id": owner_id}).mappings().first()
    owner_roles = [key for key, value in owner_roles_result.items() if value is True and key in UserRole.__members__] if owner_roles_result else []
    if owner_result:
        owner_data = dict(owner_result)
        owner_data["roles"] = owner_roles
        owner_obj = UserOut(
            **owner_data,
            address = AddressOut(**owner_result) if owner_result.get("address_id") else None,
        )
    else:
        owner_obj = None

    created_by_id = current_user.user_id
    created_by_result = db.execute(text(user_sql), {"user_id": created_by_id}).mappings().first()
    created_by_roles_result = db.execute(text(role_sql), {"user_id": created_by_id}).mappings().first()
    created_by_roles = [key for key, value in created_by_roles_result.items() if value is True and key in UserRole.__members__] if created_by_roles_result else []
    
    if created_by_result:
        created_by_data = dict(created_by_result)
        created_by_data["roles"] = created_by_roles
        created_by_obj = UserOut(
            **created_by_data,
            address = AddressOut(**created_by_result) if created_by_result.get("address_id") else None,
        )
    else:
        created_by_obj = None

    property_out_data = dict(created_property)
    property_out_data["address"] = address_obj
    property_out_data["owner"] = owner_obj
    property_out_data["created_by_user"] = created_by_obj

    created_additional = db.execute(text(additional_sql), {"property_id": new_property_id}).mappings().first()
    property_details = PropertyOut(
        **property_out_data,
        additional=created_additional
    )

    return {
        "message": "property created successfully",
        "property": property_details,
    }

@router.get("", response_model=PaginatedProperties, status_code=status.HTTP_200_OK)
def get_all_properties(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_sql = "SELECT COUNT(*) FROM properties"
    total = db.execute(text(total_sql)).scalar()
    total_pages = (total + per_page - 1) // per_page
    
    sql = load_sql("property/get_all_properties.sql")
    result = db.execute(text(sql), {'limit': per_page, 'offset': (page - 1) * per_page})

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
            roles=created_by_roles,
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
            roles=owner_roles,
            created_by=row["owner_created_by"],  # from users.created_by
            created_at=row["owner_created_at"] 
        )
            
        property = PropertyOut(
            property_id=row["property_id"],
            description=row["description"],
            price=row["price"],
            property_type=row["property_type"],
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
            images_urls=row["images_urls"],
            mls_num=row["mls_num"],
            
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
            ),
            additional= AdditionalOut(
                **row
            )
        )
        properties.append(property)

    return {
        "data": properties,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

@router.get("/my-properties", response_model=List[PropertyOut], status_code=status.HTTP_200_OK)
def my_properties(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("property/get_my_property.sql")
    result = db.execute(text(sql), {"created_by": current_user.user_id})

    properties = []
    for row in result.mappings():
        # Build roles for created_by and owner
        created_by_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"created_by_{role}") is True
        ]
        owner_roles = [
            role for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
            if row.get(f"owner_{role}") is True
        ]
        # Build nested UserOut objects
        created_by = UserOut(
            user_id=row["created_by_user_id"],
            first_name=row["created_by_first_name"],
            last_name=row["created_by_last_name"],
            email=row["created_by_email"],
            phone_number=row["created_by_phone_number"],
            roles=created_by_roles,
            created_by=row["created_by_created_by"],
            created_at=row["created_by_created_at"]
        )
        owner = UserOut(
            user_id=row["owner_user_id"],
            first_name=row["owner_first_name"],
            last_name=row["owner_last_name"],
            email=row["owner_email"],
            phone_number=row["owner_phone_number"],
            roles=owner_roles,
            created_by=row["owner_created_by"],
            created_at=row["owner_created_at"]
        )
        # Build address
        address = AddressOut(
            address_id=row["address_address_id"],
            floor=row["address_floor"],
            apt=row["address_apt"],
            area=row["address_area"],
            city=row["address_city"],
            county=row["address_county"],
            created_at=row["address_created_at"],
            created_by=row["address_created_by"],
            building_num=row["address_building_num"],
            street=row["address_street"]
        )
        # Build PropertyOut
        property = PropertyOut(
            property_id=row["property_id"],
            description=row["description"],
            price=row["price"],
            property_type=row["property_type"],
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
            images_urls=row["images_urls"],
            owner=owner,
            created_by_user=created_by,
            address=address
        )
        properties.append(property)
    return properties

@router.get("/{property_id:int}", status_code=status.HTTP_200_OK)
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
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
        additional=AdditionalOut(**row)
    )

    return {"property": property}

@router.put("/{property_id}")
def update_property_by_id(
    property_id : int ,
    property_data: PropertyUpdate = Depends(PropertyUpdate.as_form),
    address_data: AddressUpdate = Depends(AddressUpdate.as_form),
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
    if address_data:
        db_address = {
            k: v for k, v in address_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if db_address:
            db_address["address_id"] = property["address_address_id"]
            set_clause = ", ".join(f"{k} = :{k}" for k in db_address if k != "address_id")
            sql = f"UPDATE addresses SET {set_clause} WHERE address_id = :address_id"
            db.execute(text(sql), db_address)


    #update property
    db_property = {
        k: v for k, v in property_data.model_dump(exclude_unset=True, exclude={"address"}).items()
        if v is not None
    }
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

    
@router.get("/status-options", tags=["Properties"])
def get_property_status_options(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]

    if "realtor" in current_user_role or "broker" in current_user_role or "admin" in current_user_role:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    return [status.value for status in PropertyStatus]