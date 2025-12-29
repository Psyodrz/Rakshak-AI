"""
Custom Exceptions
-----------------
Application-specific exceptions with proper HTTP status mapping.
"""

from typing import Optional


class RakshakException(Exception):
    """Base exception for RAKSHAK-AI."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ZoneNotFoundError(RakshakException):
    """Raised when a track zone is not found."""
    
    def __init__(self, zone_id: str):
        super().__init__(
            message=f"Track zone not found: {zone_id}",
            status_code=404,
            details={"zone_id": zone_id}
        )


class AlertNotFoundError(RakshakException):
    """Raised when an alert is not found."""
    
    def __init__(self, alert_id: str):
        super().__init__(
            message=f"Alert not found: {alert_id}",
            status_code=404,
            details={"alert_id": alert_id}
        )


class ValidationError(RakshakException):
    """Raised for input validation failures."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=400,
            details={"field": field} if field else {}
        )


class ServiceUnavailableError(RakshakException):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(self, service_name: str, reason: str = "temporarily unavailable"):
        super().__init__(
            message=f"Service {service_name} is {reason}",
            status_code=503,
            details={"service": service_name}
        )


class SensorFailureError(RakshakException):
    """Raised when sensor data is unavailable or invalid."""
    
    def __init__(self, zone_id: str, sensor_id: Optional[str] = None):
        super().__init__(
            message=f"Sensor data unavailable for zone {zone_id}",
            status_code=503,
            details={"zone_id": zone_id, "sensor_id": sensor_id}
        )


class VisionAnalysisError(RakshakException):
    """Raised when vision analysis fails."""
    
    def __init__(self, zone_id: str, reason: str):
        super().__init__(
            message=f"Vision analysis failed for zone {zone_id}: {reason}",
            status_code=500,
            details={"zone_id": zone_id, "reason": reason}
        )
