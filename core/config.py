import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "KnowYourCampus"
    DATABASE_URL: str = "postgresql+psycopg2://kyc:knowyourcampus@172.17.4.253:5432/knowyourcampus" #WIFI
    #DATABASE_URL: str = "postgresql+psycopg2://kyc:knowyourcampus@10.100.211.210:5432/knowyourcampus" #HOTSPOT
    SECRET_KEY: str = "supersecret"  # Replace with env var
    ALGORITHM: str = "HS256"
    ENCRYPTION_KEY: str = "q31_DkkblEdJ2IzecTwU6rUbg85w6pO-id1i_P-8fHU=" #move it to env its not adviced to hardcode the encryption key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
