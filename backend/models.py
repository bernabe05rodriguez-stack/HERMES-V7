from pydantic import BaseModel
from typing import Optional

class LicenseVerification(BaseModel):
    code: str
    hwid: str

class LicenseGenerator(BaseModel):
    duration_days: int
    prefix: Optional[str] = None

class UpdateCheck(BaseModel):
    current_version: str

class UpdateInfo(BaseModel):
    version: str
    download_url: str
    filename: str
