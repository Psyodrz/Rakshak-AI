"""
Pydantic Models for Vision Detection
-------------------------------------
These models define the data structures for vision-based tampering detection.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DetectionClass(str, Enum):
    """
    Classes of objects/anomalies that can be detected in track imagery.
    Each class has specific implications for tampering assessment.
    """
    MISSING_FISH_PLATE = "missing_fish_plate"  # Critical: joins rail sections
    FOREIGN_OBJECT = "foreign_object"          # Debris or deliberate obstruction
    TRACK_DISPLACEMENT = "track_displacement"  # Rail moved from alignment
    HUMAN_PRESENCE = "human_presence"          # Person in restricted zone
    TOOL_DETECTION = "tool_detection"          # Tools near track = high risk
    VEHICLE_NEAR_TRACK = "vehicle_near_track"  # Unauthorized vehicle
    NORMAL = "normal"                          # No anomaly detected


class ImageSource(str, Enum):
    """Type of image source for detection."""
    CCTV = "cctv"
    DRONE = "drone"
    MOBILE = "mobile"  # Patrol officer mobile capture


class ImageCondition(str, Enum):
    """
    Environmental/quality conditions affecting image analysis.
    These conditions may reduce detection confidence.
    """
    NORMAL = "normal"
    LOW_LIGHT = "low_light"
    BLUR = "blur"
    PARTIAL_OCCLUSION = "partial_occlusion"
    RAIN = "rain"
    FOG = "fog"


class BoundingBox(BaseModel):
    """
    Bounding box coordinates for a detection.
    Uses normalized coordinates (0-1) for resolution independence.
    """
    x_min: float = Field(..., ge=0, le=1, description="Left edge (0-1)")
    y_min: float = Field(..., ge=0, le=1, description="Top edge (0-1)")
    x_max: float = Field(..., ge=0, le=1, description="Right edge (0-1)")
    y_max: float = Field(..., ge=0, le=1, description="Bottom edge (0-1)")
    
    @property
    def area(self) -> float:
        """Calculate bounding box area as fraction of image."""
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)


class Detection(BaseModel):
    """
    Single detection result from vision analysis.
    Includes bounding box, classification, and confidence.
    """
    detection_id: str = Field(..., description="Unique ID for this detection")
    class_label: DetectionClass = Field(..., description="Detected object class")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    bounding_box: BoundingBox = Field(..., description="Location in image")
    
    # Additional metadata for explainability
    raw_confidence: float = Field(..., ge=0, le=1, 
        description="Original confidence before condition adjustments")
    condition_penalty_applied: bool = Field(default=False,
        description="Whether image condition reduced confidence")


class VisionAnalysisRequest(BaseModel):
    """Request payload for vision analysis endpoint."""
    zone_id: str = Field(..., description="Track zone identifier")
    image_source: ImageSource = Field(..., description="Source of image")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # For simulation - in production, raw image bytes would be sent
    use_simulated: bool = Field(default=True, 
        description="Use simulated image data (for demo)")
    simulate_scenario: Optional[str] = Field(default=None,
        description="Specific scenario to simulate: 'normal', 'tampering', 'suspicious'")


class VisionAnalysisResponse(BaseModel):
    """
    Complete response from vision analysis.
    Contains all detections and metadata for audit trail.
    """
    analysis_id: str = Field(..., description="Unique analysis ID for audit")
    zone_id: str = Field(..., description="Analyzed zone")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    
    # Image metadata
    image_source: ImageSource
    image_conditions: List[ImageCondition] = Field(default_factory=list)
    
    # Detection results
    detections: List[Detection] = Field(default_factory=list)
    total_detections: int = Field(..., description="Count of detections")
    
    # Risk contribution
    vision_risk_score: float = Field(..., ge=0, le=100,
        description="Risk contribution from vision analysis (0-100)")
    
    # Explainability
    risk_reasons: List[str] = Field(default_factory=list,
        description="Human-readable reasons for risk score")
    
    # Processing metadata
    processing_time_ms: float = Field(..., description="Analysis time in milliseconds")
    is_simulated: bool = Field(default=True, description="Whether data is simulated")
    
    # For demo visualization
    annotated_image_url: Optional[str] = Field(default=None,
        description="URL to image with detection boxes drawn")
