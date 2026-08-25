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