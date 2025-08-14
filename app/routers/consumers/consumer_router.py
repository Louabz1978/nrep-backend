from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional

from app import database
from app.models.consumer_model import Consumer
from app.models.role_model import Role
from app.dependencies import get_current_user
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

    consumer_out = ConsumerOut(
        consumer_id=row["consumer_id"],
        name=row["name"],
        father_name=row["father_name"],
        surname=row["surname"],
        mother_name_surname=row["mother_name_surname"],
        place_birth=row["place_birth"],
        date_birth=row["date_birth"],
        registry=row["registry"],
        national_number=row["national_number"],
        email=row["email"],
        phone_number=row["phone_number"],
        created_at=row["created_at"],
        created_by=row["created_by"],
        roles=roles  # Pass list directly
    )

    return {"message": "Consumer updated successfully", "consumer": consumer_out}
