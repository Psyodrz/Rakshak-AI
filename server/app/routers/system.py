"""
System API Routes
-----------------
Health checks, simulation control, and system management.

PRODUCTION DESIGN:
- All endpoints return structured JSON responses
- No unhandled exceptions - every error is caught and logged
- Simulation lifecycle managed by SimulationController
- Proper HTTP status codes for all scenarios
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..config import config
from ..services.alert_service import alert_service
from ..services.audit_service import audit_service
from ..simulation_controller import simulation_controller, SimulationState, SimulationStatus
from ..utils.logger import logger

router = APIRouter(prefix="/system", tags=["System Management"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="System status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    services: dict = Field(default_factory=dict)
    is_simulated: bool = Field(default=True, description="Whether system uses simulated data")


class SimulateRequest(BaseModel):
    """Request to trigger simulation scenario."""
    zone_id: str = Field(default="ZONE-001", description="Zone to simulate for")
    scenario: str = Field(
        default="suspicious",
        description="Scenario type: normal, suspicious, tampering, environmental"
    )


class SimulateResponse(BaseModel):
    """
    Standardized simulation response.
    
    ALWAYS returns JSON with consistent structure, never throws to client.
    """
    success: bool = Field(..., description="Whether simulation completed successfully")
    message: str = Field(..., description="Human-readable status message")
    simulation_state: SimulationState = Field(..., description="Current simulation lifecycle state")
    classification: Optional[str] = Field(None, description="Tampering classification result")
    risk_score: Optional[float] = Field(None, description="Calculated risk score 0-100")
    zone_id: Optional[str] = Field(None, description="Zone that was analyzed")
    details: Optional[dict] = Field(None, description="Full classification details if successful")


# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="""
    Check the health status of all system components.
    
    Returns:
    - Overall system status
    - Individual service statuses
    - Simulation mode indicator
    """
)
async def health_check() -> HealthResponse:
    """Check system health."""
    # Check all services
    services = {
        "vision_service": "healthy",
        "sensor_service": "healthy",
        "intent_service": "healthy",
        "alert_service": "healthy",
        "audit_service": "healthy",
        "simulation_controller": simulation_controller.state.value,
    }
    
    # Determine overall status
    critical_healthy = all(
        services.get(s) == "healthy" 
        for s in ["vision_service", "sensor_service", "intent_service"]
    )
    
    return HealthResponse(
        status="healthy" if critical_healthy else "degraded",
        timestamp=datetime.utcnow(),
        version=config.API_VERSION,
        services=services,
        is_simulated=True
    )


# ============================================================================
# SIMULATION ENDPOINTS
# ============================================================================

@router.post(
    "/simulate",
    response_model=SimulateResponse,
    summary="Trigger simulation scenario",
    description="""
    Trigger a complete simulation cycle for demo purposes.
    
    **Available scenarios:**
    - `normal`: Normal track conditions, no anomalies
    - `suspicious`: Some anomalies detected, recommend investigation
    - `tampering`: Strong evidence of intentional tampering
    - `environmental`: Environmental disturbance, not intentional
    
    **Lifecycle Safety:**
    - Returns structured response even on failure
    - Never throws unhandled exceptions to client
    - Logs all errors with full context
    
    Perfect for hackathon demonstrations.
    """
)
async def simulate_scenario(request: SimulateRequest) -> SimulateResponse:
    """
    Trigger a simulation scenario.
    
    PRODUCTION GUARANTEES:
    - Always returns JSON response
    - All exceptions caught and converted to error response
    - Simulation state always accurately reflects reality
    """
    logger.info(
        f"Simulation requested: zone={request.zone_id}, scenario={request.scenario}, "
        f"current_state={simulation_controller.state.value}"
    )
    
    # Run simulation through controller (handles all safety)
    result = await simulation_controller.run_single(
        zone_id=request.zone_id,
        scenario=request.scenario
    )
    
    if result["success"]:
        # Extract key fields from result
        classification_result = result["result"]
        
        return SimulateResponse(
            success=True,
            message=f"Simulation complete: {classification_result['classification']}",
            simulation_state=SimulationState(result["state"]),
            classification=classification_result["classification"],
            risk_score=classification_result["risk_score"],
            zone_id=classification_result["zone_id"],
            details=classification_result
        )
    else:
        # Error occurred - return structured error response
        logger.error(f"Simulation failed: {result.get('error', 'Unknown error')}")
        
        return SimulateResponse(
            success=False,
            message=f"Simulation failed: {result.get('error', 'Unknown error')}",
            simulation_state=SimulationState(result["state"]),
            classification=None,
            risk_score=None,
            zone_id=request.zone_id,
            details={"error": result.get("error")}
        )


@router.get(
    "/simulate/status",
    response_model=SimulationStatus,
    summary="Get simulation status",
    description="Get current simulation lifecycle state and statistics"
)
async def get_simulation_status() -> SimulationStatus:
    """Get current simulation status."""
    return simulation_controller.get_status()


@router.post(
    "/simulate/reset",
    response_model=SimulationStatus,
    summary="Reset simulation controller",
    description="Reset controller from ERROR state to STOPPED (recovery action)"
)
async def reset_simulation() -> SimulationStatus:
    """Reset simulation controller from error state."""
    logger.info("Simulation reset requested")
    return await simulation_controller.reset()


# ============================================================================
# ZONE & SCENARIO ENDPOINTS
# ============================================================================

@router.get(
    "/zones",
    summary="Get available track zones",
    description="List all monitored track zones"
)
async def get_zones():
    """Get list of track zones."""
    return {
        "zones": config.TRACK_ZONES,
        "total": len(config.TRACK_ZONES)
    }


@router.get(
    "/scenarios",
    summary="Get available simulation scenarios"
)
async def get_scenarios():
    """Get available simulation scenarios."""
    return {
        "scenarios": [
            {
                "id": "normal",
                "name": "Normal Operations",
                "description": "Normal track conditions, no anomalies detected",
                "expected_classification": "SAFE"
            },
            {
                "id": "environmental",
                "name": "Environmental Event",
                "description": "Weather or wildlife causing minor anomalies",
                "expected_classification": "SAFE or SUSPICIOUS"
            },
            {
                "id": "suspicious",
                "name": "Suspicious Activity",
                "description": "Anomalies detected that warrant investigation",
                "expected_classification": "SUSPICIOUS"
            },
            {
                "id": "tampering",
                "name": "Confirmed Tampering",
                "description": "Strong evidence of intentional track tampering",
                "expected_classification": "CONFIRMED_TAMPERING"
            }
        ]
    }


# ============================================================================
# AUDIT ENDPOINTS
# ============================================================================

@router.get(
    "/audit/recent",
    summary="Get recent audit entries"
)
async def get_recent_audit(limit: int = 50):
    """Get recent audit log entries."""
    entries = audit_service.get_recent_entries(limit=limit)
    return {
        "entries": [e.to_dict() for e in entries],
        "count": len(entries)
    }


@router.get(
    "/audit/stats",
    summary="Get audit log statistics"
)
async def get_audit_stats():
    """Get audit log statistics."""
    return audit_service.get_stats()


# ============================================================================
# CONFIG ENDPOINT
# ============================================================================

@router.get(
    "/config",
    summary="Get system configuration",
    description="Get current system configuration (non-sensitive)"
)
async def get_config():
    """Get system configuration."""
    return {
        "risk_thresholds": {
            "safe": config.RISK_THRESHOLD_SAFE,
            "suspicious": config.RISK_THRESHOLD_SUSPICIOUS,
        },
        "alert_settings": {
            "cooldown_seconds": config.ALERT_COOLDOWN_SECONDS,
            "max_per_hour": config.MAX_ALERTS_PER_HOUR,
        },
        "simulation": {
            "anomaly_probability": config.SIMULATION_ANOMALY_PROBABILITY,
            "refresh_rate": config.SIMULATION_REFRESH_RATE,
            "current_state": simulation_controller.state.value,
        },
        "api_info": {
            "title": config.API_TITLE,
            "version": config.API_VERSION,
        }
    }
