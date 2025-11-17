from pydantic_settings import BaseSettings, SettingsConfigDict
import cloudinary

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    postgres_db: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 1440
    expire_minutes: int = 60  

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    redis_url: str

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()

def init_cloudinary():
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
