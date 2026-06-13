from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ENCRYPTION_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_TIME_MINUTES: int

    class Config:
        env_file = ".env"


settings = Settings()
