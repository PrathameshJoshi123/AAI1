"""Structured logging setup for the application."""
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure root logger with unified formatted stream handler."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

logger = logging.getLogger("ps21.backend")

