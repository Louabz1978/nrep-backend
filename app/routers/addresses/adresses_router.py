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
from app.utils.file_helper import load_sql

from ...dependencies import get_current_user

router = APIRouter(
    prefix="/address",
    tags=["Adresses"]
)

@router.get("", status_code=status.HTTP_200_OK)
def get_address(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    sql = load_sql("address/get_address.sql")
    result = db.execute(text(sql), {'address_id': current_user.address_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    address = AddressOut(**row)
    return address