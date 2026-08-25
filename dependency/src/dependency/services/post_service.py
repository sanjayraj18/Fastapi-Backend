from validation.models import PostBase, PostResponse
from sqlalchemy.orm import Session
from database.schemas import User, Post
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_post(data : PostBase, db : Session) -> PostResponse:
       try : 
              new_post = Post(
                     title = data.title,
                     content  = data.content,  
              )

              db.add(new_post)
              db.commit()
              db.refresh(new_post)

       except HTTPException:
            raise
       
       except Exception:
              db.rollback()
              raise HTTPException(status_code=500, detail="An unexpected error in creating posts")
               
