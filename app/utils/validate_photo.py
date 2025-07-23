import os
import shutil
from pathlib import Path
from fastapi import UploadFile,  HTTPException

UPLOAD_DIR = "uploaded_photos"

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

MAX_FILE_SIZE_MB = 1  # 1 MB

def validate_photo(file: UploadFile):
    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
    # if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a supported image type.")

    # Check size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' exceeds {MAX_FILE_SIZE_MB}MB size limit.")
    
def save_photos(address, photos: list[UploadFile]):
    valid_photos = []

    # Validate photos (size/type)
    for photo in photos:
        try:
            validate_photo(photo)
            valid_photos.append(photo)
        except HTTPException as e:
            print(f"Skipping {photo.filename}: {e.detail}")

    if not valid_photos:
        raise HTTPException(status_code=400, detail="No valid photos to upload.")

    # Create a safe folder name {city-code}-{building-num}-{apt-num}-{floor-num}
    folder_name = f"{address.city}_{address.building_num}_{address.apt}_{address.floor}"
    save_dir = Path(UPLOAD_DIR) / folder_name
    os.makedirs(save_dir, exist_ok=True)

    # Save valid photos
    saved_files = []
    for photo in valid_photos:
        file_path = save_dir / photo.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        saved_files.append(str(file_path))

    return saved_files
