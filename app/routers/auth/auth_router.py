from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import re
import os
from dotenv import load_dotenv

from app import database
from ...models.user_model import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

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

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire_minutes = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    email = form_data.username
    password = form_data.password
    print("Login attempt:", email)
    if not email_pattern.match(email):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # if ( not re.search(r"\d", password) ) or ( not re.search(r"[A-Z]",password) ) or (len(password) < 8):
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = db.query(User).filter(User.email == form_data.username).first()
    print("Received password from frontend:", repr(form_data.password))

    if not user:
        print("User not found")
    else:
        print("User found:", user.email)
        print("Stored hash:", user.password_hash)
        print("Password match:", pwd_context.verify(form_data.password, user.password_hash))
        
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    role_dict = user.roles.__dict__

    roles = [
        key for key, value in role_dict.items()
        if key not in ['id', 'user_id', '_sa_instance_state'] and isinstance(value, bool) and value
    ]

    access_token = create_access_token(data={
        "sub": str(user.user_id),
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "created_at": user.created_at.date().isoformat(),
        "roles": roles
    })
    refresh_token = create_refresh_token({"sub": str(user.user_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # You could also fetch user info again if needed
    new_access_token = create_access_token({"sub": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}
