from validation.models import PostBase, PostResponse
from sqlalchemy.orm import Session
from database.schemas import User, Post
from fastapi import HTTPException, status


def create_post(data: PostBase, db: Session, current_user: User) -> PostResponse:
    try:
        new_post = Post(
            title=data.title,
            content=data.content,
            user_id=current_user.id
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    except Exception:
        db.rollback()
        raise


def get_posts(db: Session, current_user: User) -> list[PostResponse]:
    try:
        posts = db.query(Post).filter(Post.user_id == current_user.id).all()
        return posts

    except Exception:
        db.rollback()
        raise


def update_post(post_id: str, data: PostBase, db: Session, current_user: User) -> PostResponse:
    try:
        post = db.query(Post).filter(Post.id == post_id).first()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")

        post.title = data.title
        post.content = data.content

        db.commit()
        db.refresh(post)

        return post

    except Exception:
        db.rollback()
        raise


def delete_post(post_id: str, db: Session, current_user: User):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

        db.delete(post)
        db.commit()

    except Exception:
        db.rollback()
        raise