"""
Centralized logging configuration for the application.
"""
import logging
import logging.handlers
from pythonjsonlogger.json import JsonFormatter
import coloredlogs

from app.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # File handler with JSON formatting
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    json_formatter = JsonFormatter(LOG_FORMAT+"%(exception)s", datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(LOG_LEVEL)
    
    # Console handler with standard formatting
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(LOG_LEVEL)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    



    # Define custom styles for log levels
    level_styles = {
    'debug': {'color': 'blue'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red', 'bold': True},
    'critical': {'color': 'white', 'background': 'red', 'bold': True},
    }

    # Define custom styles for fields
    field_styles = {
    'asctime': {'color': 'cyan'},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'black', 'bold': True},
    'name': {'color': 'blue'},
    'programname': {'color': 'yellow'},
    }

    # Install coloredlogs with custom styles
    coloredlogs.install(
    level='DEBUG',
    logger=logger,
    level_styles=level_styles,
    field_styles=field_styles,
    fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s: %(message)s'
    )    

    return logger
