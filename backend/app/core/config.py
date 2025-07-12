import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = os.getenv("PORT", 8000)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

class Settings:
    APP_NAME: str = "JobSeeker"
    APP_VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

settings = Settings()