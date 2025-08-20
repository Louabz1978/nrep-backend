from fastapi import APIRouter, Depends, HTTPException,status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import database
from app.dependencies import get_current_user
from app.models.user_model import User
from app.routers.consumers.consumer_pagination import PaginatedConsumer
from app.utils.file_helper import load_sql
from app.routers.consumers.consumer_out import ConsumerOut
from app.routers.consumers.consumer_update import ConsumerUpdate

router = APIRouter(prefix="/consumers", tags=["Consumers"])


@router.put("/{consumer_id}")
def update_consumer_by_id(
    consumer_id: int,
    consumer_data: ConsumerUpdate = Depends(ConsumerUpdate.as_form),
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    sql = load_sql("consumer/get_consumer_by_id.sql")
    consumer_row = db.execute(text(sql), {"consumer_id": consumer_id}).mappings().first()
    if not consumer_row:
        raise HTTPException(status_code=404, detail="Consumer not found")

    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role_list = [key for key, value in current_user_roles.items() if value]
    if not (
        "admin" in current_user_role_list
        or current_user.user_id == consumer_row["created_by"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized to update this consumer")

    db_consumer_update = {
        k: v for k, v in consumer_data.model_dump(exclude_unset=True).items()
        if v is not None
    }
    db_consumer_update["consumer_id"] = consumer_id

    if not db_consumer_update:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    set_clause = ", ".join(f"{k} = :{k}" for k in db_consumer_update if k != "consumer_id")
    sql = f"""
        UPDATE consumers
        SET {set_clause}
        WHERE consumer_id = :consumer_id
        RETURNING consumer_id;
    """
    updated_consumer_id = db.execute(text(sql), db_consumer_update).scalar()
    db.commit()

    sql = load_sql("consumer/get_consumer_by_id.sql")
    row = db.execute(text(sql), {"consumer_id": updated_consumer_id}).mappings().first()

    roles = [
        role
        for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
        if row.get(role)
    ]

    consumer_out = ConsumerOut(**row)

    return {"message": "Consumer updated successfully", "consumer": consumer_out}


@router.get("/consumers", response_model=PaginatedConsumer, status_code=status.HTTP_200_OK)
def get_all_consumers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    sort_by: str = Query("consumer_id", regex="^(consumer_id|surname|father_name|name|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    
    if roles["admin"] == False and roles["broker"] == False and roles["realtor"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if roles["admin"] == True:
        role = 'admin'
    elif roles["broker"] == True:
        role = 'broker'
    else:
        role = 'realtor'
    # total count
    total_sql = load_sql("consumer/count_all_consumers.sql")
    total = db.execute(text(total_sql), {
        "role" : role,
    })
    total_pages = (total + per_page - 1) // per_page
    sql = load_sql("consumer/get_all_consumers.sql")
    result = db.execute(text(sql), {
        "role" : role,
        "limit": per_page,
        "offset": (page - 1) * per_page
    })

    consumers = [ConsumerOut(**row) for row in result.mappings()]

    return {
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "data": consumers
    }
