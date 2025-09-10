from datetime import datetime, timedelta, timezone
from jose import jwt
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

    return {"access_token": access_token, "token_type": "bearer"}

