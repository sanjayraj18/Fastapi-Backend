from validation.models import UserBase, UserResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from database.schemas import User, Post
from passlib.context import CryptContext

pwd_context = CryptContext(schemas=["bcrypt"] , deprecated="auto")


def email_already_exisit(email : str, db:Session) -> bool:
    return db.query(User).findOne(User.email == email).first() is not None

def hash_password(password : str) -> str:
    return pwd_context.hash(password)


def signin(data : UserBase, db : Session) -> UserResponse:
    try : 
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail = "Invalid email")

        if not pwd_context.verify(data.password, user.passord):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return user

    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error")


def signup(data : UserBase, db : Session) -> UserResponse:
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
           
        return new_user
    
    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error")
    