from validation.models import UserBase, UserResponse, TokenResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from database.schemas import User, Post
from passlib.context import CryptContext
from services.token_service import create_access_token , create_refresh_token, save_refresh_token_to_db

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto")


#Helpers
def email_already_exisit(email : str, db:Session) -> bool:
    return db.query(User).filter(User.email == email).first() is not None

def hash_password(password : str) -> str:
    return pwd_context.hash(password)


def signin(data : UserBase, db : Session) -> TokenResponse:
    try : 
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail = "Invalid email")

        if not pwd_context.verify(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        save_refresh_token_to_db(user.id, refresh_token, db)

        return TokenResponse(
            access_token = access_token,
            refresh_token = refresh_token
        )

    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error")


def signup(data : UserBase, db : Session) -> TokenResponse:
    try :     
        if email_already_exisit(data.email, db):
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists",
                )
        hashed_password = hash_password(data.password)
           
        new_user = User(
                    name = data.name,
                    email = data.email,
                    password = hashed_password,
                    Bio = data.Bio
                )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)
        save_refresh_token_to_db(new_user.id, refresh_token, db)
                   
           
        return TokenResponse(
             access_token=access_token,
             refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error")

