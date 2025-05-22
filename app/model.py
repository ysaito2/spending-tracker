from pydantic import BaseModel
from typing import Optional


class AuthResponse(BaseModel):
    token: str
    error: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    document_id: Optional[str] = None
    error: Optional[str] = None