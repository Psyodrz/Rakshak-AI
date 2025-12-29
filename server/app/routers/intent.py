"""
Intent Classification API Routes
---------------------------------
Core endpoint for tampering intent classification.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from ..models.intent import (
    IntentClassifyRequest,
    IntentClassifyResponse,
    TamperingClassification,
)
from ..services.intent_service import intent_service
from ..services.alert_service import alert_service
from ..services.audit_service import audit_service
from ..utils.logger import logger

router = APIRouter(prefix="/intent", tags=["Intent Classification"])


@router.post(
    "/classify",
    response_model=IntentClassifyResponse,
    summary="Classify tampering intent",
    description="""
    **THE CORE INTELLIGENCE ENDPOINT**
    
    Combines vision and sensor analysis with temporal context to determine
    whether detected anomalies represent intentional track tampering.
    
    **Algorithm:**
    1. Run/receive vision analysis
    2. Run/receive sensor analysis  
    3. Calculate temporal risk modifier
    4. Combine with weighted formula
    5. Generate explainable risk factors
    6. Classify as SAFE / SUSPICIOUS / CONFIRMED_TAMPERING
    7. Generate recommended actions
    
    **Classification outputs:**
    - **SAFE**: No threat detected, normal operations
    - **SUSPICIOUS**: Anomalies detected, recommend investigation
    - **CONFIRMED_TAMPERING**: High confidence tampering, immediate action
    
    **Explainability:**
    Every decision includes detailed risk factors explaining exactly
    WHY the system reached its conclusion. This is critical for:
    - Operator trust
    - Audit compliance
    - Continuous improvement
    """
)
async def classify_intent(request: IntentClassifyRequest) -> IntentClassifyResponse:
    """Classify tampering intent from combined evidence."""
    logger.info(f"Intent classification requested for zone {request.zone_id}")
    
    try:
        response = await intent_service.classify(request)
        
        # Log to audit trail
        audit_service.log_intent_classification(
            zone_id=request.zone_id,
            classification_id=response.classification_id,
            classification=response.classification.value,
            risk_score=response.risk_score,
            confidence=response.confidence,
            risk_factors=[f.name for f in response.risk_factors],
            recommended_actions=response.recommended_actions,
            processing_time_ms=response.processing_time_ms
        )
        
        # Create alert if warranted
        if response.classification != TamperingClassification.SAFE:
            alert = alert_service.create_alert_from_classification(
                zone_id=response.zone_id,
                classification_id=response.classification_id,
                classification=response.classification,
                risk_score=response.risk_score,
                reasons=response.primary_reasons
            )
            
            if alert:
                logger.info(f"Alert created: {alert.alert_id} for zone {request.zone_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Intent classification failed: {str(e)}")
        audit_service.log_error(
            error_message=str(e),
            error_type="intent_classification_error",
            zone_id=request.zone_id
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/classifications",
    summary="Get classification type descriptions"
)
async def get_classification_types():
    """Get descriptions of classification types."""
    return {
        "classifications": {
            "SAFE": {
                "description": "No threat detected, normal operations",
                "action": "Continue monitoring",
                "color": "#22c55e"  # Green
            },
            "SUSPICIOUS": {
                "description": "Anomalies detected, investigation recommended",
                "action": "Dispatch patrol, review footage",
                "color": "#f59e0b"  # Amber
            },
            "CONFIRMED_TAMPERING": {
                "description": "High confidence tampering, immediate action required",
                "action": "Alert control, halt trains, emergency response",
                "color": "#ef4444"  # Red
            }
        }
    }


@router.get(
    "/thresholds",
    summary="Get current classification thresholds"
)
async def get_thresholds():
    """Get current risk score thresholds."""
    from ..config import config
    
    return {
        "safe_threshold": config.RISK_THRESHOLD_SAFE,
        "suspicious_threshold": config.RISK_THRESHOLD_SUSPICIOUS,
        "description": {
            "0 - safe_threshold": "SAFE",
            "safe_threshold - suspicious_threshold": "SUSPICIOUS", 
            "above suspicious_threshold": "CONFIRMED_TAMPERING"
        }
    }
