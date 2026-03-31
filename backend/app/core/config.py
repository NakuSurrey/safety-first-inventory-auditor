"""
Application configuration.
Reads all settings from the .env file using pydantic-settings.
Every other file imports 'settings' from here to get config values.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Each field below maps to an environment variable in .env.
    Pydantic reads the .env file, finds the matching variable name,
    and loads the value into this class — with type validation.
    """

    # Database
    database_url: str

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:8081"

    # YOLO Model
    model_confidence_threshold: float = 0.5
    model_path: str = "./models/yolov8n_safety.tflite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a single instance — every file imports THIS object
settings = Settings()
