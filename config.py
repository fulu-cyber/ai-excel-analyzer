import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_ROWS_PREVIEW = int(os.getenv("MAX_ROWS_PREVIEW", "100"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "10000"))

    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
    API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))

    APP_TITLE = "AI Excel Analyzer"
    APP_ICON = "📊"
