"""
Audit Logging Service
----------------------
Government-grade audit trail for all system decisions.

DESIGN RATIONALE:
- Every decision must be traceable
- Logs include inputs, intermediate steps, and outputs
- Structured JSON format for analysis
- Retention policy compliant
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

from ..config import config


class AuditEventType(str, Enum):
    """Types of audit events."""
    VISION_ANALYSIS = "vision_analysis"
    SENSOR_ANALYSIS = "sensor_analysis"
    INTENT_CLASSIFICATION = "intent_classification"
    ALERT_CREATED = "alert_created"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    ALERT_RESOLVED = "alert_resolved"
    ALERT_ESCALATED = "alert_escalated"
    SYSTEM_EVENT = "system_event"
    API_REQUEST = "api_request"
    ERROR = "error"


@dataclass
class AuditEntry:
    """Single audit log entry."""
    entry_id: str
    timestamp: datetime
    event_type: AuditEventType
    zone_id: Optional[str]
    
    # Event details
    summary: str
    details: Dict[str, Any]
    
    # Input/output capture
    inputs: Optional[Dict[str, Any]]
    outputs: Optional[Dict[str, Any]]
    
    # Decision trail
    decision_factors: Optional[List[str]]
    
    # Metadata
    user_id: Optional[str]
    session_id: Optional[str]
    processing_time_ms: Optional[float]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["event_type"] = self.event_type.value
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class AuditService:
    """
    Audit logging service.
    
    Provides comprehensive audit trail for:
    - All analysis decisions
    - Alert lifecycle events
    - System events
    - API requests
    
    In production, this would write to:
    - Immutable log storage
    - SIEM systems
    - Compliance databases
    """
    
    def __init__(self):
        """Initialize audit service."""
        # In-memory storage for demo (would be persistent storage in production)
        self._entries: List[AuditEntry] = []
        self._session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    def log_vision_analysis(
        self,
        zone_id: str,
        analysis_id: str,
        inputs: dict,
        outputs: dict,
        detections_count: int,
        risk_score: float,
        processing_time_ms: float
    ) -> str:
        """Log a vision analysis event."""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.VISION_ANALYSIS,
            zone_id=zone_id,
            summary=f"Vision analysis {analysis_id}: {detections_count} detections, "
                   f"risk score {risk_score:.1f}",
            details={
                "analysis_id": analysis_id,
                "detections_count": detections_count,
                "risk_score": risk_score,
            },
            inputs=inputs,
            outputs=outputs,
            decision_factors=[
                f"Detected {detections_count} anomalies",
                f"Calculated risk score: {risk_score}",
            ],
            user_id=None,
            session_id=self._session_id,
            processing_time_ms=processing_time_ms
        )
        
        self._add_entry(entry)
        return entry.entry_id
    
    def log_sensor_analysis(
        self,
        zone_id: str,
        analysis_id: str,
        inputs: dict,
        outputs: dict,
        sensors_count: int,
        anomalies_count: int,
        risk_score: float,
        processing_time_ms: float
    ) -> str:
        """Log a sensor analysis event."""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.SENSOR_ANALYSIS,
            zone_id=zone_id,
            summary=f"Sensor analysis {analysis_id}: {sensors_count} sensors, "
                   f"{anomalies_count} anomalies, risk score {risk_score:.1f}",
            details={
                "analysis_id": analysis_id,
                "sensors_count": sensors_count,
                "anomalies_count": anomalies_count,
                "risk_score": risk_score,
            },
            inputs=inputs,
            outputs=outputs,
            decision_factors=[
                f"Analyzed {sensors_count} sensors",
                f"Detected {anomalies_count} anomalies",
                f"Calculated risk score: {risk_score}",
            ],
            user_id=None,
            session_id=self._session_id,
            processing_time_ms=processing_time_ms
        )
        
        self._add_entry(entry)
        return entry.entry_id
    
    def log_intent_classification(
        self,
        zone_id: str,
        classification_id: str,
        classification: str,
        risk_score: float,
        confidence: float,
        risk_factors: List[str],
        recommended_actions: List[str],
        processing_time_ms: float
    ) -> str:
        """Log an intent classification event."""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.INTENT_CLASSIFICATION,
            zone_id=zone_id,
            summary=f"Classification {classification_id}: {classification} "
                   f"(score: {risk_score:.1f}, confidence: {confidence:.2f})",
            details={
                "classification_id": classification_id,
                "classification": classification,
                "risk_score": risk_score,
                "confidence": confidence,
                "recommended_actions": recommended_actions,
            },
            inputs=None,
            outputs=None,
            decision_factors=risk_factors,
            user_id=None,
            session_id=self._session_id,
            processing_time_ms=processing_time_ms
        )
        
        self._add_entry(entry)
        return entry.entry_id
    
    def log_alert_event(
        self,
        event_type: AuditEventType,
        zone_id: str,
        alert_id: str,
        details: dict,
        user_id: Optional[str] = None
    ) -> str:
        """Log an alert lifecycle event."""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=event_type,
            zone_id=zone_id,
            summary=f"Alert {alert_id}: {event_type.value}",
            details=details,
            inputs=None,
            outputs=None,
            decision_factors=None,
            user_id=user_id,
            session_id=self._session_id,
            processing_time_ms=None
        )
        
        self._add_entry(entry)
        return entry.entry_id
    
    def log_error(
        self,
        error_message: str,
        error_type: str,
        zone_id: Optional[str] = None,
        details: Optional[dict] = None
    ) -> str:
        """Log an error event."""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.ERROR,
            zone_id=zone_id,
            summary=f"Error: {error_message}",
            details={
                "error_type": error_type,
                "error_message": error_message,
                **(details or {})
            },
            inputs=None,
            outputs=None,
            decision_factors=None,
            user_id=None,
            session_id=self._session_id,
            processing_time_ms=None
        )
        
        self._add_entry(entry)
        return entry.entry_id
    
    def _add_entry(self, entry: AuditEntry):
        """Add entry to log, enforcing max size."""
        self._entries.append(entry)
        
        # Enforce max entries
        if len(self._entries) > config.MAX_AUDIT_LOG_ENTRIES:
            # Remove oldest entries
            self._entries = self._entries[-config.MAX_AUDIT_LOG_ENTRIES:]
    
    def get_recent_entries(
        self, 
        limit: int = 100,
        event_type: Optional[AuditEventType] = None,
        zone_id: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get recent audit entries with optional filtering."""
        entries = self._entries
        
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        if zone_id:
            entries = [e for e in entries if e.zone_id == zone_id]
        
        # Return most recent first
        return list(reversed(entries[-limit:]))
    
    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get a specific audit entry."""
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None
    
    def export_to_json(self, limit: int = 1000) -> str:
        """Export audit log to JSON for compliance."""
        entries = self._entries[-limit:]
        return json.dumps(
            [e.to_dict() for e in entries],
            default=str,
            indent=2
        )
    
    def get_stats(self) -> dict:
        """Get audit log statistics."""
        return {
            "total_entries": len(self._entries),
            "session_id": self._session_id,
            "oldest_entry": self._entries[0].timestamp.isoformat() if self._entries else None,
            "newest_entry": self._entries[-1].timestamp.isoformat() if self._entries else None,
            "event_type_counts": self._count_by_type()
        }
    
    def _count_by_type(self) -> dict:
        """Count entries by event type."""
        counts = {}
        for entry in self._entries:
            key = entry.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts


# Singleton instance
audit_service = AuditService()
