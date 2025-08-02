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
    
def save_photos(mls_num, photos: list[UploadFile], base_url, metadata: list[dict]):
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

        # Match metadata for is_main
        meta = next((m for m in metadata if m["filename"] == photo.filename), {})
        is_main = meta.get("is_main", False)

        saved_files.append({
            "is_main": is_main,
            "url": file_url
        })

    return saved_files

def update_photos(mls_num, new_photos: list[UploadFile], update_photos_data, base_url, metadata: list[dict]):
    saved_files = []

    # Create a folder with name to mls_num
    folder_dir = Path(UPLOAD_DIR + "/" + str(mls_num))
    os.makedirs(folder_dir, exist_ok=True)

    # Removed photos that not exist in old_photos
    if update_photos_data:
        keep_filenames = set()

        # Extract filenames from URLs
        for url in update_photos_data:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            keep_filenames.add(filename)

        # Loop through files in the folder
        for file in folder_dir.iterdir():
            if file.is_file() and file.name not in keep_filenames:
                print(f"Removing unused file: {file.name}")
                file.unlink()
            else:
                # Add base url to photo
                file_url = urljoin(base_url + f"/{UPLOAD_DIR}/{mls_num}/", file.name)

                # Match metadata for is_main
                meta = next((m for m in metadata if m["filename"] == file.name), {})
                is_main = meta.get("is_main", False)
                
                saved_files.append({
                    "is_main": is_main,
                    "url": file_url
                })

    # Validate photos (size/type)
    if new_photos:
        valid_photos = []
        for photo in new_photos:
            try:
                validate_photo(photo)
                valid_photos.append(photo)
            except HTTPException as e:
                print(f"Skipping {photo.filename}: {e.detail}")

        if not valid_photos:
            raise HTTPException(status_code=400, detail="No valid photos to upload.")

        # Save valid photos
        for photo in valid_photos:
            file_path = folder_dir / photo.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            
            # Add base url to photo
            file_url = urljoin(base_url + f"/{UPLOAD_DIR}/{mls_num}/", photo.filename)

            # Match metadata for is_main
            meta = next((m for m in metadata if m["filename"] == photo.filename), {})
            is_main = meta.get("is_main", False)
            
            saved_files.append({
                "is_main": is_main,
                "url": file_url
            })
            
    return saved_files
