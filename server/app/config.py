from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/dreamlink"

    # JWT
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 30

    # 文件存储
    media_root: str = "./storage"
    media_url: str = "/media/"

    # 跨域
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
