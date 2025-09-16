import json
from fastapi import APIRouter, Depends, HTTPException, status
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import database

from ...models.user_model import User

from ...dependencies import get_current_user
from ...utils.file_helper import load_sql

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

DATA_FILE = Path("static/contracts/data.json")

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

    return "Contract closed successfully"
