"""
Utilities Package
-----------------
Shared utilities for RAKSHAK-AI server.
"""

from .logger import logger
from .exceptions import (
    RakshakException,
    ZoneNotFoundError,
    AlertNotFoundError,
    ValidationError,
    ServiceUnavailableError,
)

__all__ = [
    "logger",
    "RakshakException",
    "ZoneNotFoundError", 
    "AlertNotFoundError",
    "ValidationError",
    "ServiceUnavailableError",
]
