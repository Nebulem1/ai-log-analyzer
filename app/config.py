from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    LOCAL_DATABASE_URL: str
    REDIS_URL: str
    GOOGLE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()