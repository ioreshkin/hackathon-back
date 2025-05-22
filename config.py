from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TOKEN: str
    API_HOST:  str
    
    class Config:
        env_file = ".env"

settings = Settings()