from validation.models import PostBase, PostResponse
from sqlalchemy.orm import Session
from database.schemas import User, Post
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_post(data : PostBase, db : Session , current_user : User) -> PostResponse:
       try : 
              new_post = Post(
                     title = data.title,
                     content  = data.content,  
                     user_id = current_user.id
              )

              db.add(new_post)
              db.commit()
              db.refresh(new_post)

       except HTTPException:
            raise
       
       except Exception:
              db.rollback()
              raise HTTPException(status_code=500, detail="An unexpected error in creating posts")
               
def get_posts(db :Session, current_user : User):
       try:
              userId = current_user.id
              posts = db.query(Post).filter(Post.user_id == userId)

              return posts

       except HTTPException:
              raise
              
       except Exception:
              db.rollback()
              raise HTTPException(status_code=500, detail="An unexpected error in fetching posts")

def update_post(post_id : str,data : PostBase, db :Session , current_user : User):
       try:
           post = db.query(Post).filter(Post.id == post_id)

           if not post:
             raise HTTPException(status_code=404, detail="Post not found")

           if post.user_id != current_user.id:
              raise HTTPException(status_code=403, detail="Not authorized to update this post")

           post.title = data.title
           post.content = data.content

           db.commit()
           db.refresh(post)

           return post

       except HTTPException:
              raise

       except Exception:
              db.rollback()
              raise HTTPException(status_code=500, detail = "An error occured in updating post")