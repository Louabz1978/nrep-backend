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

router = APIRouter(
    prefix="/listing",
    tags=["Properties"]
)

# Defines a POST HTTP endpoint at the path '/listing'
# Creates a new property listing
# Returns HTTP 201 Created with a JSON message confirming success and the new_listing_id
# Raises HTTP 403 Forbidden if the user is not authorized (admin, broker, or realtor)
# Raises HTTP 400 Bad Request if:
#   - The user role is 'realtor' and agent_id is missing, invalid, or not a realtor
#   - The owner_id does not exist
#   - The specified owner is not a seller
@router.post("", status_code=status.HTTP_201_CREATED)
def create_listing(
    listing: PropertyCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "broker", "realtor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    #validate agent_id

    agent = listing.agent_id
    if current_user.role != "realtor":
        if agent is None:
            raise HTTPException(status_code=400, detail="agent_id is required")
        
        sql = load_sql("get_user_by_id.sql")
        result = db.execute(text(sql), {"user_id": agent})
        row = result.mappings().first()
        if not row :
            raise HTTPException(status_code=400, detail="invalid agent_id")
        if row["role"] != "realtor":
            raise HTTPException(status_code=400, detail="agent must be realtor")
    else:
        agent = current_user.user_id

    #validate owner_id

    sql = load_sql("get_user_by_id.sql")
    result = db.execute(text(sql), {"user_id": listing.owner_id})
    row = result.mappings().first()
    if not row :
        raise HTTPException(status_code=400, detail="invalid seller_id")
    if row["role"] != "seller":
        raise HTTPException(status_code=400, detail="owner must be seller")

    db_listing = Property(
        owner_id = listing.owner_id,
        agent_id = agent,
        address = listing.address,
        neighborhood = listing.neighborhood,
        city = listing.city,
        county = listing.county,
        description = listing.description,
        price = listing.price,
        property_type = listing.property_type,
        floor = listing.floor,
        bedrooms = listing.bedrooms,
        bathrooms = listing.bathrooms,
        listing_agent_commission = listing.listing_agent_commission,
        buyer_agent_commission = listing.buyer_agent_commission,
        area_space = listing.area_space,
        year_built = listing.year_built,
        latitude = listing.latitude,
        longitude = listing.longitude,
        status = listing.status,
        listed_date = listing.listed_date,
        last_updated = listing.last_update,
        image_url = listing.image_url
    )

    listing_data = {
        column.name: getattr(db_listing, column.name)
        for column in db_listing.__table__.columns
        if column.name !="property_id"
    }

    sql = load_sql("create_listing.sql")
    result = db.execute(text(sql), listing_data)
    new_listing_id = result.scalar()

    db.commit()

    return {"message" : "Listing created successfully", "listing_id": new_listing_id}

# Defines a GET HTTP endpoint at the path '/listing/{listing_id}'
# GET the resource identified by 'listing_id'
# Returns HTTP status code 200 with a JSON PropertyOut
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the listing does not exist
@router.get("/{listing_id}", response_model=PropertyOut, status_code=status.HTTP_200_OK)
def get_listing_by_id(
    listing_id: int, 
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    
    if current_user.role != "admin" and current_user.role != "broker" and current_user.role != "realtor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("get_listing_by_id.sql")
    result = db.execute(text(sql), {"listing_id": listing_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    property = PropertyOut(
        **row,
        owner=build_user_out(row, "owner_"),
        agent=build_user_out(row, "agent_")
    )
    return property

@router.post("/all-listings")
async def all_listings(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    properties = db.query(Property).options(
        joinedload(Property.agent).joinedload(User.agency)
    ).all()
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
            "status":prop.status,
            "address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "price": prop.price,
            "bedrooms": prop.bedrooms,
            "bathrooms": prop.bathrooms,
            "listing_agent": prop.agent,
            "broker": prop.agent.agency.name, # type: ignore
            "listed_date": prop.listed_date,
            "listing_agent_commission":prop.listing_agent_commission,
            "buyer_agent_commission":prop.buyer_agent_commission,
            "area_sqft": prop.area_sqft,
            "images": images,  
        })

    return property_list

@router.post("/my-listings")
async def my_listings(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    properties = db.query(Property).filter(Property.agent_id == current_user.user_id).all()
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
            "listing_agent_commission":prop.listing_agent_commission,
            "buyer_agent_commission":prop.buyer_agent_commission,
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
    listing_agent_commission: float = Form(...),
    buyer_agent_commission: float = Form(...),
    area_sqft: int = Form(...),
    lot_size_sqft: int = Form(...),
    year_built: int = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "agent": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload a property. Agent role required."
        )

    new_property = Property(
        agent_id=current_user.user_id,
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
        listing_agent_commission=listing_agent_commission,
        buyer_agent_commission=buyer_agent_commission,
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

# Defines a DELETE HTTP endpoint at the path '/listing/{listing_id}'
# Deletes the resource identified by 'listing_id'
# Returns HTTP status code 204 with a JSON message confirming successful deletion
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the listing does not exist
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sql = load_sql("get_listing_by_id.sql")
    result = db.execute(text(sql), {"listing_id": listing_id})
    listing = result.mappings().first()
    if not listing:
        raise HTTPException(status_code=404, detail="listing not found")

    delete_sql = load_sql("delete_listing.sql")
    db.execute(text(delete_sql), {"property_id": listing_id})
    
    db.commit()
    return {"message": "listing deleted successfully"}
