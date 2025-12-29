"""
Pydantic Models for Intent Classification
------------------------------------------
Models for the core intent classification engine that determines tampering likelihood.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

from .vision import VisionAnalysisResponse, Detection
from .sensor import SensorAnalysisResponse, SensorAnomaly


class TamperingClassification(str, Enum):
    """
    Final classification output.
    
    SAFE: No threat detected, normal operations
    SUSPICIOUS: Anomalies detected, recommend human review
    CONFIRMED_TAMPERING: High confidence tampering, immediate action required
    """
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED_TAMPERING = "CONFIRMED_TAMPERING"


class RiskFactor(BaseModel):
    """
    Individual risk factor contributing to overall score.
    Used for explainability - judges can see exactly why a decision was made.
    """
    factor_id: str = Field(..., description="Unique identifier")
    category: str = Field(..., description="Category: vision, sensor, temporal, behavioral")
    name: str = Field(..., description="Human-readable factor name")
    description: str = Field(..., description="Detailed explanation")
    
    # Contribution to risk
    weight: float = Field(..., description="Weight in scoring (from config)")
    raw_score: float = Field(..., ge=0, le=1, description="Raw factor score (0-1)")
    weighted_contribution: float = Field(..., ge=0, 
        description="Actual points contributed to total")
    
    # Evidence
    evidence: List[str] = Field(default_factory=list,
        description="Supporting evidence for this factor")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in this factor")


class TemporalContext(BaseModel):
    """
    Time-based context for risk assessment.
    Tampering is more likely at certain times/conditions.
    """
    timestamp: datetime = Field(..., description="Time of analysis")
    hour_of_day: int = Field(..., ge=0, le=23)
    is_night_hours: bool = Field(..., description="22:00-05:00")
    is_peak_hours: bool = Field(..., description="Rush hour periods")
    is_maintenance_window: bool = Field(..., description="Scheduled maintenance")
    
    # Risk modifier from temporal context
    time_risk_modifier: float = Field(..., ge=0.5, le=2.0,
        description="Multiplier applied to base risk")
    
    # Reasoning
    temporal_notes: List[str] = Field(default_factory=list)


class IntentClassifyRequest(BaseModel):
    """
    Request for intent classification.
    Can accept pre-computed vision/sensor analysis or trigger new analysis.
    """
    zone_id: str = Field(..., description="Track zone to classify")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Option 1: Provide pre-computed analyses
    vision_analysis: Optional[VisionAnalysisResponse] = Field(default=None)
    sensor_analysis: Optional[SensorAnalysisResponse] = Field(default=None)
    
    # Option 2: Trigger new analyses
    run_vision_analysis: bool = Field(default=False)
    run_sensor_analysis: bool = Field(default=False)
    
    # Simulation settings
    use_simulated: bool = Field(default=True)
    simulate_scenario: Optional[str] = Field(default=None)


class IntentClassifyResponse(BaseModel):
    """
    Complete intent classification response.
    This is the CORE output of RAKSHAK-AI.
    
    Provides:
    - Final classification (SAFE/SUSPICIOUS/CONFIRMED_TAMPERING)
    - Risk score (0-100)
    - Complete explainability via risk factors
    - Audit trail information
    """
    classification_id: str = Field(..., description="Unique ID for audit")
    zone_id: str = Field(..., description="Classified zone")
    timestamp: datetime = Field(..., description="Classification time")
    
    # ==========================================================================
    # CORE OUTPUT - What operators need to act on
    # ==========================================================================
    
    classification: TamperingClassification = Field(..., 
        description="Final classification decision")
    risk_score: float = Field(..., ge=0, le=100,
        description="Overall risk score (0=safe, 100=definite tampering)")
    confidence: float = Field(..., ge=0, le=1,
        description="Confidence in classification (0-1)")
    
    # ==========================================================================
    # EXPLAINABILITY - Why this decision was made
    # ==========================================================================
    
    risk_factors: List[RiskFactor] = Field(default_factory=list,
        description="All factors contributing to risk score")
    
    # Summary reasons (for UI display)
    primary_reasons: List[str] = Field(default_factory=list,
        description="Top reasons for this classification")
    
    # Recommended actions
    recommended_actions: List[str] = Field(default_factory=list,
        description="Suggested actions based on classification")
    
    # ==========================================================================
    # COMPONENT SCORES
    # ==========================================================================
    
    vision_risk_score: float = Field(..., ge=0, le=100)
    sensor_risk_score: float = Field(..., ge=0, le=100)
    temporal_modifier: float = Field(..., ge=0.5, le=2.0)
    
    # Temporal context
    temporal_context: TemporalContext
    
    # ==========================================================================
    # SOURCE DATA REFERENCES
    # ==========================================================================
    
    vision_analysis_id: Optional[str] = Field(default=None)
    sensor_analysis_id: Optional[str] = Field(default=None)
    
    # ==========================================================================
    # METADATA
    # ==========================================================================
    
    processing_time_ms: float = Field(..., description="Total processing time")
    is_simulated: bool = Field(default=True)
    model_version: str = Field(default="1.0.0")


class ClassificationHistory(BaseModel):
    """Historical classification for timeline view."""
    classification_id: str
    zone_id: str
    timestamp: datetime
    classification: TamperingClassification
    risk_score: float
    was_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
