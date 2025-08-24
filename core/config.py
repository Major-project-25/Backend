import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "KnowYourCampus"
    DATABASE_URL: str = "postgresql+psycopg2://kyc:knowyourcampus@192.168.137.65:5432/knowyourcampus"
    SECRET_KEY: str = "supersecret"  # Replace with env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
