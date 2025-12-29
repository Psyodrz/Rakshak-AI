"""
Configuration and Thresholds for RAKSHAK-AI
--------------------------------------------
This file contains all configurable parameters for the system.
Thresholds are set conservatively for safety-critical operations.

DESIGN RATIONALE:
- Risk thresholds are intentionally low to minimize false negatives
- Cooldown periods prevent alert fatigue while maintaining safety
- All values should be reviewed by domain experts before production use
"""

from pydantic import BaseModel
from typing import Dict, List
from enum import Enum


class SeverityLevel(str, Enum):
    """
    Alert severity levels based on risk score ranges.
    
    LOW: 25-49 - Monitor situation, no immediate action required
    MEDIUM: 50-69 - Investigate within 15 minutes
    HIGH: 70-84 - Immediate investigation required
    CRITICAL: 85-100 - Emergency response, stop trains in zone
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TamperingClassification(str, Enum):
    """
    Final classification output for intent analysis.
    
    SAFE: Normal operations, no threat detected
    SUSPICIOUS: Anomalies detected, human review recommended
    CONFIRMED_TAMPERING: High confidence tampering, immediate action required
    """
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED_TAMPERING = "CONFIRMED_TAMPERING"


class Config:
    """
    Central configuration class for RAKSHAK-AI.
    All thresholds and parameters are defined here for easy tuning.
    """
    
    # ==========================================================================
    # RISK SCORE THRESHOLDS
    # ==========================================================================
    # Risk scores range from 0-100
    # Lower values = safer, Higher values = more dangerous
    
    RISK_THRESHOLD_SAFE = 25  # Below this = SAFE
    RISK_THRESHOLD_SUSPICIOUS = 60  # Below this but above SAFE = SUSPICIOUS
    # Above SUSPICIOUS threshold = CONFIRMED_TAMPERING
    
    # Severity level thresholds (for alerts)
    SEVERITY_THRESHOLDS = {
        SeverityLevel.LOW: (25, 49),
        SeverityLevel.MEDIUM: (50, 69),
        SeverityLevel.HIGH: (70, 84),
        SeverityLevel.CRITICAL: (85, 100),
    }
    
    # ==========================================================================
    # VISION DETECTION WEIGHTS
    # ==========================================================================
    # Weights for different vision-detected anomalies
    # Higher weight = more indicative of tampering
    
    VISION_WEIGHTS = {
        "missing_fish_plate": 35,      # Critical structural component
        "foreign_object": 25,          # Could be debris or deliberate
        "track_displacement": 40,      # Very serious, likely tampering
        "human_presence": 20,          # Suspicious in restricted zones
        "tool_detection": 30,          # Tools near tracks = high risk
        "vehicle_near_track": 15,      # Unauthorized vehicle access
    }
    
    # Minimum confidence for vision detections to be considered
    VISION_CONFIDENCE_THRESHOLD = 0.6
    
    # Low-light detection confidence penalty (multiplier)
    LOW_LIGHT_CONFIDENCE_PENALTY = 0.7
    
    # ==========================================================================
    # SENSOR ANOMALY WEIGHTS
    # ==========================================================================
    # Weights for different sensor anomaly types
    
    SENSOR_WEIGHTS = {
        "vibration_anomaly": 20,       # Could be train or tampering
        "tilt_anomaly": 30,            # Track misalignment indicator
        "pressure_anomaly": 25,        # Load distribution issue
        "sudden_change": 35,           # Abrupt changes = sabotage-like
        "coordinated_anomaly": 40,     # Multiple sensors = likely tampering
    }
    
    # Statistical thresholds for sensor anomaly detection
    SENSOR_THRESHOLDS = {
        "vibration": {
            "normal_range": (0, 50),    # Normal vibration amplitude
            "warning_range": (50, 80),  # Elevated but possibly normal
            "critical_range": (80, 100),# Definite anomaly
        },
        "tilt": {
            "normal_range": (0, 2),     # Degrees from baseline
            "warning_range": (2, 5),
            "critical_range": (5, 15),
        },
        "pressure": {
            "normal_range": (0.9, 1.1), # Ratio to expected load
            "warning_range": (0.7, 0.9),
            "critical_range": (0, 0.7),
        },
    }
    
    # ==========================================================================
    # TEMPORAL CONTEXT WEIGHTS
    # ==========================================================================
    # Time-based risk modifiers
    
    TIME_WEIGHTS = {
        "night_hours": 1.3,            # 22:00-05:00 = higher risk
        "early_morning": 1.2,          # 05:00-07:00 = elevated risk
        "peak_hours": 0.9,             # Lower tampering likelihood during busy times
        "maintenance_window": 0.5,     # Scheduled maintenance = lower risk
    }
    
    # ==========================================================================
    # ALERT MANAGEMENT
    # ==========================================================================
    
    # Cooldown period in seconds between alerts for same zone
    ALERT_COOLDOWN_SECONDS = 300  # 5 minutes
    
    # Maximum alerts per zone per hour (flooding prevention)
    MAX_ALERTS_PER_HOUR = 10
    
    # Escalation time in seconds (if not acknowledged)
    ESCALATION_TIMEOUT = {
        SeverityLevel.LOW: 1800,       # 30 minutes
        SeverityLevel.MEDIUM: 900,     # 15 minutes
        SeverityLevel.HIGH: 300,       # 5 minutes
        SeverityLevel.CRITICAL: 60,    # 1 minute
    }
    
    # ==========================================================================
    # TRACK ZONES (SIMULATED)
    # ==========================================================================
    # Simulated track zones for demo purposes
    
    TRACK_ZONES = [
        {"id": "ZONE-001", "name": "Mumbai Central - Dadar", "km_start": 0, "km_end": 10},
        {"id": "ZONE-002", "name": "Dadar - Kurla", "km_start": 10, "km_end": 18},
        {"id": "ZONE-003", "name": "Kurla - Thane", "km_start": 18, "km_end": 35},
        {"id": "ZONE-004", "name": "Thane - Kalyan", "km_start": 35, "km_end": 54},
        {"id": "ZONE-005", "name": "Kalyan Junction", "km_start": 54, "km_end": 56},
    ]
    
    # ==========================================================================
    # SIMULATION PARAMETERS
    # ==========================================================================
    
    # Probability of generating anomalous data in simulation
    SIMULATION_ANOMALY_PROBABILITY = 0.3
    
    # Simulation refresh rate in seconds
    SIMULATION_REFRESH_RATE = 5
    
    # ==========================================================================
    # AUDIT LOGGING
    # ==========================================================================
    
    # Maximum audit log entries to keep in memory
    MAX_AUDIT_LOG_ENTRIES = 10000
    
    # Audit log retention period in days
    AUDIT_RETENTION_DAYS = 365
    
    # ==========================================================================
    # API SETTINGS
    # ==========================================================================
    
    API_TITLE = "RAKSHAK-AI API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    AI System to Detect Intentional Railway Track Tampering.
    
    ⚠️ IMPORTANT: This system uses SIMULATED sensor and vision data.
    All AI/ML logic is real and production-grade.
    """
    
    # CORS settings for development
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]


# Singleton config instance
config = Config()
