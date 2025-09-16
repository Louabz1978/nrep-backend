import json
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional

from app import database

from pytest import Session

from app import database

from ...models.user_model import User

from ...dependencies import get_current_user
from ...utils.file_helper import load_sql

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

UPLOAD_DIR = "static/contracts"

STATIC_DIR = os.path.join(os.getcwd(), "static")
CONTRACT_DIR = os.path.join(STATIC_DIR, "contracts")
os.makedirs(CONTRACT_DIR, exist_ok=True)

def load_data(path):
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail=f"❌ The file at '{path}' does not exist.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in file: {path}")

@router.get("/{mls}")
def get_contract_by_mls(
    mls: str,
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=404, detail="Not authorized")
    
    folder_dir = os.path.join(UPLOAD_DIR, f"{mls}.json")

    result = load_data(folder_dir)

    if not result:
        raise HTTPException(status_code=404, detail="Contract is empty.")
    
    return result

@router.post("/sign/{mls}/{receiver_id}", status_code=status.HTTP_201_CREATED)
async def create_signed_contract(
    mls: str,
    receiver_id: int,
    contract_json: str = Form(...),
    pdf_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    contract_data = json.loads(contract_json)
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    # File path: static/contracts/{mls}.json
    file_path = os.path.join(CONTRACT_DIR, f"{mls}.json")

    # Save contract JSON to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(contract_data, f, ensure_ascii=False, indent=4)

    return {
        "message": "Contract saved successfully"
    }

@router.put("/contract/close/{mls}", status_code=status.HTTP_200_OK)
def close_contract(
    mls: int, 
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False and roles["broker"] == False and roles["realtor"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if mls_num exists
    sql_check = load_sql("property/check_mls.sql")
    result = db.execute(text(sql_check), {"mls": mls}).mappings().first()
    if not result:
        raise HTTPException(status_code=404, detail="Property with this MLS number not found")

    # Update property status to 'closed'
    sql_update = load_sql("property/close_contract.sql")
    updated_property = db.execute(text(sql_update), {"mls": mls}).mappings().first()
    if not updated_property:
        raise HTTPException(status_code=404, detail="Failed to update property status")

    # Commit the transaction
    db.commit()

    return {
        "message": "Contract closed successfully"
    }
