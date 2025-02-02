from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/codepilot/v1"
    GEMINI_API_KEY: str
    PROJECT_NAME: str = "VS CodePilot extension"

    class Config:
        env_file = ".env"


settings = Settings()
