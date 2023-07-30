from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.param_functions import Form
from typing import Annotated, List, Union

print(dir(OAuth2PasswordRequestForm))
class OAuth2PasswordRequestFormWithAdmin(OAuth2PasswordRequestForm):
    def __init__(
        self,
        admin_username: Annotated[str, Form()],
        admin_password: Annotated[str, Form()],
    ):
        self.admin_username = admin_username
        self.admin_password = admin_password
OAuth2PasswordRequestForm()
OAuth2PasswordRequestFormWithAdmin('root', 'secure').ad