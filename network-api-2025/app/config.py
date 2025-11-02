from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Network API 2025"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "change_me"
    TOKEN_EXPIRE_MINUTES: int = 60
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100


    class Config:
        env_file = ".env"


settings = Settings()