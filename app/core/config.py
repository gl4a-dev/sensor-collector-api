import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sensor Collector API"

    DB_USER: str
    DB_PASSWORD: str 
    DB_HOST: str
    DB_NAME: str

    GOOGLE_CLIENT_ID: str
    FIREBASE_CREDENTIALS_PATH: str

    REGION_POINTS: list[list[float]] = []

    model_config = SettingsConfigDict(
        env_file="./.env",
        extra="ignore"
    )

    @field_validator("REGION_POINTS", mode="before")
    @classmethod
    def parse_region_points(cls, v: str | list) -> list:
        """Converts the JSON string contained in the .env into a list of coordinates."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    def get_database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}?sslmode=require"
    
settings = Settings()