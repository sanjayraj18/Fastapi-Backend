from fastapi import APIRouter, HTTPException, status, Depends
from validation.models import UserResponse, UserBase
from sqlalchemy.orm import Session
from database.database import get_db
from routes.user_routes import signin as signin_service
from routes.user_routes import signup as signup_service

router = APIRouter()

@router.post("/signin", response_model= UserResponse, status_code=status.HTTP_201_CREATED)
def signin(data : UserBase, db :Session = Depends(get_db) ):
    return signin_service(data,db)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data : UserBase, db: Session = Depends(get_db)):
    return signup_service(data,db)