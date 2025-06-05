# schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthData(BaseModel):
    e_mail: str
    password: str

class UserCreate(BaseModel):
    e_mail: str
    password: str
