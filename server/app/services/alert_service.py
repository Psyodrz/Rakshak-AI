"""
Alert Management Service
-------------------------
Handles alert generation, tracking, and lifecycle management.

DESIGN RATIONALE:
- Alerts are generated from classification results
- Cooldown prevents alert flooding
- Escalation ensures timely response
- All alerts are auditable
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from collections import defaultdict

from ..models.alert import (
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
from ..models.intent import TamperingClassification
from ..config import config


class AlertService:
    """
    Alert management service.
    
    Responsibilities:
    - Generate alerts from classification results
    - Track alert lifecycle (active -> acknowledged -> resolved)
    - Prevent alert flooding via cooldowns
    - Handle escalation for unacknowledged alerts
    """
    
    def __init__(self):
        """Initialize alert service."""
        # In-memory alert storage (would be database in production)
        self._alerts: Dict[str, Alert] = {}
        self._zone_last_alert: Dict[str, datetime] = {}
        self._zone_alert_counts: Dict[str, List[datetime]] = defaultdict(list)
    
    def create_alert_from_classification(
        self,
        zone_id: str,
        classification_id: str,
        classification: TamperingClassification,
        risk_score: float,
        reasons: List[str]
    ) -> Optional[Alert]:
        """
        Create an alert from a classification result.
        
        Only creates alert if:
        - Classification is not SAFE
        - Not in cooldown period for this zone
        - Under max alerts per hour
        """
        # Don't alert for SAFE classifications
        if classification == TamperingClassification.SAFE:
            return None
        
        # Check cooldown
        if not self._check_cooldown(zone_id):
            return None
        
        # Check flooding
        if not self._check_flooding(zone_id):
            return None
        
        # Determine severity
        severity = self._determine_severity(risk_score)
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            zone_id=zone_id,
            classification_id=classification_id,
            severity=severity,
            status=AlertStatus.ACTIVE,
            risk_score=risk_score,
            classification=classification.value,
            title=self._generate_title(zone_id, classification, severity),
            description=self._generate_description(classification, risk_score),
            reasons=reasons[:5],  # Keep top 5 reasons
            is_simulated=True
        )
        
        # Store alert
        self._alerts[alert.alert_id] = alert
        self._zone_last_alert[zone_id] = datetime.utcnow()
        self._zone_alert_counts[zone_id].append(datetime.utcnow())
        
        return alert
    
    def _check_cooldown(self, zone_id: str) -> bool:
        """Check if zone is in cooldown period."""
        last_alert = self._zone_last_alert.get(zone_id)
        if last_alert is None:
            return True
        
        elapsed = (datetime.utcnow() - last_alert).total_seconds()
        return elapsed >= config.ALERT_COOLDOWN_SECONDS
    
    def _check_flooding(self, zone_id: str) -> bool:
        """Check if zone is under max alerts per hour."""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old entries
        self._zone_alert_counts[zone_id] = [
            t for t in self._zone_alert_counts[zone_id] 
            if t > hour_ago
        ]
        
        return len(self._zone_alert_counts[zone_id]) < config.MAX_ALERTS_PER_HOUR
    
    def _determine_severity(self, risk_score: float) -> SeverityLevel:
        """Determine severity level from risk score."""
        for severity, (min_score, max_score) in config.SEVERITY_THRESHOLDS.items():
            if min_score <= risk_score <= max_score:
                return severity
        
        if risk_score < 25:
            return SeverityLevel.LOW
        return SeverityLevel.CRITICAL
    
    def _generate_title(
        self, 
        zone_id: str, 
        classification: TamperingClassification,
        severity: SeverityLevel
    ) -> str:
        """Generate alert title."""
        zone_name = zone_id  # Would look up actual name in production
        
        if classification == TamperingClassification.CONFIRMED_TAMPERING:
            return f"🚨 TAMPERING DETECTED: {zone_name}"
        else:
            return f"⚠️ Suspicious Activity: {zone_name}"
    
    def _generate_description(
        self,
        classification: TamperingClassification,
        risk_score: float
    ) -> str:
        """Generate alert description."""
        if classification == TamperingClassification.CONFIRMED_TAMPERING:
            return (
                f"High confidence ({risk_score:.1f}%) evidence of intentional "
                "track tampering. Immediate investigation required."
            )
        else:
            return (
                f"Suspicious anomalies detected (risk score: {risk_score:.1f}%). "
                "Human investigation recommended."
            )
    
    async def acknowledge_alert(
        self, 
        request: AlertAcknowledgeRequest
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        alert = self._alerts.get(request.alert_id)
        if not alert:
            return None
        
        alert.acknowledged = True
        alert.acknowledged_by = request.acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledgement_notes = request.notes
        alert.updated_at = datetime.utcnow()
        
        if request.mark_as_false_positive:
            alert.status = AlertStatus.FALSE_POSITIVE
        else:
            alert.status = AlertStatus.ACKNOWLEDGED
        
        return alert
    
    async def resolve_alert(self, request: AlertResolveRequest) -> Optional[Alert]:
        """Resolve an alert."""
        alert = self._alerts.get(request.alert_id)
        if not alert:
            return None
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = request.resolution_notes
        alert.updated_at = datetime.utcnow()
        
        return alert
    
    async def get_status(self) -> AlertStatusResponse:
        """Get current alert status summary."""
        active_alerts = [
            a for a in self._alerts.values() 
            if a.status == AlertStatus.ACTIVE
        ]
        
        # Count by severity
        by_severity = {s.value: 0 for s in SeverityLevel}
        for alert in active_alerts:
            by_severity[alert.severity.value] += 1
        
        # Get most urgent
        most_urgent = None
        if active_alerts:
            # Sort by severity (CRITICAL first) then by time
            severity_order = {
                SeverityLevel.CRITICAL: 0,
                SeverityLevel.HIGH: 1,
                SeverityLevel.MEDIUM: 2,
                SeverityLevel.LOW: 3,
            }
            sorted_alerts = sorted(
                active_alerts,
                key=lambda a: (severity_order.get(a.severity, 99), a.created_at)
            )
            most_urgent = sorted_alerts[0]
        
        # Recent alerts (last 10)
        all_alerts = sorted(
            self._alerts.values(),
            key=lambda a: a.created_at,
            reverse=True
        )
        
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)
        
        return AlertStatusResponse(
            total_active=len(active_alerts),
            by_severity=by_severity,
            most_urgent=most_urgent,
            recent_alerts=all_alerts[:10],
            alerts_last_hour=sum(1 for a in self._alerts.values() if a.created_at > hour_ago),
            alerts_last_24h=sum(1 for a in self._alerts.values() if a.created_at > day_ago),
            system_status="operational"
        )
    
    async def get_history(self, query: AlertHistoryQuery) -> AlertHistoryResponse:
        """Get alert history with filtering."""
        alerts = list(self._alerts.values())
        
        # Apply filters
        if query.zone_id:
            alerts = [a for a in alerts if a.zone_id == query.zone_id]
        if query.severity:
            alerts = [a for a in alerts if a.severity == query.severity]
        if query.status:
            alerts = [a for a in alerts if a.status == query.status]
        if query.start_time:
            alerts = [a for a in alerts if a.created_at >= query.start_time]
        if query.end_time:
            alerts = [a for a in alerts if a.created_at <= query.end_time]
        
        # Sort by time descending
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        total = len(alerts)
        
        # Paginate
        alerts = alerts[query.offset:query.offset + query.limit]
        
        return AlertHistoryResponse(
            alerts=alerts,
            total=total,
            limit=query.limit,
            offset=query.offset,
            has_more=(query.offset + len(alerts)) < total
        )
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get a specific alert by ID."""
        return self._alerts.get(alert_id)
    
    async def check_escalations(self):
        """
        Check for alerts that need escalation.
        
        Called periodically to escalate unacknowledged alerts.
        """
        now = datetime.utcnow()
        
        for alert in self._alerts.values():
            if alert.status != AlertStatus.ACTIVE:
                continue
            if alert.acknowledged:
                continue
            
            # Check escalation timeout
            timeout = config.ESCALATION_TIMEOUT.get(
                alert.severity, 
                config.ESCALATION_TIMEOUT[SeverityLevel.LOW]
            )
            
            elapsed = (now - alert.created_at).total_seconds()
            
            if elapsed > timeout and alert.escalation_level < EscalationLevel.EMERGENCY:
                alert.escalation_level = EscalationLevel(alert.escalation_level.value + 1)
                alert.escalated_at = now
                alert.status = AlertStatus.ESCALATED


# Singleton instance
alert_service = AlertService()
