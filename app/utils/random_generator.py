import random
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from .file_helper import load_sql

def generate_unique_mls_num(db: Session, retries: int = 3) -> int:
    for _ in range(retries):
        mls_num = random.randint(100000, 999999)
        sql = load_sql("property/get_property_by_mls.sql")
        exists = db.execute(text(sql), { "mls": mls_num}).mappings().first()
        if not exists:
            return mls_num
        
    raise HTTPException(status_code=400, detail="Could not generate a unique MLS number. Please try again.")

def generate_unique_license_num(db: Session, retries: int = 3) -> int:
    for _ in range(retries):
        mls_num = random.randint(10**13,10**14-1)
        sql = load_sql("property/get_property_by_mls.sql")
        exists = db.execute(text(sql), { "mls": mls_num}).mappings().first()
        if not exists:
            return mls_num
        
    raise HTTPException(status_code=400, detail="Could not generate a unique License number. Please try again.")
