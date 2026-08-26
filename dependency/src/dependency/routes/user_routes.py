from fastapi import APIRouter, HTTPException, status, Depends
from validation.models import UserBase, TokenResponse, RefreshRequest
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import RefreshToken
from services.user_service import signin as signin_service
from services.user_service import signup as signup_service
from services.token_service import validate_refresh_token_in_db, create_access_token

router = APIRouter()

@router.post("/auth/signin", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def signin(data: UserBase, db: Session = Depends(get_db)):
    return signin_service(data, db)


@router.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserBase, db: Session = Depends(get_db)):
    return signup_service(data, db)


@router.post("/auth/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    user_id = validate_refresh_token_in_db(request.refresh_token, db)
    access_token = create_access_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token
    )


@router.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout(request: RefreshRequest, db: Session = Depends(get_db)):
    """Revoke refresh token"""
    db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).delete()
    db.commit()
    return {"message": "Logged out successfully"}