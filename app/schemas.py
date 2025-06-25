from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr   # validate email format automatically
    password: str
