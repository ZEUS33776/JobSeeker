import os
from dotenv import load_dotenv

load_dotenv()

# API keys with fallback values for development
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PORT = os.getenv("PORT", 8000)
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# Validation for required API keys
def validate_api_keys():
    """Validate that required API keys are set"""
    missing_keys = []
    
    if not GEMINI_API_KEY:
        missing_keys.append("GEMINI_API_KEY")
    if not SERPER_API_KEY:
        missing_keys.append("SERPER_API_KEY")
    
    return missing_keys

class Settings:
    APP_NAME: str = "JobSeeker"
    APP_VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

settings = Settings()