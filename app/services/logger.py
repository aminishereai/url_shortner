"""
Logger module for simplified logger access.
Use setup_logger() from logging_config for creating loggers.
"""
from app.logging_config import setup_logger

# Create logger for this module
logger = setup_logger(__name__)