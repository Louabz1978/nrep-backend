from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.routers.auth import get_current_user
from app import database, models
import os
import shutil

router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)

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

@router.get("/details/{property_id}")
def get_property_details(property_id: int, db: Session = Depends(database.get_db)):
    property = db.query(models.Property)\
    .options(joinedload(models.Property.agent).joinedload(models.User.agency))\
    .filter(models.Property.property_id == property_id).first()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Find images in folder
    images_folder = f"property_images/{property.property_id}"
    if os.path.exists(images_folder):
        images = sorted(
            [f"/{images_folder}/{img}" for img in os.listdir(images_folder)
             if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        )
    else:
        images = []

    return {
        "property_id": property.property_id,
        "agent_id":property.agent_id,
        "address": property.address,
        "city": property.city,
        "state": property.state,
        "price": property.price,
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "listing_agent_commission": property.listing_agent_commission,
        "buyer_agent_commission": property.buyer_agent_commission,
        "area_sqft": property.area_sqft,
        "lot_size_sqft": property.lot_size_sqft,
        "year_built": property.year_built,
        "zip_code": property.zip_code,
        "latitude": property.latitude,
        "longitude": property.longitude,
        "property_type": property.property_type,
        "status": property.status,
        "description": property.description,
        "listed_date":property.listed_date,
        "last_updated":property.last_updated,
        "images": images, 
        "agent": {
        "first_name": property.agent.first_name if property.agent else None,
        "last_name": property.agent.last_name if property.agent else None,
        "email": property.agent.email if property.agent else None,
        "phone_number": property.agent.phone_number if property.agent else None,
        "lic_num": property.agent.lic_num if property.agent else None,
        "agency": {
            "name": property.agent.agency.name if property.agent and property.agent.agency else "N/A",
            "phone_number": property.agent.agency.phone_number if property.agent and property.agent.agency else "N/A",
            "agency_lic": property.agent.agency.agency_lic if property.agent and property.agent.agency else "N/A"
        }
}

    }


