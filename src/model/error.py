
from pydantic import BaseModel
from typing import Annotated, Union
from datetime import datetime
import src.model.metadata as metadata
class SqlError(BaseModel):
    error_code: Union[int, str] = None
    sql_state: Union[int, str] = None
    message: Union[str, None] = None
    time: str = metadata.get_timestamp()
    def as_dict(self):
        return vars(self)
    def return_message(self):
        error = {
            "Error_code": self.error_code,
            "SQL_state": self.sql_state,
            "time": self.time,
            "message": self.message
        }
        return {'error': self.__class__.__name__, 'data': error}