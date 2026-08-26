from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from config import settings
from fastapi import Depends, HTTPException
from database.schemas import User
from services.token_service import verify_access_token

engine = create_engine(settings.DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(authorization : str = Header(...), db : Session = Depends(get_db)) -> User:
     
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token  = parts[1]

    user_id = verify_access_token(token)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
