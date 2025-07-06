from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import os
from dotenv import load_dotenv

from app import database, models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    print("Login attempt:", form_data.username)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    print("Received password from frontend:", repr(form_data.password))

    if not user:
        print("User not found")
    else:
        print("User found:", user.email)
        print("Stored hash:", user.password_hash)
        print("Password match:", pwd_context.verify(form_data.password, user.password_hash))
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={
        "sub": str(user.user_id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "address":user.address,
        "neighborhood":user.neighborhood,
        "city":user.city,
        "county":user.county,
        "lic_num": user.lic_num,
        "role": user.role,
    })
    return {"access_token": access_token, "token_type": "bearer"}

