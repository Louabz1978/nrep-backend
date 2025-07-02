from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.routers.auth import get_current_user
from app import database, models
from app.utils.out_helper import build_user_out
from app.routers.agencies import AgencyOut
from app.routers.users import UserOut
from app.utils.file_helper import load_sql
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from app.utils.file_helper import load_sql
from sqlalchemy import text

router = APIRouter(
    prefix="/listing",
    tags=["Properties"]
)

class PropertyOut(BaseModel):
    property_id: int
    owner_id: int
    agent_id: Optional[int]
    address: str
    neighborhood: str
    city: str
    county: str
    description: str
    price: int
    property_type: Optional[str]
    floor: Optional[int]
    bedrooms: int
    bathrooms: float
    listing_agent_commission: float
    buyer_agent_commission: float
    area_space: int
    year_built: int
    latitude: float
    longitude: float
    status: str
    listed_date: date
    last_updated: datetime
    image_url: Optional[str]

    # Relationships
    owner: Optional[UserOut] = None
    agent: Optional[UserOut] = None

@router.post("/all-listings")
async def all_listings(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    properties = db.query(models.Property).options(
        joinedload(models.Property.agent).joinedload(models.User.agency)
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
async def my_listings(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    properties = db.query(models.Property).filter(models.Property.agent_id == current_user.user_id).all()
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
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "agent": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload a property. Agent role required."
        )

    new_property = models.Property(
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



# Defines a GET HTTP endpoint at the path '/{listing_id}'
# GET the resource identified by 'listing_id'
# Returns HTTP status code 200 with a JSON PropertyOut
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the listing does not exist
@router.get("/{listing_id}", response_model=PropertyOut, status_code=status.HTTP_200_OK)
def get_listing_by_id(
    listing_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
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


# Defines a DELETE HTTP endpoint at the path '/{listing_id}'
# Deletes the resource identified by 'listing_id'
# Returns HTTP status code 204 with a JSON message confirming successful deletion
# Raises HTTP 403 Forbidden if the user is not authorized as admin
# Raises HTTP 404 Not Found if the listing does not exist
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
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
