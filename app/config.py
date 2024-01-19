from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./shorten-url.db"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    print(f"Starting the settings in {settings.env_name} environment")
    return settings
