from validation.models import UserBase, UserResponse
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import User
from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def email_already_Exisits(email : str, db:Session) -> bool:
      return db.query(User).filter(User.email == email).first() is not None

def hash_password(password : str) -> str:
      return pwd_context.hash(password)


def signup(register_data : UserBase, db:Session) -> UserResponse:
      
      try:
            if email_already_Exisits(register_data.email, db):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exists",
                        )
            hashed_password = hash_password(register_data.password)

            new_user = User(
                   name = register_data.name,
                   email = register_data.email,
                   password = hashed_password,
                   Bio = register_data.Bio
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return new_user

      except HTTPException:
            raise
      
      except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
                  
                  
            
     