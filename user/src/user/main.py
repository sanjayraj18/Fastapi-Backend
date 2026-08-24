from datetime import datetime
from email.policy import default
from typing import Dict, Optional
from passlib.context import CryptContext

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    name : str = Field(min_length=2, max_length=100, example="John Doe")
    email : EmailStr = Field(default=None, example="sanjay@gmail.com")
    Bio : Optional[str] = Field(default=None, min_length=10, max_length=500, example="This is a sample bio for the user.")

class RegisterUser(UserBase):
    password : str = Field(default=None, min_length=8, max_length=100, example="password123")

class UserResponse(UserBase):
    id : int
    created_at : datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    password: str  
    created_at: datetime = Field(default_factory=datetime.now)

user_db : Dict[int,User] = {}
next_id : int = 1

# helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#routes
@app.post("/user/register", response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register_user(register_data : RegisterUser):
    global next_id
    try :
        hashed_password = hash_password(register_data.password)
        new_user = User(
            id = next_id,
            name = register_data.name,
            email = register_data.email,
            Bio = register_data.Bio,
            password = hashed_password,
            created_at = datetime.now()
        )

        user_db[next_id] = new_user
        next_id +=1

        return new_user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during registration")


@app.get("/users" , response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def all_users():
    try:
        return list(user_db.values())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching users")