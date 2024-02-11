# config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"  
    PORT: int = 8000

settings = Settings()