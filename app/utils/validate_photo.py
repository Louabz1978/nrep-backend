import os
import shutil
from pathlib import Path
from fastapi import UploadFile,  HTTPException
from urllib.parse import urljoin, urlparse

UPLOAD_DIR = "static/properties_photos"

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
    
def save_photos(mls_num, photos: list[UploadFile], base_url, main_photo: str):
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

    # Create a folder with name to mls_num
    folder_dir = Path(UPLOAD_DIR + "/" + str(mls_num))
    os.makedirs(folder_dir, exist_ok=True)

    # Save valid photos
    saved_files = []
    for photo in valid_photos:
        file_path = folder_dir / photo.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Add base url to photo
        file_url = urljoin(base_url + f"/{UPLOAD_DIR}/{mls_num}/", photo.filename)

        # Match main_photo
        is_main = False
        if main_photo == photo.filename:
            is_main = True

        saved_files.append({
            "is_main": is_main,
            "url": file_url
        })

    return saved_files

def update_photos(
        mls_num,
        db_images_property,
        new_photos: list[UploadFile],
        update_photos_data,
        base_url,
        main_photo: str
    ):
    folder_dir = Path(f"static/properties_photos/{mls_num}")
    os.makedirs(folder_dir, exist_ok=True)

    updated_db_images = []

    # Step 1: Only clean up files if update_photos_data is provided
    if update_photos_data is not None:
        for file in folder_dir.iterdir():
            if file.is_file():
                if file.name not in update_photos_data:
                    print(f"Removing unused file: {file.name}")
                    file.unlink()

                    # Remove from db_images_property as well
                    db_images_property = [
                        img for img in db_images_property if not img["url"].endswith(file.name)
                    ]
                else:
                    # Retain in updated_db_images
                    for img in db_images_property:
                        if img["url"].endswith(file.name):
                            updated_db_images.append(img)
                            break
    else:
        # If no update_photos_data sent, keep all current db images
        updated_db_images = db_images_property.copy()

    # Step 2: Save new photos
    saved_files = []
    if new_photos:
        for photo in new_photos:
            file_path = folder_dir / photo.filename
            with open(file_path, "wb") as f:
                f.write(photo.file.read())

            file_url = f"{base_url}/static/properties_photos/{mls_num}/{photo.filename}"

            # Get metadata for the photo if available
            meta = next((item for item in (update_photos_data or []) if item == photo.filename), {})
            is_main = meta.get("is_main", False)

            saved_files.append({
                "url": file_url,
                "is_main": is_main
            })

    # Step 3: Handle main_photo if exists (update is_main flag)
    if main_photo:
        for image in updated_db_images + saved_files:
            image["is_main"] = image["url"].endswith(main_photo)

    return updated_db_images + saved_files
