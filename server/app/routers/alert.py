"""
Alert API Routes
----------------
Endpoints for alert management and tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional

from ..models.alert import (
    Alert,
    AlertStatus,
    SeverityLevel,
    AlertAcknowledgeRequest,
    AlertResolveRequest,
    AlertStatusResponse,
    AlertHistoryQuery,
    AlertHistoryResponse,
)
from ..services.alert_service import alert_service
from ..services.audit_service import audit_service, AuditEventType
from ..utils.logger import logger

router = APIRouter(prefix="/alert", tags=["Alert Management"])


@router.get(
    "/status",
    response_model=AlertStatusResponse,
    summary="Get current alert status",
    description="""
    Get a summary of current alert status including:
    - Total active alerts
    - Count by severity level
    - Most urgent alert
    - Recent alerts
    - Statistics
    """
)
async def get_alert_status() -> AlertStatusResponse:
    """Get current alert status summary."""
    return await alert_service.get_status()


@router.get(
    "/history",
    response_model=AlertHistoryResponse,
    summary="Get alert history",
    description="Query historical alerts with filtering options"
)
async def get_alert_history(
    zone_id: Optional[str] = Query(None, description="Filter by zone"),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> AlertHistoryResponse:
    """Get alert history with filters."""
    query = AlertHistoryQuery(
        zone_id=zone_id,
        severity=severity,
        status=status,
        limit=limit,
        offset=offset
    )
    return await alert_service.get_history(query)


@router.get(
    "/{alert_id}",
    response_model=Alert,
    summary="Get specific alert"
)
async def get_alert(alert_id: str) -> Alert:
    """Get a specific alert by ID."""
    alert = await alert_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
    return alert


@router.post(
    "/acknowledge",
    response_model=Alert,
    summary="Acknowledge an alert",
    description="""
    Acknowledge an alert to indicate it has been seen and is being handled.
    
    Acknowledgement:
    - Stops escalation timer
    - Records who acknowledged and when
    - Can optionally mark as false positive
    """
)
async def acknowledge_alert(request: AlertAcknowledgeRequest) -> Alert:
    """Acknowledge an alert."""
    logger.info(f"Acknowledging alert {request.alert_id}")
    
    alert = await alert_service.acknowledge_alert(request)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {request.alert_id}")
    
    # Log to audit trail
    audit_service.log_alert_event(
        event_type=AuditEventType.ALERT_ACKNOWLEDGED,
        zone_id=alert.zone_id,
        alert_id=alert.alert_id,
        details={
            "acknowledged_by": request.acknowledged_by,
            "notes": request.notes,
            "marked_false_positive": request.mark_as_false_positive
        },
        user_id=request.acknowledged_by
    )
    
    return alert


@router.post(
    "/resolve",
    response_model=Alert,
    summary="Resolve an alert",
    description="""
    Resolve an alert after investigation is complete.
    
    Resolution requires:
    - Minimum 10 character notes explaining resolution
    - Confirmation of whether actual tampering was found
    
    This data is critical for:
    - Audit compliance
    - System accuracy metrics
    - Model improvement
    """
)
async def resolve_alert(request: AlertResolveRequest) -> Alert:
    """Resolve an alert."""
    logger.info(f"Resolving alert {request.alert_id}")
    
    alert = await alert_service.resolve_alert(request)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {request.alert_id}")
    
    # Log to audit trail
    audit_service.log_alert_event(
        event_type=AuditEventType.ALERT_RESOLVED,
        zone_id=alert.zone_id,
        alert_id=alert.alert_id,
        details={
            "resolved_by": request.resolved_by,
            "resolution_notes": request.resolution_notes,
            "was_actual_tampering": request.was_actual_tampering
        },
        user_id=request.resolved_by
    )
    
    return alert


@router.get(
    "/severity-levels",
    summary="Get severity level descriptions"
)
async def get_severity_levels():
    """Get descriptions of severity levels."""
    from ..config import config
    
    return {
        "levels": {
            "LOW": {
                "description": "Monitor situation, investigate within 30 minutes",
                "color": "#22c55e",  # Green
                "risk_range": config.SEVERITY_THRESHOLDS[SeverityLevel.LOW]
            },
            "MEDIUM": {
                "description": "Investigate within 15 minutes",
                "color": "#f59e0b",  # Amber
                "risk_range": config.SEVERITY_THRESHOLDS[SeverityLevel.MEDIUM]
            },
            "HIGH": {
                "description": "Immediate investigation required",
                "color": "#f97316",  # Orange
                "risk_range": config.SEVERITY_THRESHOLDS[SeverityLevel.HIGH]
            },
            "CRITICAL": {
                "description": "Emergency response, consider stopping trains",
                "color": "#ef4444",  # Red
                "risk_range": config.SEVERITY_THRESHOLDS[SeverityLevel.CRITICAL]
            }
        }
    }
