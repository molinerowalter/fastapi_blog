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

    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5 MB //buena practica para limitar el tamaño de los archivos que se pueden subir al servidor, evitando posibles problemas de rendimiento o seguridad.

    posts_per_page: int = 10  # Number of posts to display per page in pagination

    reset_token_expire_minutes: int = 60  # Expiration time for password reset tokens in minutes

    mail_server: str = "localhost"
    mail_port: int = 587 #Puerto standard para SMTP (Simple Mail Transfer Protocol) que se utiliza para enviar correos electrónicos. El puerto 587 es el puerto recomendado para enviar correos electrónicos de manera segura utilizando STARTTLS.
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8000" 

settings = Settings()