import json
import os
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pathlib import Path

from pydantic import BaseModel
from pytest import Session

from app import database

from ...models.user_model import User

from ...dependencies import get_current_user

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

DATA_FILE = Path("static/contracts/data.json")
STATIC_DIR = os.path.join(os.getcwd(), "static")
CONTRACT_DIR = os.path.join(STATIC_DIR, "contracts")
os.makedirs(CONTRACT_DIR, exist_ok=True)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

@router.get("/{mls}")
def get_contract_by_mls(
    mls: str,
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=404, detail="Not authorized")
    
    data = load_data()
    result = list(filter(lambda p: p["mls"] == mls, data))
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return result[0]

@router.post("/sign/{mls}/{receiver_id}", status_code=status.HTTP_201_CREATED)
async def create_signed_contract(
    mls: str,
    receiver_id: int,
    contract_data: dict = Body(...),
    current_user: User = Depends(get_current_user)
):
    if not current_user.roles.admin and not current_user.roles.broker and not current_user.roles.realtor:
        raise HTTPException(status_code=403, detail="Not authorized")

    # File path: static/contracts/{mls}.txt
    file_path = os.path.join(CONTRACT_DIR, f"{mls}.txt")

    # Save contract JSON to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(contract_data, f, ensure_ascii=False, indent=4)

    # Public URL for static serving
    file_url = f"/static/contracts/{mls}.txt"

    return {
        "message": "Contract saved successfully",
        "mls": mls,
        "receiver_id": receiver_id,
        "file_url": file_url,
        "email": contract_data.get("email")
    }