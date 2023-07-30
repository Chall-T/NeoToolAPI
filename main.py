from datetime import datetime, timedelta
from typing import Annotated, List, Union
from dotenv import load_dotenv
import os, binascii
from fastapi import Depends, FastAPI, HTTPException, Security, status, Request, Body
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.param_functions import Form
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from src.repository.database import get_user, get_user_by_id, create_new_api_key, create_new_stat_for_user, get_event_by_name, get_stats_of_user
from src.model.user import *
from src.model.metadata import CreateNewStatItem
import uvicorn


ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 1 day
USER_TABLE = 'users'

app = FastAPI(root_path="/api/v1", swagger_ui_parameters={"defaultModelsExpandDepth": -1})


@app.post("/api_key")
async def create_api_key_for_user(
    form_data: Annotated[OAuth2PasswordRequestFormWithAdmin, Depends()]
):
    user = authenticate_admin(USER_TABLE, form_data.admin_username, form_data.admin_password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    new_user = authenticate_user(USER_TABLE, form_data.username, form_data.password)
    if not new_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    api_key = create_new_api_key(new_user.id)

    return {"api_key": api_key}


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(USER_TABLE, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.gge_name, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])]
):
    return [{"item_id": "Foo", "owner": current_user.gge_name}]


@app.get("/stats/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return get_stats_of_user(current_user)

@app.post("/stats/create")
async def create_new_stat(body: Annotated[ CreateNewStatItem, ...], current_user: Annotated[User, Depends(get_current_user)]):
    event = get_event_by_name(str(body.event))
    create_new_stat_for_user(current_user, User_stat(iduser=int(current_user.iduser),event_id=event.id, event_name=event.name,count=int(body.count)))
    raise HTTPException(status_code=200, detail={'status':'success'})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, root_path='/api/v1')