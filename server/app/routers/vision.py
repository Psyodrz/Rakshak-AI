"""
Vision API Routes
-----------------
Endpoints for image-based tampering detection.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..models.vision import (
    VisionAnalysisRequest,
    VisionAnalysisResponse,
    ImageSource,
)
from ..services.vision_service import vision_service
from ..services.audit_service import audit_service, AuditEventType
from ..utils.logger import logger

router = APIRouter(prefix="/vision", tags=["Vision Detection"])


@router.post(
    "/analyze",
    response_model=VisionAnalysisResponse,
    summary="Analyze image for tampering evidence",
    description="""
    Analyze CCTV or drone imagery for signs of track tampering.
    
    **Detectable anomalies:**
    - Missing fish plates (rail connectors)
    - Foreign objects on tracks
    - Track displacement/misalignment
    - Human presence in restricted zones
    - Tools or equipment near tracks
    
    **Returns:**
    - List of detections with confidence scores
    - Bounding boxes for visualization
    - Risk score contribution
    - Human-readable explanations
    
    ⚠️ **Note:** This endpoint uses SIMULATED image data for demo purposes.
    """
)
async def analyze_image(request: VisionAnalysisRequest) -> VisionAnalysisResponse:
    """Analyze an image for tampering evidence."""
    logger.info(f"Vision analysis requested for zone {request.zone_id}")
    
    try:
        response = await vision_service.analyze(request)
        
        # Log to audit trail
        audit_service.log_vision_analysis(
            zone_id=request.zone_id,
            analysis_id=response.analysis_id,
            inputs={
                "zone_id": request.zone_id,
                "image_source": request.image_source.value,
                "timestamp": request.timestamp.isoformat(),
            },
            outputs={
                "detections_count": response.total_detections,
                "risk_score": response.vision_risk_score,
            },
            detections_count=response.total_detections,
            risk_score=response.vision_risk_score,
            processing_time_ms=response.processing_time_ms
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Vision analysis failed: {str(e)}")
        audit_service.log_error(
            error_message=str(e),
            error_type="vision_analysis_error",
            zone_id=request.zone_id
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sources",
    summary="Get available image sources",
    description="List all available image sources (CCTV, drone, mobile)"
)
async def get_image_sources():
    """Get available image sources."""
    return {
        "sources": [s.value for s in ImageSource],
        "descriptions": {
            "cctv": "Fixed CCTV cameras along track",
            "drone": "Patrol drone imagery",
            "mobile": "Mobile patrol officer captures"
        }
    }


@router.get(
    "/stats",
    summary="Get vision service statistics"
)
async def get_stats():
    """Get vision service statistics."""
    return vision_service.get_processing_stats()
