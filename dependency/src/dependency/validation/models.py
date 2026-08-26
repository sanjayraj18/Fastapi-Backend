from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel , Field, EmailStr


class UserBase(BaseModel):
    name: str = Field(default = None , min_length=4, max_length=25)
    email: EmailStr = Field(default = None) 
    password: str = Field(default = None, min_length = 6, max_length = 100)
    Bio : Optional[str] = Field(default = None, min_length = 10, max_length = 100)

class UserResponse(BaseModel):
    id : UUID
    name : str
    email : EmailStr
    Bio : Optional[str] = None
    created_at : datetime

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title : str = Field(default=None, min_length=5, max_length=40)
    content : str = Field(default=None)
    created_at : datetime


class PostResponse(PostBase):
    id : int

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token : str
    refresh_token : str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id : UUID
    exp : int 

class RefreshRequest(BaseModel):
    refresh_token: str
    