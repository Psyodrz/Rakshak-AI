"""
Sensor API Routes
-----------------
Endpoints for sensor-based anomaly detection.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..models.sensor import (
    SensorAnalysisRequest,
    SensorAnalysisResponse,
    SensorType,
    SensorStatus,
)
from ..services.sensor_service import sensor_service
from ..services.audit_service import audit_service
from ..utils.logger import logger

router = APIRouter(prefix="/sensor", tags=["Sensor Analysis"])


@router.post(
    "/analyze",
    response_model=SensorAnalysisResponse,
    summary="Analyze sensor data for anomalies",
    description="""
    Analyze readings from vibration, tilt, and pressure sensors.
    
    **Detection methods:**
    - Statistical threshold analysis
    - Isolation Forest-style scoring
    - Cross-sensor correlation
    
    **Differentiates between:**
    - Environmental noise (weather, wildlife)
    - Mechanical wear patterns
    - Sudden sabotage-like events
    - Coordinated multi-sensor anomalies
    
    ⚠️ **Note:** This endpoint uses SIMULATED sensor data for demo purposes.
    """
)
async def analyze_sensors(request: SensorAnalysisRequest) -> SensorAnalysisResponse:
    """Analyze sensor readings for anomalies."""
    logger.info(f"Sensor analysis requested for zone {request.zone_id}")
    
    try:
        response = await sensor_service.analyze(request)
        
        # Log to audit trail
        audit_service.log_sensor_analysis(
            zone_id=request.zone_id,
            analysis_id=response.analysis_id,
            inputs={
                "zone_id": request.zone_id,
                "timestamp": request.timestamp.isoformat(),
            },
            outputs={
                "anomalies_count": response.total_anomalies,
                "risk_score": response.sensor_risk_score,
                "is_coordinated": response.is_coordinated,
            },
            sensors_count=response.total_sensors,
            anomalies_count=response.total_anomalies,
            risk_score=response.sensor_risk_score,
            processing_time_ms=response.processing_time_ms
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Sensor analysis failed: {str(e)}")
        audit_service.log_error(
            error_message=str(e),
            error_type="sensor_analysis_error",
            zone_id=request.zone_id
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/types",
    summary="Get available sensor types",
    description="List all sensor types deployed on tracks"
)
async def get_sensor_types():
    """Get available sensor types."""
    return {
        "types": [s.value for s in SensorType],
        "descriptions": {
            "vibration": "Track vibration sensors - detect unusual movement patterns",
            "tilt": "Track tilt sensors - detect alignment changes",
            "pressure": "Rail pressure sensors - detect load distribution anomalies"
        }
    }


@router.get(
    "/status/{zone_id}",
    response_model=SensorStatus,
    summary="Get sensor status for a zone"
)
async def get_zone_sensor_status(zone_id: str) -> SensorStatus:
    """Get sensor status summary for a zone."""
    return await sensor_service.get_zone_status(zone_id)
