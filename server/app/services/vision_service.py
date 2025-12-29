"""
Vision Detection Service
------------------------
Processes CCTV and drone imagery to detect tampering evidence.

DESIGN RATIONALE:
- Uses simulated detection for hackathon demo
- Production would integrate YOLO/Faster R-CNN models
- Returns standardized detection format regardless of underlying model
- Includes explainability for each detection
"""

import uuid
import time
from datetime import datetime
from typing import List, Optional

from ..models.vision import (
    DetectionClass,
    ImageSource,
    ImageCondition,
    Detection,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from ..simulation.image_generator import image_generator
from ..config import config


from ..adapters.simulated import SimulatedVisionAdapter

class VisionService:
    # ... (docstring omitted for brevity) ...
    
    def __init__(self):
        """Initialize vision service."""
        self._processing_count = 0
        # Initialize adapter
        self.adapter = SimulatedVisionAdapter()
    
    async def analyze(self, request: VisionAnalysisRequest) -> VisionAnalysisResponse:
        """
        Analyze an image for tampering evidence.
        
        This is the main entry point for vision analysis.
        In production, this would:
        1. Receive raw image bytes
        2. Preprocess (resize, normalize)
        3. Run through detection model (YOLO/Faster R-CNN)
        4. Post-process detections
        5. Calculate risk score
        
        For demo, we use simulated detections.
        """
        start_time = time.time()
        analysis_id = f"vis_{uuid.uuid4().hex[:12]}"
        
        # Get detections via adapter
        detections, conditions = await self.adapter.get_detections(
            zone_id=request.zone_id,
            source_id=request.image_source
        )
        
        # Filter by confidence threshold
        filtered_detections = [
            d for d in detections 
            if d.confidence >= config.VISION_CONFIDENCE_THRESHOLD
        ]
        
        # Calculate risk score
        risk_score, risk_reasons = self._calculate_risk_score(
            filtered_detections, 
            conditions
        )
        
        processing_time = (time.time() - start_time) * 1000
        self._processing_count += 1
        
        return VisionAnalysisResponse(
            analysis_id=analysis_id,
            zone_id=request.zone_id,
            timestamp=request.timestamp,
            image_source=request.image_source,
            image_conditions=conditions,
            detections=filtered_detections,
            total_detections=len(filtered_detections),
            vision_risk_score=risk_score,
            risk_reasons=risk_reasons,
            processing_time_ms=round(processing_time, 2),
            is_simulated=request.use_simulated,
            annotated_image_url=None  # Would be set in production
        )
    
    def _calculate_risk_score(
        self, 
        detections: List[Detection],
        conditions: List[ImageCondition]
    ) -> tuple[float, List[str]]:
        """
        Calculate risk score from detections.
        
        ALGORITHM:
        1. Sum weighted contributions from each detection
        2. Weight by confidence (higher confidence = more risk)
        3. Apply condition modifiers (poor visibility = less certainty)
        4. Cap at 100
        
        Returns: (risk_score, list of reasons)
        """
        if not detections:
            return 0.0, ["No anomalies detected in image"]
        
        total_risk = 0.0
        reasons = []
        
        for detection in detections:
            # Get base weight for this detection class
            class_key = detection.class_label.value
            base_weight = config.VISION_WEIGHTS.get(class_key, 10)
            
            # Apply confidence weighting
            weighted_contribution = base_weight * detection.confidence
            total_risk += weighted_contribution
            
            # Generate human-readable reason
            reason = self._generate_detection_reason(detection)
            reasons.append(reason)
        
        # Apply condition penalty to overall score if applicable
        has_poor_visibility = any(
            c in [ImageCondition.LOW_LIGHT, ImageCondition.FOG, 
                  ImageCondition.BLUR, ImageCondition.PARTIAL_OCCLUSION]
            for c in conditions
        )
        
        if has_poor_visibility:
            total_risk *= 0.85  # Reduce confidence due to poor visibility
            reasons.append("⚠️ Image quality reduced detection confidence")
        
        # Cap at 100
        final_score = min(total_risk, 100.0)
        
        return round(final_score, 2), reasons
    
    def _generate_detection_reason(self, detection: Detection) -> str:
        """
        Generate human-readable reason for a detection.
        
        This is crucial for explainability - operators need to understand
        WHY the system flagged something.
        """
        class_label = detection.class_label
        confidence_pct = int(detection.confidence * 100)
        
        reasons_map = {
            DetectionClass.MISSING_FISH_PLATE: 
                f"🔴 Missing fish plate detected ({confidence_pct}% confidence) - "
                "Critical structural component that joins rail sections",
            DetectionClass.FOREIGN_OBJECT: 
                f"🟠 Foreign object on track ({confidence_pct}% confidence) - "
                "Could be debris or deliberate obstruction",
            DetectionClass.TRACK_DISPLACEMENT: 
                f"🔴 Track displacement detected ({confidence_pct}% confidence) - "
                "Rail appears misaligned from normal position",
            DetectionClass.HUMAN_PRESENCE: 
                f"🟡 Unauthorized person detected ({confidence_pct}% confidence) - "
                "Human presence in restricted track zone",
            DetectionClass.TOOL_DETECTION: 
                f"🟠 Tools detected near track ({confidence_pct}% confidence) - "
                "Equipment that could be used for tampering",
            DetectionClass.VEHICLE_NEAR_TRACK: 
                f"🟡 Vehicle near track ({confidence_pct}% confidence) - "
                "Unauthorized vehicle access to track area",
            DetectionClass.NORMAL:
                "✅ Normal track conditions observed",
        }
        
        return reasons_map.get(
            class_label, 
            f"Anomaly detected: {class_label.value} ({confidence_pct}% confidence)"
        )
    
    def get_processing_stats(self) -> dict:
        """Get service statistics."""
        return {
            "total_processed": self._processing_count,
            "confidence_threshold": config.VISION_CONFIDENCE_THRESHOLD,
        }


# Singleton instance
vision_service = VisionService()
