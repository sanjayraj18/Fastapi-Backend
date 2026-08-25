
from fastapi import APIRouter, status, Depends
from validation.models import UserBase, UserResponse
from services.post_service import signup as signup_service
from sqlalchemy.orm import Session
from database.database import get_db

router = APIRouter()

@router.post("/user/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(register_data: UserBase, db : Session = Depends(get_db)):
    return signup_service(register_data, db)