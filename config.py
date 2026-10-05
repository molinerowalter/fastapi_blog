from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encodig="utf-8"
    )

    secret_key: SecretStr
    algoritm:str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()