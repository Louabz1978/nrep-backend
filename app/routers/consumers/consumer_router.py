from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone

from app import database
from app.dependencies import get_current_user
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

    if not ("admin" in current_user_role_list or "broker" in current_user_role_list):
        raise HTTPException(status_code=403, detail="Not authorized to create consumers")

    db_consumer = consumer.model_dump(exclude={"roles"})
    db_consumer["created_by"] = current_user.user_id
    db_consumer["created_at"] = datetime.now(timezone.utc)
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
    realtor_ids = db.execute(text("""SELECT u.user_id FROM users u LEFT JOIN roles r ON r.user_id = u.user_id
                WHERE u.created_by = :broker_id AND r.realtor = TRUE"""),
                {"broker_id": current_user.user_id}).scalars().all()
    if not (
        roles["admin"] == True
        or (roles["realtor"] == True and current_user.user_id == consumer_data["created_by"])
        or (roles["broker"] == True and (current_user.user_id == consumer_data["created_by"] or current_user.user_id in realtor_ids) )
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

    roles = [
        role
        for role in ["admin", "broker", "realtor", "buyer", "seller", "tenant"]
        if row.get(role)
    ]

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
