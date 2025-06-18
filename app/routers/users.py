from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from app.models import Users
from app.database import db_depends
from starlette import status
from app.utils import oath_depends, oathbearer_depends, create_token, hashing, bcrypt_context
from datetime import timedelta


router = APIRouter(
    prefix='/user',
    tags=['user']
)


class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=3)
    role: str



class Token(BaseModel):
    access_token: str
    token_type: str



@router.post('/token', status_code=status.HTTP_202_ACCEPTED, response_model=Token)
async def auth_user (form: oath_depends, db: db_depends):

    user = db.query(Users).filter(Users.email == form.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not bcrypt_context.verify(form.password, user.password): # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = create_token(user.email, user.id, timedelta(minutes=30)) # type: ignore
    return {'access_token':token,
            'token_type':'bearer'}


@router.get('/', status_code=status.HTTP_200_OK, include_in_schema=True)
async def get_all_users(db:db_depends):
    users = db.query(Users).all()
    return users


@router.get('/email', status_code=status.HTTP_200_OK)
async def get_user_by_email(email:str , db:db_depends):
    users = db.query(Users).filter(Users.email ==  email)
    return users.first()


@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_new_user(user_request:CreateUserRequest, db:db_depends):

    try:
        user_request.password = hashing(user_request.password)
        new_user = Users(**user_request.model_dump())
        db.add(new_user)
        db.commit()
        return {'details':[new_user.email, new_user.password]}
    except :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')


@router.put('/email', status_code=status.HTTP_200_OK)
async def update_user_by_email(update_request: CreateUserRequest,email: str, db: db_depends):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    user.first_name = update_request.first_name # type: ignore
    user.last_name = update_request.last_name   # type: ignore
    user.role = update_request.role             # type: ignore
    user.password = hashing(update_request.password) # type: ignore

    db.commit()
    db.refresh(user)
    return user



@router.delete('/email', status_code=status.HTTP_200_OK)
async def delete_user_by_email(email: str, db: db_depends):
    pass
