"""
Structured Logger
-----------------
Logging configuration for RAKSHAK-AI.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "zone_id"):
            log_data["zone_id"] = record.zone_id
        if hasattr(record, "analysis_id"):
            log_data["analysis_id"] = record.analysis_id
        if hasattr(record, "alert_id"):
            log_data["alert_id"] = record.alert_id
        
        return json.dumps(log_data)


def setup_logger(name: str = "rakshak-ai") -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler with structured output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Use simple format for console (easier to read during development)
    simple_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(simple_formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger


# Default logger instance
logger = setup_logger()
