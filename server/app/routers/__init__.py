"""
Routers Package
---------------
FastAPI route definitions for RAKSHAK-AI API.
"""

from .vision import router as vision_router
from .sensor import router as sensor_router
from .intent import router as intent_router
from .alert import router as alert_router
from .system import router as system_router

__all__ = [
    "vision_router",
    "sensor_router",
    "intent_router",
    "alert_router",
    "system_router",
]
