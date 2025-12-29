"""
Pydantic Models for Sensor Data
--------------------------------
Models for vibration, tilt, and pressure sensor data and anomaly detection.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    """Types of sensors deployed on track."""
    VIBRATION = "vibration"
    TILT = "tilt"
    PRESSURE = "pressure"


class AnomalyType(str, Enum):
    """
    Types of sensor anomalies detected.
    Each type has different tampering implications.
    """
    ENVIRONMENTAL_NOISE = "environmental_noise"  # Weather, wildlife, etc.
    MECHANICAL_WEAR = "mechanical_wear"          # Normal degradation
    SUDDEN_CHANGE = "sudden_change"              # Abrupt = sabotage-like
    COORDINATED_ANOMALY = "coordinated_anomaly"  # Multiple sensors = likely tampering
    SENSOR_FAILURE = "sensor_failure"            # Sensor malfunction
    NORMAL = "normal"                            # No anomaly


class AnomalySeverity(str, Enum):
    """Severity classification for sensor anomalies."""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class SensorReading(BaseModel):
    """
    Single sensor reading with metadata.
    Represents one data point from a sensor.
    """
    sensor_id: str = Field(..., description="Unique sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    zone_id: str = Field(..., description="Track zone where sensor is located")
    
    # Raw reading
    value: float = Field(..., description="Raw sensor value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_operational: bool = Field(default=True, description="Sensor functioning")
    battery_level: Optional[float] = Field(default=None, ge=0, le=100)


class SensorAnomaly(BaseModel):
    """
    Detected anomaly from sensor analysis.
    Includes classification and severity.
    """
    anomaly_id: str = Field(..., description="Unique anomaly ID")
    sensor_id: str = Field(..., description="Source sensor")
    sensor_type: SensorType
    
    # Anomaly classification
    anomaly_type: AnomalyType = Field(..., description="Type of anomaly")
    severity: AnomalySeverity = Field(..., description="Severity level")
    
    # Detection details
    value_observed: float = Field(..., description="Observed value")
    value_expected: float = Field(..., description="Expected baseline value")
    deviation_percent: float = Field(..., description="Percentage deviation from normal")
    
    # Statistical analysis
    z_score: Optional[float] = Field(default=None, 
        description="Standard deviations from mean")
    isolation_score: Optional[float] = Field(default=None, ge=0, le=1,
        description="Isolation Forest anomaly score (0=normal, 1=anomalous)")
    
    # Temporal context
    duration_seconds: Optional[float] = Field(default=None,
        description="How long anomaly persisted")
    is_recurring: bool = Field(default=False,
        description="Has this pattern been seen before?")


class SensorAnalysisRequest(BaseModel):
    """Request payload for sensor analysis endpoint."""
    zone_id: str = Field(..., description="Track zone to analyze")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # For simulation
    use_simulated: bool = Field(default=True)
    simulate_scenario: Optional[str] = Field(default=None,
        description="Scenario: 'normal', 'environmental', 'mechanical', 'sabotage'")
    
    # Optional: provide actual sensor readings
    readings: Optional[List[SensorReading]] = Field(default=None,
        description="Actual sensor readings if not simulating")


class SensorAnalysisResponse(BaseModel):
    """
    Complete response from sensor analysis.
    Contains all anomaly detections and risk assessment.
    """
    analysis_id: str = Field(..., description="Unique analysis ID for audit")
    zone_id: str = Field(..., description="Analyzed zone")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    
    # Sensor readings analyzed
    total_sensors: int = Field(..., description="Number of sensors in zone")
    operational_sensors: int = Field(..., description="Functioning sensors")
    readings_analyzed: int = Field(..., description="Number of readings processed")
    
    # Anomaly detection results
    anomalies: List[SensorAnomaly] = Field(default_factory=list)
    total_anomalies: int = Field(..., description="Count of anomalies")
    
    # Cross-sensor correlation
    is_coordinated: bool = Field(default=False,
        description="Multiple sensors showing correlated anomalies")
    coordination_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Risk contribution
    sensor_risk_score: float = Field(..., ge=0, le=100,
        description="Risk contribution from sensor analysis (0-100)")
    
    # Explainability
    risk_reasons: List[str] = Field(default_factory=list,
        description="Human-readable reasons for risk score")
    
    # Differentiation evidence
    environmental_likelihood: float = Field(default=0, ge=0, le=1,
        description="Probability anomaly is environmental")
    mechanical_likelihood: float = Field(default=0, ge=0, le=1,
        description="Probability anomaly is mechanical wear")
    sabotage_likelihood: float = Field(default=0, ge=0, le=1,
        description="Probability anomaly is intentional")
    
    # Processing metadata
    processing_time_ms: float = Field(..., description="Analysis time")
    is_simulated: bool = Field(default=True)


class SensorStatus(BaseModel):
    """Status summary for sensors in a zone."""
    zone_id: str
    total_sensors: int
    operational: int
    degraded: int
    failed: int
    last_reading_time: datetime
