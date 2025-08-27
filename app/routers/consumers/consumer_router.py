from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timezone

from app import database
from app.dependencies import get_current_user
from app.models.user_model import User
from app.routers.consumers.consumer_pagination import PaginatedConsumer
from app.utils.file_helper import load_sql

from app.routers.consumers.consumer_out import ConsumerOut
from app.routers.consumers.consumer_create import ConsumerCreate
from app.routers.consumers.consumer_update import ConsumerUpdate

from app.models.user_model import User

router = APIRouter(prefix="/consumers", tags=["Consumers"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_consumer(
    consumer: ConsumerCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    current_user_roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    current_user_role_list = [key for key, value in current_user_roles.items() if value]

    if not any(role in current_user_role_list for role in ["admin", "broker", "realtor"]):
        raise HTTPException(status_code=403, detail="Not authorized to create consumers")

    db_consumer = consumer.model_dump(exclude={"roles"})
    db_consumer["created_by"] = current_user.user_id
    db_consumer["created_at"] = datetime.now(timezone.utc)
    db_consumer["created_by_type"] = current_user_role_list[1]
    params = {**db_consumer}

    sql = load_sql("consumer/create_consumer.sql")
    new_consumer_id = db.execute(text(sql), params).scalar()
    db.commit()

    sql = load_sql("consumer/get_consumer_by_id.sql")
    created_consumer = db.execute(text(sql), {"consumer_id": new_consumer_id}).mappings().first()

    consumer_details = ConsumerOut(**created_consumer, address=None)

    return {
        "message": "Consumer created successfully",
        "consumer": consumer_details  
    }

@router.get("/{consumer_id:int}", status_code=status.HTTP_200_OK)
def get_consumer_by_id(
    consumer_id: int, 
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user),
):
    sql = load_sql("consumer/get_consumer_by_id.sql")
    consumer_data = db.execute(text(sql), {"consumer_id": consumer_id}).mappings().first()

    if consumer_data is None:
        raise HTTPException(status_code=404, detail="consumer not found")
    
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if not (
        roles["admin"] == True
        or current_user.user_id == consumer_data["created_by"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    consumer = ConsumerOut(**consumer_data)
    return consumer

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

    consumer_out = ConsumerOut(**row)

    return {"message": "Consumer updated successfully", "consumer": consumer_out}

@router.delete("/{consumer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumer(
    consumer_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    role_sql = load_sql("role/get_user_roles.sql")
    roles = db.execute(text(role_sql), {"user_id": current_user.user_id}).mappings().first()
    if roles["admin"] == False:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    sql = load_sql("consumer/get_consumer_by_id.sql")
    result = db.execute(text(sql), {"consumer_id": consumer_id})
    consumer = result.mappings().first()
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")
    
    delete_sql = load_sql("consumer/delete_consumer.sql")
    db.execute(text(delete_sql), {"consumer_id": consumer_id})
    db.commit()
    
    return {"message": "Consumer deleted successfully"}
@router.get("/", response_model=PaginatedConsumer, status_code=status.HTTP_200_OK)
def get_all_consumers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    sort_by: str = Query("consumer_id", regex="^(consumer_id|surname|father_name|name|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),

    name: Optional[str] = Query(None),
    father_name: Optional[str] = Query(None),
    surname: Optional[str] = Query(None),
    mother_name_surname: Optional[str] = Query(None),
    place_birth: Optional[str] = Query(None),
    date_birth: Optional[date] = Query(None),
    registry: Optional[str] = Query(None),
    national_number: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    created_by_type: Optional[str] = Query(None),
    created_at: Optional[date] = Query(None),

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
    params = {
        "user_id": current_user.user_id,
        "role": role,
        "name": f"%{name}%" if name else None,
        "father_name": f"%{father_name}%" if father_name else None,
        "surname": f"%{surname}%" if surname else None,
        "mother_name_surname": f"%{mother_name_surname}%" if mother_name_surname else None,
        "place_birth": f"%{place_birth}%" if place_birth else None,
        "date_birth": date_birth,
        "registry": f"%{registry}%" if registry else None,
        "national_number": f"%{national_number}%" if national_number else None,
        "email": f"%{email}%" if email else None,
        "phone_number": f"%{phone_number}%" if phone_number else None,
        "created_by": created_by,
        "created_by_type": f"%{created_by_type}%" if created_by_type else None,
        "created_at": created_at,
    }

    # total count
    total_sql = load_sql("consumer/count_all_consumers.sql")
    total = db.execute(text(total_sql), params).scalar()
    total_pages = (total + per_page - 1) // per_page
    sql = load_sql("consumer/get_all_consumers.sql").format(
        sort_by=sort_by,
        sort_order=sort_order
    )
    params.update({
        "limit": per_page,
        "offset": (page - 1) * per_page
    })

    result = db.execute(text(sql), params)
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
