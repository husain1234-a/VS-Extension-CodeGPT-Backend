from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    GEMINI_API_KEY: str
    PROJECT_NAME: str = "VS Code Debug Bot"

    class Config:
        env_file = ".env"


settings = Settings()
