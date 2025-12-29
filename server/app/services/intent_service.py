"""
Intent Classification Engine
-----------------------------
The CORE intelligence of RAKSHAK-AI.

Combines vision + sensor analysis with temporal context to determine
whether detected anomalies represent intentional tampering.

DESIGN RATIONALE:
- Rule-based + weighted scoring for transparency
- Every decision is explainable via risk factors
- Temporal context affects risk (night = higher risk)
- Conservative thresholds (safety-critical = prefer false positives)
"""

import uuid
import time
from datetime import datetime
from typing import List, Optional, Tuple

from ..models.intent import (
    TamperingClassification,
    RiskFactor,
    TemporalContext,
    IntentClassifyRequest,
    IntentClassifyResponse,
    TamperingClassification,
)
from ..models.vision import VisionAnalysisRequest, VisionAnalysisResponse
from ..models.sensor import SensorAnalysisRequest, SensorAnalysisResponse
from .vision_service import vision_service
from .sensor_service import sensor_service
from ..config import config


class IntentService:
    """
    Intent classification engine.
    
    The brain of RAKSHAK-AI. Takes evidence from vision and sensors,
    applies contextual analysis, and produces a classification with
    full explainability.
    
    Classification Outputs:
    - SAFE: No threat, normal operations
    - SUSPICIOUS: Anomalies detected, recommend investigation
    - CONFIRMED_TAMPERING: High confidence tampering, immediate action
    """
    
    def __init__(self):
        """Initialize intent service."""
        self._classification_count = 0
    
    async def classify(self, request: IntentClassifyRequest) -> IntentClassifyResponse:
        """
        Main classification entry point.
        
        ALGORITHM:
        1. Get/run vision analysis
        2. Get/run sensor analysis
        3. Calculate temporal context
        4. Combine scores with weighted formula
        5. Generate risk factors for explainability
        6. Classify based on thresholds
        7. Generate recommended actions
        """
        start_time = time.time()
        classification_id = f"cls_{uuid.uuid4().hex[:12]}"
        
        # Step 1: Get vision analysis
        vision_analysis = request.vision_analysis
        if vision_analysis is None and request.run_vision_analysis:
            vision_request = VisionAnalysisRequest(
                zone_id=request.zone_id,
                image_source="cctv",
                timestamp=request.timestamp,
                use_simulated=request.use_simulated,
                simulate_scenario=request.simulate_scenario
            )
            vision_analysis = await vision_service.analyze(vision_request)
        
        # Step 2: Get sensor analysis
        sensor_analysis = request.sensor_analysis
        if sensor_analysis is None and request.run_sensor_analysis:
            sensor_request = SensorAnalysisRequest(
                zone_id=request.zone_id,
                timestamp=request.timestamp,
                use_simulated=request.use_simulated,
                simulate_scenario=request.simulate_scenario
            )
            sensor_analysis = await sensor_service.analyze(sensor_request)
        
        # Step 3: Calculate temporal context
        temporal_context = self._calculate_temporal_context(request.timestamp)
        
        # Step 4: Calculate combined risk score with SAFETY GUARDS
        from ..utils.safe_math import safe_clamp, safe_risk_score
        from ..utils.logger import logger
        
        # Default to 0 if analysis is None
        vision_score = vision_analysis.vision_risk_score if vision_analysis else 0.0
        sensor_score = sensor_analysis.sensor_risk_score if sensor_analysis else 0.0
        
        # Ensure input scores are valid
        vision_score = safe_clamp(vision_score, 0.0, 100.0)
        sensor_score = safe_clamp(sensor_score, 0.0, 100.0)
        
        # Weighted combination: Vision 45%, Sensor 45%, Temporal 10%
        base_score = (vision_score * 0.45) + (sensor_score * 0.45)
        
        # Apply temporal modifier (ensure it's >= 0)
        temporal_mod = max(temporal_context.time_risk_modifier, 0.0)
        final_score = base_score * temporal_mod
        
        # CRITICAL SAFETY: Clamp to valid range and log any adjustments
        final_score, clamp_reason = safe_risk_score(final_score, context="final_score_calculation")
        if clamp_reason:
            logger.warning(f"Score clamped: {clamp_reason} (vision={vision_score}, sensor={sensor_score}, temporal={temporal_mod})")
        
        # Step 5: Generate risk factors
        risk_factors = self._generate_risk_factors(
            vision_analysis,
            sensor_analysis,
            temporal_context
        )
        
        # Step 6: Classify
        classification, confidence = self._determine_classification(
            final_score,
            vision_analysis,
            sensor_analysis
        )
        
        # Step 7: Generate primary reasons and recommendations
        primary_reasons = self._generate_primary_reasons(
            classification,
            risk_factors,
            vision_analysis,
            sensor_analysis
        )
        
        recommended_actions = self._generate_recommendations(
            classification,
            final_score
        )
        
        processing_time = (time.time() - start_time) * 1000
        self._classification_count += 1
        
        response = IntentClassifyResponse(
            classification_id=classification_id,
            zone_id=request.zone_id,
            timestamp=request.timestamp,
            classification=classification,
            risk_score=round(final_score, 2),
            confidence=confidence,
            risk_factors=risk_factors,
            primary_reasons=primary_reasons,
            recommended_actions=recommended_actions,
            vision_risk_score=vision_score,
            sensor_risk_score=sensor_score,
            temporal_modifier=temporal_context.time_risk_modifier,
            temporal_context=temporal_context,
            vision_analysis_id=vision_analysis.analysis_id if vision_analysis else None,
            sensor_analysis_id=sensor_analysis.analysis_id if sensor_analysis else None,
            processing_time_ms=round(processing_time, 2),
            is_simulated=request.use_simulated,
            model_version="1.0.0"
        )
        
        # Broadcast result to real-time clients
        from ..websockets import manager
        await manager.broadcast({
            "type": "ALERT_NEW" if classification != TamperingClassification.SAFE else "ANALYSIS_UPDATE",
            "payload": response.model_dump(mode="json"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return response
    
    def _calculate_temporal_context(self, timestamp: datetime) -> TemporalContext:
        """
        Calculate temporal context for risk assessment.
        
        Time of day significantly affects tampering likelihood:
        - Night hours (22:00-05:00): Higher risk
        - Early morning (05:00-07:00): Elevated risk
        - Peak hours: Lower risk (more witnesses)
        """
        hour = timestamp.hour
        
        is_night = hour >= 22 or hour < 5
        is_early_morning = 5 <= hour < 7
        is_peak = (7 <= hour < 10) or (17 <= hour < 20)
        
        # Calculate risk modifier
        if is_night:
            modifier = config.TIME_WEIGHTS["night_hours"]
        elif is_early_morning:
            modifier = config.TIME_WEIGHTS["early_morning"]
        elif is_peak:
            modifier = config.TIME_WEIGHTS["peak_hours"]
        else:
            modifier = 1.0
        
        notes = []
        if is_night:
            notes.append("🌙 Night hours - elevated tampering risk period")
        if is_early_morning:
            notes.append("🌅 Early morning - reduced visibility period")
        if is_peak:
            notes.append("🚂 Peak hours - increased monitoring")
        
        return TemporalContext(
            timestamp=timestamp,
            hour_of_day=hour,
            is_night_hours=is_night,
            is_peak_hours=is_peak,
            is_maintenance_window=False,  # Would be checked against schedule
            time_risk_modifier=modifier,
            temporal_notes=notes
        )
    
    def _generate_risk_factors(
        self,
        vision_analysis: Optional[VisionAnalysisResponse],
        sensor_analysis: Optional[SensorAnalysisResponse],
        temporal_context: TemporalContext
    ) -> List[RiskFactor]:
        """
        Generate detailed risk factors for explainability.
        
        Each factor shows exactly how it contributed to the score.
        """
        factors = []
        
        # Vision factors
        if vision_analysis:
            for detection in vision_analysis.detections:
                weight = config.VISION_WEIGHTS.get(detection.class_label.value, 10)
                contribution = weight * detection.confidence
                
                factors.append(RiskFactor(
                    factor_id=f"v_{detection.detection_id}",
                    category="vision",
                    name=detection.class_label.value.replace("_", " ").title(),
                    description=f"Visual detection of {detection.class_label.value}",
                    weight=weight,
                    raw_score=detection.confidence,
                    weighted_contribution=round(contribution, 2),
                    evidence=[
                        f"Detected with {detection.confidence*100:.1f}% confidence",
                        f"Bounding box area: {detection.bounding_box.area*100:.1f}% of image"
                    ],
                    confidence=detection.confidence
                ))
        
        # Sensor factors
        if sensor_analysis:
            for anomaly in sensor_analysis.anomalies:
                weight = config.SENSOR_WEIGHTS.get(anomaly.anomaly_type.value, 10)
                
                # Severity multiplier
                sev_mult = {"minor": 0.5, "moderate": 1.0, "severe": 1.5}.get(
                    anomaly.severity.value.lower(), 1.0
                )
                contribution = weight * sev_mult
                
                factors.append(RiskFactor(
                    factor_id=f"s_{anomaly.anomaly_id}",
                    category="sensor",
                    name=f"{anomaly.sensor_type.value.title()} {anomaly.anomaly_type.value.replace('_', ' ')}",
                    description=f"Sensor anomaly from {anomaly.sensor_id}",
                    weight=weight,
                    raw_score=anomaly.isolation_score or 0.5,
                    weighted_contribution=round(contribution, 2),
                    evidence=[
                        f"Observed: {anomaly.value_observed}, Expected: {anomaly.value_expected}",
                        f"Deviation: {anomaly.deviation_percent:.1f}%",
                        f"Severity: {anomaly.severity.value}"
                    ],
                    confidence=anomaly.isolation_score or 0.5
                ))
            
            # Coordination factor if applicable
            if sensor_analysis.is_coordinated:
                factors.append(RiskFactor(
                    factor_id="s_coordination",
                    category="sensor",
                    name="Sensor Coordination",
                    description="Multiple sensors showing coordinated anomalies",
                    weight=40,
                    raw_score=sensor_analysis.coordination_confidence or 0.7,
                    weighted_contribution=40 * (sensor_analysis.coordination_confidence or 0.7),
                    evidence=[
                        f"Coordination confidence: {(sensor_analysis.coordination_confidence or 0)*100:.1f}%",
                        "Multiple sensor types affected simultaneously"
                    ],
                    confidence=sensor_analysis.coordination_confidence or 0.7
                ))
        
        # Temporal factor
        # Only add as risk factor if it increases risk (> 1.0)
        # We don't list risk reducers as risk factors
        if temporal_context.time_risk_modifier > 1.0:
            factors.append(RiskFactor(
                factor_id="t_temporal",
                category="temporal",
                name="Time of Day Risk",
                description="Temporal risk modifier based on time",
                weight=10,
                raw_score=temporal_context.time_risk_modifier - 1.0,
                weighted_contribution=10 * (temporal_context.time_risk_modifier - 1.0),
                evidence=temporal_context.temporal_notes,
                confidence=0.9
            ))
        
        return factors
    
    def _determine_classification(
        self,
        risk_score: float,
        vision_analysis: Optional[VisionAnalysisResponse],
        sensor_analysis: Optional[SensorAnalysisResponse]
    ) -> Tuple[TamperingClassification, float]:
        """
        Determine final classification based on risk score and evidence.
        
        Thresholds are from config:
        - Below SAFE threshold: SAFE
        - Below SUSPICIOUS threshold: SUSPICIOUS  
        - Above SUSPICIOUS threshold: CONFIRMED_TAMPERING
        """
        # Check for high-confidence specific detections that override score
        if vision_analysis:
            for d in vision_analysis.detections:
                # Missing fish plate or track displacement with high confidence
                # is automatic CONFIRMED_TAMPERING
                if d.class_label.value in ["missing_fish_plate", "track_displacement"]:
                    if d.confidence >= 0.85:
                        return TamperingClassification.CONFIRMED_TAMPERING, d.confidence
        
        # Check for coordinated sensor anomalies
        if sensor_analysis and sensor_analysis.is_coordinated:
            if sensor_analysis.sabotage_likelihood >= 0.7:
                return TamperingClassification.CONFIRMED_TAMPERING, sensor_analysis.sabotage_likelihood
        
        # Standard threshold-based classification
        # SAFETY: Guard against division by zero in confidence calculations
        threshold_safe = max(config.RISK_THRESHOLD_SAFE, 0.01)  # Prevent zero
        threshold_suspicious = max(config.RISK_THRESHOLD_SUSPICIOUS, threshold_safe + 0.01)
        suspicious_range = threshold_suspicious - threshold_safe
        tampering_range = 100.0 - threshold_suspicious
        
        if risk_score < threshold_safe:
            # Safe range: confidence decreases as risk increases toward threshold
            confidence = 1.0 - (risk_score / threshold_safe) if threshold_safe > 0 else 1.0
            return TamperingClassification.SAFE, round(max(confidence, 0.0), 2)
        elif risk_score < threshold_suspicious:
            # Suspicious range with safe division
            if suspicious_range > 0:
                confidence = 0.5 + ((risk_score - threshold_safe) / suspicious_range * 0.3)
            else:
                confidence = 0.65
            return TamperingClassification.SUSPICIOUS, round(confidence, 2)
        else:
            # Confirmed tampering range with safe division
            if tampering_range > 0:
                confidence = 0.7 + ((risk_score - threshold_suspicious) / tampering_range * 0.3)
            else:
                confidence = 0.85
            return TamperingClassification.CONFIRMED_TAMPERING, round(min(confidence, 1.0), 2)
    
    def _generate_primary_reasons(
        self,
        classification: TamperingClassification,
        risk_factors: List[RiskFactor],
        vision_analysis: Optional[VisionAnalysisResponse],
        sensor_analysis: Optional[SensorAnalysisResponse]
    ) -> List[str]:
        """Generate top reasons for the classification (for UI display)."""
        reasons = []
        
        if classification == TamperingClassification.SAFE:
            reasons.append("✅ No significant anomalies detected")
            reasons.append("✅ All sensor readings within normal parameters")
            return reasons
        
        # Sort risk factors by contribution
        sorted_factors = sorted(
            risk_factors, 
            key=lambda f: f.weighted_contribution, 
            reverse=True
        )
        
        # Take top 3 contributing factors
        for factor in sorted_factors[:3]:
            if factor.weighted_contribution > 0:
                reasons.append(f"• {factor.name}: contributed {factor.weighted_contribution:.1f} risk points")
        
        # Add specific high-priority reasons
        if vision_analysis:
            for reason in vision_analysis.risk_reasons[:2]:
                if reason not in reasons:
                    reasons.append(reason)
        
        if sensor_analysis:
            for reason in sensor_analysis.risk_reasons[:2]:
                if reason not in reasons:
                    reasons.append(reason)
        
        return reasons[:5]  # Max 5 reasons
    
    def _generate_recommendations(
        self,
        classification: TamperingClassification,
        risk_score: float
    ) -> List[str]:
        """Generate recommended actions based on classification."""
        if classification == TamperingClassification.SAFE:
            return [
                "Continue normal monitoring",
                "No immediate action required"
            ]
        
        if classification == TamperingClassification.SUSPICIOUS:
            return [
                "🟡 Dispatch patrol to verify zone condition",
                "🟡 Review CCTV footage for the past hour",
                "🟡 Cross-check with adjacent zone sensors",
                "⏱️ Re-analyze in 5 minutes"
            ]
        
        # CONFIRMED_TAMPERING
        actions = [
            "🔴 IMMEDIATE: Alert zone supervisor",
            "🔴 IMMEDIATE: Notify train control to halt approach"
        ]
        
        if risk_score >= 85:
            actions.insert(0, "🚨 CRITICAL: Stop all trains in zone immediately")
            actions.append("🔴 Dispatch emergency response team")
            actions.append("🔴 Activate backup communication channels")
        else:
            actions.append("🔴 Reduce train speed in zone to 20km/h")
            actions.append("🔴 Dispatch maintenance crew for inspection")
        
        return actions


# Singleton instance
intent_service = IntentService()
