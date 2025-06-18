from passlib.context import CryptContext  # hashing password library
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException
import jwt
from datetime import timedelta, datetime, timezone
from starlette import status



# Hashing password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

# Encoding Token dependency
oath_depends = Annotated[OAuth2PasswordRequestForm, Depends()]






#get secrent access key from CMD: openssl rand -hex 32
SECRET_KEY = '1ace655f024f3542e5182ec135a8b092d95c2f0e962ad863b5cc3288612e7b2b'
ALGORITHM = 'HS256'

# Create Token function
def create_token(email: str, id: str, expires_delta: timedelta):
    """
    This function generates token

    Args:
        email (str): email address
        expires_delta (timedelta): experation time

    Returns:
        token (dict): token and token type
    """
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        'sub': email,
        'id': id,
        'exp': expire
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token






# Decoding Token dependency
oathbearer_depends = OAuth2PasswordBearer(tokenUrl='user/token') 
# Retrieve Token information function
def decode_token(token: Annotated[str, Depends(oathbearer_depends)]):
    """
    This fucntion retreives the infromation from token

    Args:
        token (Annotated[str, Depends): generated token

    Raises:
        HTTPException: Passed HTTP_200_OK
        HTTPException: Failed HTTP_401_UNAUTHORIZED

    Returns:
        (dict): username (email)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get('sub')
        user_id : str = payload.get('id')
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not authorize user')
        return {'username': username, 'id':user_id}
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not authorize user')

# Token information dependency 
users_depends = Annotated[dict, Depends(decode_token)]






# Hashing password function
def hashing(password):
    """
    This function hashes the password

    Args:
        password (str): the inputed password

    Returns:
        hashed_password (str): hashed password in hex 32 
    """
    hashing = CryptContext(schemes=['bcrypt'], deprecated='auto')
    return hashing.hash(password)
