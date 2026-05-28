"""
Application configuration and environment variables.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "app" / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"
LOG_FORMAT = "%(levelname)s %(asctime)s %(name)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Application
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
