from pydantic import BaseModel, EmailStr
from typing import Literal

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserRegisterResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool

    class Config():
        from_attributes = True