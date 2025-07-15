from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database
from ...utils.file_helper import load_sql
from ...models.user_model import User
from ...dependencies import get_current_user
from ..roles.roles_create import RolesCreate

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_role(
    user_id: int,
    role_data: RolesCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    
    user_sql = load_sql("get_user_by_id.sql")
    cur_user = db.execute(text(user_sql), {"user_id": current_user.user_id}).mappings().first()
    role_sql = load_sql("get_user_roles.sql")
    roles = db.execute(text(role_sql), {"role_id": cur_user["role_id"]}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_sql = load_sql("get_user_by_id.sql")
    user = db.execute(text(user_sql), {"user_id": user_id}).mappings().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    sql = load_sql("update_role.sql")
    db.execute(
        text(sql), 
        {
            "role_id": user["role_id"],
            "admin": role_data.admin,
            "broker": role_data.broker,
            "realtor": role_data.realtor,
            "seller": role_data.seller,
            "buyer": role_data.buyer,
            "tenant": role_data.tenant
        })
    
    db.commit()
    return {"message": "Role updated successfully", "user_id": user_id}