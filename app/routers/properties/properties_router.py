from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile, Query, Request
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import random
import json

from app import database

from ...utils.file_helper import load_sql
from ...utils.out_helper import build_user_out
from ...utils.random_generator import generate_unique_mls_num
from ...dependencies import get_current_user
from ...utils.validate_photo import save_photos, update_photos

from ...models.user_model import User

from ..users.roles_enum import UserRole

from ..users.user_out import UserOut
from ..consumers.consumer_out import ConsumerOut
from .property_out import PropertyOut
from .property_pagination import PaginatedProperties
from ..addresses.address_out import AddressOut
from ..addresses.address_update import AddressUpdate
from ..additional.additional_update import AdditionalUpdate

from .property_create import PropertyCreate
from .property_update import PropertyUpdate
from ..additional.additional_create import AdditionalCreate
from ..additional.additional_out import AdditionalOut
from ..addresses.address_create import AddressCreate

from ...utils.enums import PropertyStatus, PropertyTypes

router = APIRouter(
    prefix="/property",
    tags=["Properties"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_property(
    request: Request,
    property: PropertyCreate = Depends(PropertyCreate.as_form),
    additional: AdditionalCreate = Depends(AdditionalCreate.as_form),
    address: AddressCreate = Depends(AddressCreate.as_form),
    photos: List[UploadFile] = File(...),
    main_photo: str = Form(None),
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

    sql = load_sql("consumer/get_consumer_by_id.sql")
    owner_result = db.execute(text(sql), {"consumer_id": property.owner_id}).mappings().first()
    if not owner_result :
        raise HTTPException(status_code=400, detail="invalid owner_id")

    mls_num = generate_unique_mls_num(db)
    base_url = str(request.base_url)
    saved_files = save_photos(mls_num, photos, base_url, main_photo)

    # Create property
    db_property = property.model_dump()
    db_property["created_by"] = current_user.user_id
    db_property["created_at"] = datetime.now(timezone.utc)
    db_property["last_updated"] = datetime.now(timezone.utc)
    db_property["images_urls"] = json.dumps(saved_files)
    db_property["mls_num"] = mls_num

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
    
    consumer_sql = load_sql("consumer/get_consumer_by_id.sql")
    user_sql = load_sql("user/get_user_by_id.sql")
    role_sql = load_sql("role/get_user_roles.sql")
    additional_sql = load_sql("additional/get_additional_by_id.sql")

    owner_id = property.owner_id
    owner_result = db.execute(text(consumer_sql), {"consumer_id": owner_id}).mappings().first()
    owner_data = dict(owner_result)
    owner_obj = ConsumerOut(**owner_data)

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
    
    sort_by: str = Query("property_id", regex="^(property_id|status|mls_num|price|area|city|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    
    city: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    mls_num: Optional[int] = Query(None),
    status_filter: Optional[PropertyStatus] = Query(None),

    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    params = {
        # "created_by": current_user.user_id,
        "city": f"%{city}%" if city else None,
        "area": f"%{area}%" if area else None,
        "min_price": min_price,
        "max_price": max_price,
        "mls_num": f"%{mls_num}%" if mls_num else None,
        "status": status_filter.value if status_filter else None,
        "limit": per_page,
        "offset": (page - 1) * per_page
    }

    total_sql = "SELECT COUNT(*) FROM properties"
    total = db.execute(text(total_sql)).scalar()
    total_pages = (total + per_page - 1) // per_page
    
    sql = load_sql("property/get_all_properties.sql")
    sql = sql.format(sort_by=sort_by, sort_order=sort_order)
    result = db.execute(text(sql), params)

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

        owner = ConsumerOut(
            consumer_id=row["owner_consumer_id"],
            name=row["owner_name"],
            father_name=row["owner_father_name"],
            surname=row["owner_surname"],
            mother_name_surname=row["owner_mother_name_surname"],
            place_birth=row["owner_place_birth"],
            date_birth=row["owner_date_birth"],
            registry=row["owner_registry"],
            national_number=row["owner_national_number"],
            email=row["owner_email"],
            phone_number=row["owner_phone_number"],
            created_by=row["owner_created_by"],
            created_at=row["owner_created_at"],
            created_by_type=row["owner_created_by_type"]
        )
            
        property = PropertyOut(
            property_id=row["property_id"],
            description=row["description"],
            show_inst=row["show_inst"],
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
            trans_type=row["trans_type"],
            exp_date=row["exp_date"],
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

@router.get("/my-properties", response_model=PaginatedProperties, status_code=status.HTTP_200_OK)
def my_properties(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),

    sort_by: str = Query("property_id", regex="^(property_id|status|mls_num|price|area|city|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    
    city: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    mls_num: Optional[int] = Query(None),
    status_filter: Optional[PropertyStatus] = Query(None),

    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    params = {
        "created_by": current_user.user_id,
        "city": f"%{city}%" if city else None,
        "area": f"%{area}%" if area else None,
        "min_price": min_price,
        "max_price": max_price,
        "mls_num": f"%{mls_num}%" if mls_num else None,
        "status": status_filter.value if status_filter else None,
        "limit": per_page,
        "offset": (page - 1) * per_page
    }

    # Load SQL from files (SQL already has WHERE clauses with optional filters)
    total_sql = load_sql("property/count_my_property.sql")
    total = db.execute(text(total_sql), params).scalar()
    total_pages = (total + per_page - 1) // per_page

    sql = load_sql("property/get_my_property.sql")
    sql = sql.format(sort_by=sort_by, sort_order=sort_order)
    result = db.execute(text(sql), params)

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
        owner = ConsumerOut(
            consumer_id=row["owner_consumer_id"],
            name=row["owner_name"],
            father_name=row["owner_father_name"],
            surname=row["owner_surname"],
            mother_name_surname=row["owner_mother_name_surname"],
            place_birth=row["owner_place_birth"],
            date_birth=row["owner_date_birth"],
            registry=row["owner_registry"],
            national_number=row["owner_national_number"],
            email=row["owner_email"],
            phone_number=row["owner_phone_number"],
            created_by=row["owner_created_by"],
            created_at=row["owner_created_at"],
            created_by_type=row["owner_created_by_type"]
        )
        address = AddressOut(
            address_id=row["address_address_id"],
            floor=row["floor"],
            apt=row["apt"],
            area=row["area"],
            city=row["city"],
            county=row["county"],
            created_at=row["address_created_at"],
            created_by=row["address_created_by"],
            building_num=row["building_num"],
            street=row["street"]
        )
        additional = AdditionalOut(**row)

        property = PropertyOut(
            property_id=row["property_id"],
            description=row["description"],
            show_inst=row["show_inst"],
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
            trans_type=row["trans_type"],
            exp_date=row["exp_date"],
            created_at=row["created_at"],
            last_updated=row["last_updated"],
            images_urls=row["images_urls"],
            mls_num=row["mls_num"],
            owner=owner, 
            created_by_user=created_by,
            address=address,
            additional=additional
        )
        properties.append(property)

    return {
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "data": properties
    }
    
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

    nested_prefixes = ("created_by_", "address_")

    property_data = {
        k: v for k, v in row.items()
        if not any(k.startswith(prefix) for prefix in nested_prefixes)
    }
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

    consumer_sql = load_sql("consumer/get_consumer_by_id.sql")
    owner = db.execute(text(consumer_sql), {"consumer_id": row.owner_consumer_id}).mappings().first()
    
    property = PropertyOut(
        **property_data,
        owner=owner,
        created_by_user=build_user_out(row, "created_by_"),
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
        additional=AdditionalOut(**row)
    )

    return {"property": property}

@router.get("/mls/{mls:int}", status_code=status.HTTP_200_OK)
def get_property_by_mls(
    mls: int,
    db: Session = Depends(database.get_db),
    current_user : User = Depends(get_current_user)
):

    role_sql = load_sql("role/get_user_roles.sql")
    role_result = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key, value in role_result.items() if value]

    if "realtor" in current_user_role or "broker" in current_user_role or "admin" in current_user_role:
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("property/get_property_by_mls.sql")
    row = db.execute(text(sql), { "mls": mls}).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")

    nested_prefixes = ("created_by_", "address_")

    property_data = {
        k: v for k, v in row.items()
        if not any(k.startswith(prefix) for prefix in nested_prefixes)
    }
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

    consumer_sql = load_sql("consumer/get_consumer_by_id.sql")
    owner = db.execute(text(consumer_sql), {"consumer_id": row.owner_consumer_id}).mappings().first()
    
    property = PropertyOut(
        **property_data,
        owner=owner,
        created_by_user=build_user_out(row, "created_by_"),
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
        additional=AdditionalOut(**row)
    )

    return {"property": property}

@router.put("/{property_id}")
def update_property_by_id(
    request: Request,
    property_id : int ,
    property_data: PropertyUpdate = Depends(PropertyUpdate.as_form),
    address_data: AddressUpdate = Depends(AddressUpdate.as_form),
    additional_data: AdditionalUpdate = Depends(AdditionalUpdate.as_form),
    photos: Optional[List[UploadFile]] = File(None),
    main_photo: Optional[str] = Form(None),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    # Get property
    sql = load_sql("property/get_property_by_id.sql")
    property = db.execute(text(sql), {"property_id": property_id}).mappings().first()
    if not property:
        raise HTTPException( status_code= 404 , detail="property not found")
    
    # Authorization check
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role = [key for key,value in current_user_roles.items() if value]
    if not (
        "admin" in current_user_role
        or ("broker" in current_user_role and (current_user.user_id in [ property["created_by_user_id"], property["created_by_created_by"] ] ) )
        or ("realtor" in current_user_role and current_user.user_id == property["created_by_user_id"])
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # owner_id check
    if property_data.owner_id or property_data.owner_id == 0:
        consumer_sql = load_sql("consumer/get_consumer_by_id.sql")
        owner_result = db.execute(text(consumer_sql), {"consumer_id": property_data.owner_id}).mappings().first()
        
        if not owner_result:
            raise HTTPException(status_code=404, detail="Owner not found")
        
        owner = ConsumerOut(**owner_result)

    base_url = str(request.base_url)
    saved_files = update_photos(property.mls_num, property['images_urls'], photos, property_data.preserve_images, base_url, main_photo)
    del property_data.preserve_images

    # Update address
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

    # Update Additional
    if additional_data:
        db_additional = {
            k: v for k, v in additional_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if db_additional:
            db_additional["additional_id"] = property["additional_id"]
            set_clause = ", ".join(f"{k} = :{k}" for k in db_additional if k != "additional_id")
            sql = f"UPDATE additional SET {set_clause} WHERE additional_id = :additional_id"
            db.execute(text(sql), db_additional)

    # Update property
    db_property = {
        k: v for k, v in property_data.model_dump(exclude_unset=True, exclude={"address"}).items()
        if v is not None
    }
    db_property["property_id"] = property_id
    if property_data.status != property["status"]:
        db_property["last_updated"] = datetime.now()
    if saved_files:
        db_property['images_urls'] = json.dumps(saved_files)
        
    set_clause = ", ".join(f"{k} = :{k}" for k in db_property)
    
    sql = f"UPDATE PROPERTIES SET {set_clause} WHERE property_id= :property_id RETURNING property_id;"
    updated_property_id = db.execute(text(sql), db_property).scalar()
    db.commit()

    # Fetch property data
    sql = load_sql("property/get_property_by_id.sql")
    row = db.execute(text(sql), {"property_id": updated_property_id}).mappings().first()
    nested_prefixes = ("created_by_", "address_")
    property_data = {
        k: v for k, v in row.items()
        if not any(k.startswith(prefix) for prefix in nested_prefixes)
    }
    address_data = {k[len("address_"):]: v for k, v in row.items() if k.startswith("address_")}

    consumer_sql = load_sql("consumer/get_consumer_by_id.sql")
    owner = db.execute(text(consumer_sql), {"consumer_id": row.owner_consumer_id}).mappings().first()
    
    property_details = PropertyOut(
        **property_data,
        owner=owner,
        created_by_user=build_user_out(row, "created_by_"),
        address=AddressOut(**address_data) if address_data.get("address_id") else None,
        additional=AdditionalOut(**row)
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

@router.get("types_option")
def get_property_type_options(
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

    return [types.value for types in PropertyTypes]
