from datetime import datetime

from pydantic import BaseModel


class ORMModel(BaseModel):
    class Config:
        orm_mode = True


class DocumentOut(ORMModel):
    id: int
    filename: str
    mime_type: str
    uri: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(ORMModel):
    id: int
    username: str
