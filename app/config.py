from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_host: str = "redis"
    redis_port: int = 6379

    mail_username: str = "test@test.com"
    mail_password: str = "123456"

    class Config:
        env_file = ".env"


settings = Settings()