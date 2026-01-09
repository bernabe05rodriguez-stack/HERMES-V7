from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    username: str
    password: str
    hwid: str

class UserCreate(BaseModel):
    username: str
    password: str
    expiration_date: Optional[str] = None

class UpdateCheck(BaseModel):
    current_version: str

class UpdateInfo(BaseModel):
    version: str
    download_url: str
    filename: str
