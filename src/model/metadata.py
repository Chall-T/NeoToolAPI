from datetime import datetime
import time
from pydantic import BaseModel, ValidationError, Field
from typing import Annotated, List, Union
from fastapi import Body

def get_datetime():
    date = datetime.now()
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def get_timestamp():
    return str(int(time.time()))

def get_timezone():
    return str(datetime.now().astimezone(None).strftime("GMT%z"))

class AppVersion(BaseModel):
    id: Union[int, str]
    version: str
    cdata: Union[str, int] = None
    date: Union[datetime, str] = None
    
    def update_version(self, version:str, cdata:int):
        ...
class CreateNewStatItem(BaseModel):
    event: str | None = Field(
        default='Attack', description="Event group name"
    )
    count: int | None = Field(
        default=1, description="Amount of the logged stat"
    )