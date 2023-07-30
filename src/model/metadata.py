from datetime import datetime
import time
from pydantic import BaseModel, ValidationError
from typing import Annotated, List, Union

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
