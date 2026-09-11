from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sensor Collector API"

    DB_USER: str
    DB_PASSWORD: str 
    DB_HOST: str
    DB_NAME: str

    GOOGLE_CLIENT_ID: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        extra="ignore"
    )

    def get_database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}?sslmode=require"
    
settings = Settings()