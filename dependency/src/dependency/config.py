from pathlib import Path

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL:str

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"

settings = Settings()
