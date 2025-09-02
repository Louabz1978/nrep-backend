from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database

from ...utils.file_helper import load_sql
from ...models.user_model import User
from ...dependencies import get_current_user
from ..roles.roles_update import RolesUpdate

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_role(
    user_id: int,
    role_data: RolesUpdate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_sql = load_sql("user/get_user_by_id.sql")
    user = db.execute(text(user_sql), {"user_id": user_id}).mappings().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    #update address
    db_roles = role_data.model_dump(exclude_unset=True)
    db_roles["user_id"] = user_id
    set_clause = ", ".join(f"{k} = :{k}" for k in db_roles)
    sql = f"UPDATE ROLES SET {set_clause} WHERE user_id = :user_id RETURNING user_id;"
    updated_user_id = db.execute(text(sql), db_roles).scalar()
    
    db.commit()
    return {"message": "Role updated successfully", "user_id": updated_user_id}
