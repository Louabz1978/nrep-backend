import json
from fastapi import APIRouter, Depends, HTTPException, status
from pathlib import Path

from ...models.user_model import User

from ...dependencies import get_current_user

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