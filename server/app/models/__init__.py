"""
Models Package
--------------
All Pydantic models for RAKSHAK-AI.
"""

from .vision import (
    DetectionClass,
    ImageSource,
    ImageCondition,
    BoundingBox,
    Detection,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)

from .sensor import (
    SensorType,
    AnomalyType,
    AnomalySeverity,
    SensorReading,
    SensorAnomaly,
    SensorAnalysisRequest,
    SensorAnalysisResponse,
    SensorStatus,
)

from .intent import (
    TamperingClassification,
    RiskFactor,
    TemporalContext,
    IntentClassifyRequest,
    IntentClassifyResponse,
    ClassificationHistory,
)

from .alert import (
    SeverityLevel,
    AlertStatus,
    EscalationLevel,
    Alert,
    AlertCreateRequest,
    AlertAcknowledgeRequest,
    AlertResolveRequest,
    AlertStatusResponse,
    AlertHistoryQuery,
    AlertHistoryResponse,
)

__all__ = [
    # Vision
    "DetectionClass",
    "ImageSource",
    "ImageCondition",
    "BoundingBox",
    "Detection",
    "VisionAnalysisRequest",
    "VisionAnalysisResponse",
    # Sensor
    "SensorType",
    "AnomalyType",
    "AnomalySeverity",
    "SensorReading",
    "SensorAnomaly",
    "SensorAnalysisRequest",
    "SensorAnalysisResponse",
    "SensorStatus",
    # Intent
    "TamperingClassification",
    "RiskFactor",
    "TemporalContext",
    "IntentClassifyRequest",
    "IntentClassifyResponse",
    "ClassificationHistory",
    # Alert
    "SeverityLevel",
    "AlertStatus",
    "EscalationLevel",
    "Alert",
    "AlertCreateRequest",
    "AlertAcknowledgeRequest",
    "AlertResolveRequest",
    "AlertStatusResponse",
    "AlertHistoryQuery",
    "AlertHistoryResponse",
]
