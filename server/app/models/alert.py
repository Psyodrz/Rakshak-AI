"""
Pydantic Models for Alert Management
-------------------------------------
Models for alert generation, tracking, and management.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """
    Alert severity levels.
    Directly maps to response timeframes and escalation procedures.
    """
    LOW = "LOW"           # Monitor, investigate within 30 minutes
    MEDIUM = "MEDIUM"     # Investigate within 15 minutes
    HIGH = "HIGH"         # Immediate investigation required
    CRITICAL = "CRITICAL" # Emergency response, consider stopping trains


class AlertStatus(str, Enum):
    """Current status of an alert."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FALSE_POSITIVE = "false_positive"


class EscalationLevel(int, Enum):
    """Escalation levels for unacknowledged alerts."""
    INITIAL = 1
    SUPERVISOR = 2
    MANAGER = 3
    EMERGENCY = 4


class Alert(BaseModel):
    """
    Core alert model.
    Generated when risk score exceeds thresholds.
    """
    alert_id: str = Field(..., description="Unique alert identifier")
    zone_id: str = Field(..., description="Affected zone")
    
    # Classification reference
    classification_id: str = Field(..., description="Source classification")
    
    # Alert details
    severity: SeverityLevel = Field(..., description="Alert severity")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    
    # Risk information
    risk_score: float = Field(..., ge=0, le=100)
    classification: str = Field(..., description="SAFE/SUSPICIOUS/CONFIRMED_TAMPERING")
    
    # Summary for display
    title: str = Field(..., description="Short alert title")
    description: str = Field(..., description="Detailed description")
    reasons: List[str] = Field(default_factory=list,
        description="Reasons for alert")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Acknowledgement
    acknowledged: bool = Field(default=False)
    acknowledged_by: Optional[str] = Field(default=None)
    acknowledged_at: Optional[datetime] = Field(default=None)
    acknowledgement_notes: Optional[str] = Field(default=None)
    
    # Escalation
    escalation_level: EscalationLevel = Field(default=EscalationLevel.INITIAL)
    escalated_at: Optional[datetime] = Field(default=None)
    
    # Resolution
    resolved_at: Optional[datetime] = Field(default=None)
    resolution_notes: Optional[str] = Field(default=None)
    
    # Evidence links
    evidence_urls: List[str] = Field(default_factory=list,
        description="Links to images, sensor data, etc.")
    
    # Metadata
    is_simulated: bool = Field(default=True)


class AlertCreateRequest(BaseModel):
    """Internal request to create an alert (from classification engine)."""
    zone_id: str
    classification_id: str
    risk_score: float
    classification: str
    reasons: List[str]
    evidence_urls: List[str] = []


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert."""
    alert_id: str = Field(..., description="Alert to acknowledge")
    acknowledged_by: str = Field(..., description="User ID or name")
    notes: Optional[str] = Field(default=None, description="Optional notes")
    mark_as_false_positive: bool = Field(default=False)


class AlertResolveRequest(BaseModel):
    """Request to resolve an alert."""
    alert_id: str
    resolved_by: str
    resolution_notes: str = Field(..., min_length=10,
        description="Required explanation of resolution")
    was_actual_tampering: bool = Field(...,
        description="Confirm if tampering was real")


class AlertStatusResponse(BaseModel):
    """
    Current alert status summary.
    Used for dashboard overview.
    """
    total_active: int = Field(..., description="Currently active alerts")
    by_severity: Dict[str, int] = Field(..., 
        description="Count by severity level")
    
    # Most urgent alert
    most_urgent: Optional[Alert] = Field(default=None)
    
    # Recent alerts
    recent_alerts: List[Alert] = Field(default_factory=list)
    
    # Statistics
    alerts_last_hour: int = Field(default=0)
    alerts_last_24h: int = Field(default=0)
    
    # System status
    system_status: str = Field(default="operational")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AlertHistoryQuery(BaseModel):
    """Query parameters for alert history."""
    zone_id: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    status: Optional[AlertStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=50, le=500)
    offset: int = Field(default=0)


class AlertHistoryResponse(BaseModel):
    """Paginated alert history response."""
    alerts: List[Alert]
    total: int
    limit: int
    offset: int
    has_more: bool
