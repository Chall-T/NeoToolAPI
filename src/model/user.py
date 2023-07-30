
from pydantic import BaseModel, ValidationError
from typing import Annotated, List, Union
from fastapi import Depends, FastAPI, HTTPException, Security, status
from datetime import datetime
from passlib.context import CryptContext
from src.repository.database import get_user
from fastapi.param_functions import Form
import os, binascii
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)


SECRET_KEY = "f3063917d33abd5df9fca65d95d054dc1193c27159fa05f34b4883b0ba8d5c12"
ALGORITHM = "HS256"
USER_TABLE = 'users'

load_dotenv()

admin_user_name = os.environ.get('API_USER')
admin_password = os.environ.get('API_PASSWORD')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []

class User(BaseModel):
    iduser: Union[int, None] = None
    gge_id: Union[str, None] = None
    gge_name: Union[str, None] = None
    gge_world: Union[str, None] = None
    sub: Union[datetime, str] = None
    client: Union[int, None] = None
    telegram_id: Union[int, str] = None
    last_ip: Union[str, None] = None
    last_socket: Union[str, None] = None
    gge_connection: Union[str, None] = None
    lts: Union[str, int] = None
    api_key: Union[str, None] = None
    disabled: bool = False

    def verify_password(self, plain_password, api_key):
        return pwd_context.verify(plain_password, api_key)

    def get_password_hash(self, password):
        return pwd_context.hash(password)
    
    def as_dict(self):
        return vars(self)


class OAuth2PasswordRequestFormWithAdmin(OAuth2PasswordRequestForm):
    def __init__(
        self,
        admin_username: Annotated[str, Form()],
        admin_password: Annotated[str, Form()],
    ):
        self.admin_username = admin_username
        self.admin_password = admin_password


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)


def authenticate_user(db_table, username: str, password: str):
    user = get_user(db_table, username)
    if not user:
        return False
    print(password, user.api_key)
    if not user.verify_password(str(password), str(user.api_key)):
        return False
    return user
def authenticate_admin(db_table, username: str, password: str):
    if username not in [admin_user_name]:
        return False
    user = get_user(db_table, username)
    if not user:
        return False
    if not user.verify_password(password, user.api_key):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(USER_TABLE, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user