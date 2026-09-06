from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    bot_token: str
    redis_url: str = "redis://localhost:6379/0"
    deepseek_api_key: str
    admin_ids: List[int] = []

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
