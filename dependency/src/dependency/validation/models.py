import datetime
from typing import Optional

from pydantic import BaseModel , Field, EmailStr


class UserBase(BaseModel):
    name: str = Field(default = None , min_length=4, max_length=25)
    email: EmailStr = Field(default = None) 
    password: str = Field(default = None, min_length = 6, max_length = 100)
    Bio : Optional[str] = Field(default = None, min_length = 10, max_length = 100)

class UserResponse(UserBase):
    id : int
    created_at : datetime

    class Config:
        from_attributes = True