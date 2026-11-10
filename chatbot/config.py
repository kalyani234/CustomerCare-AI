import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

APP_NAME = "CustomerCare AI"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"  # Default model if not specified in .env
)

APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


def validate_config():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

    print("Configuration loaded successfully!")
    print(f"Application: {APP_NAME}")
    print(f"Environment: {APP_ENV}")
    print(f"Model: {GROQ_MODEL}")