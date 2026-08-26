from fastapi import APIRouter, status, Depends
from validation.models import PostBase, PostResponse
from sqlalchemy.orm import Session
from database.database import get_db, get_current_user
from database.schemas import User
from services.post_service import (
    create_post as create_post_service,
    get_posts as get_posts_service,
    update_post as update_post_service,
    delete_post as delete_post_service
)

router = APIRouter()

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(data: PostBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_post_service(data, db, current_user)


@router.get("/posts", response_model=list[PostResponse], status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_posts_service(db, current_user)


@router.put("/posts/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
def update_post(post_id: str, data: PostBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_post_service(post_id, data, db, current_user)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_post_service(post_id, db, current_user)