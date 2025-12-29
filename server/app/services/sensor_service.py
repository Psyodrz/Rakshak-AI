"""
Sensor Anomaly Detection Service
---------------------------------
Analyzes sensor data to detect anomalies that may indicate tampering.

DESIGN RATIONALE:
- Uses statistical methods + Isolation Forest-style scoring
- Differentiates between environmental/mechanical/sabotage patterns
- Provides correlation analysis across multiple sensors
- Fully explainable outputs
"""

import uuid
import time
from datetime import datetime
from typing import List, Optional, Tuple

from ..models.sensor import (
    SensorType,
    AnomalyType,
    AnomalySeverity,
    SensorReading,
    SensorAnomaly,
    SensorAnalysisRequest,
    SensorAnalysisResponse,
    SensorStatus,
)
from ..simulation.sensor_generator import sensor_generator
from ..config import config


from ..adapters.simulated import SimulatedSensorAdapter

class SensorService:
    # ... (docstring) ...
    
    def __init__(self):
        """Initialize sensor service."""
        self._processing_count = 0
        self.adapter = SimulatedSensorAdapter()
    
    async def analyze(self, request: SensorAnalysisRequest) -> SensorAnalysisResponse:
        """
        Analyze sensor readings for anomalies.
        
        In production, this would:
        1. Receive streaming sensor data
        2. Apply statistical analysis (z-score, moving average)
        3. Run Isolation Forest for anomaly detection
        4. Correlate across sensors for coordinated anomalies
        5. Calculate risk score
        """
        start_time = time.time()
        analysis_id = f"sens_{uuid.uuid4().hex[:12]}"
        
        # Get sensor readings (simulated or provided)
        if request.readings:
            readings = request.readings
        else:
            # Get readings via adapter
            readings = await self.adapter.get_readings(
                zone_id=request.zone_id
            )
        
        # Run anomaly detection (Service Logic)
        anomalies = self._detect_anomalies(readings)
        
        # Count sensors
        total_sensors = len(readings)
        operational_sensors = sum(1 for r in readings if r.is_operational)
        
        # Check for coordination
        is_coordinated, coord_confidence = self._check_coordination(anomalies)
        
        # Calculate likelihood scores
        likelihoods = sensor_generator.calculate_likelihood_scores(anomalies)
        
        # Calculate risk score
        risk_score, risk_reasons = self._calculate_risk_score(
            anomalies,
            is_coordinated,
            likelihoods
        )
        
        processing_time = (time.time() - start_time) * 1000
        self._processing_count += 1
        
        return SensorAnalysisResponse(
            analysis_id=analysis_id,
            zone_id=request.zone_id,
            timestamp=request.timestamp,
            total_sensors=total_sensors,
            operational_sensors=operational_sensors,
            readings_analyzed=len(readings),
            anomalies=anomalies,
            total_anomalies=len(anomalies),
            is_coordinated=is_coordinated,
            coordination_confidence=coord_confidence,
            sensor_risk_score=risk_score,
            risk_reasons=risk_reasons,
            environmental_likelihood=likelihoods["environmental"],
            mechanical_likelihood=likelihoods["mechanical"],
            sabotage_likelihood=likelihoods["sabotage"],
            processing_time_ms=round(processing_time, 2),
            is_simulated=request.use_simulated
        )
    
    def _detect_anomalies(self, readings: List[SensorReading]) -> List[SensorAnomaly]:
        """
        Detect anomalies from provided sensor readings.
        
        Uses statistical thresholds from config.
        In production, would also use trained Isolation Forest model.
        """
        anomalies = []
        thresholds = config.SENSOR_THRESHOLDS
        
        for reading in readings:
            threshold_config = thresholds.get(reading.sensor_type.value, {})
            if not threshold_config:
                continue
            
            value = reading.value
            normal_range = threshold_config.get("normal_range", (0, 100))
            warning_range = threshold_config.get("warning_range", (0, 100))
            critical_range = threshold_config.get("critical_range", (0, 100))
            
            # Check if outside normal range
            is_normal = normal_range[0] <= value <= normal_range[1]
            is_warning = warning_range[0] <= value <= warning_range[1]
            is_critical = critical_range[0] <= value <= critical_range[1]
            
            if not is_normal:
                severity = AnomalySeverity.NONE
                anomaly_type = AnomalyType.NORMAL
                
                if is_critical:
                    severity = AnomalySeverity.SEVERE
                    anomaly_type = AnomalyType.SUDDEN_CHANGE
                elif is_warning:
                    severity = AnomalySeverity.MODERATE
                    anomaly_type = AnomalyType.MECHANICAL_WEAR
                else:
                    severity = AnomalySeverity.MINOR
                    anomaly_type = AnomalyType.ENVIRONMENTAL_NOISE
                
                if severity != AnomalySeverity.NONE:
                    # Calculate expected value (midpoint of normal range)
                    # SAFETY: Use safe division to prevent division by zero
                    from ..utils.safe_math import safe_divide, safe_clamp
                    
                    expected = (normal_range[0] + normal_range[1]) / 2
                    # Guard against zero or near-zero expected values
                    expected_denominator = max(abs(expected), 0.01)
                    deviation_pct_raw, _ = safe_divide(
                        abs(value - expected), 
                        expected_denominator, 
                        default=0.0,
                        context=f"sensor_deviation_{reading.sensor_id}"
                    )
                    deviation_pct = deviation_pct_raw * 100
                    
                    # z_score approximation with safe clamp
                    z_score = safe_clamp(deviation_pct / 25.0, 0.0, 10.0)
                    isolation_score = safe_clamp(deviation_pct / 100.0, 0.0, 1.0)
                    
                    anomalies.append(SensorAnomaly(
                        anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
                        sensor_id=reading.sensor_id,
                        sensor_type=reading.sensor_type,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        value_observed=value,
                        value_expected=expected,
                        deviation_percent=round(deviation_pct, 2),
                        z_score=z_score,
                        isolation_score=isolation_score,
                        duration_seconds=None,
                        is_recurring=False
                    ))
        
        return anomalies
    
    def _check_coordination(
        self, 
        anomalies: List[SensorAnomaly]
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if anomalies are coordinated across multiple sensors.
        
        Coordinated anomalies (multiple sensors, similar timing) strongly
        indicate intentional tampering rather than random failure.
        """
        if len(anomalies) < 2:
            return False, None
        
        # Check if anomalies span multiple sensor types
        sensor_types = set(a.sensor_type for a in anomalies)
        if len(sensor_types) >= 2:
            # Multiple sensor types = higher coordination likelihood
            confidence = 0.5 + (len(sensor_types) * 0.15)
            
            # Check for severe anomalies
            severe_count = sum(
                1 for a in anomalies 
                if a.severity == AnomalySeverity.SEVERE
            )
            if severe_count >= 2:
                confidence += 0.2
            
            return True, min(confidence, 1.0)
        
        return False, None
    
    def _calculate_risk_score(
        self,
        anomalies: List[SensorAnomaly],
        is_coordinated: bool,
        likelihoods: dict
    ) -> Tuple[float, List[str]]:
        """
        Calculate risk score from sensor anomalies.
        
        ALGORITHM:
        1. Sum weighted contributions from each anomaly
        2. Apply coordination multiplier if applicable
        3. Weight by sabotage likelihood
        4. Cap at 100
        """
        if not anomalies:
            return 0.0, ["All sensor readings within normal parameters"]
        
        total_risk = 0.0
        reasons = []
        
        for anomaly in anomalies:
            # Get base weight based on anomaly type
            type_key = anomaly.anomaly_type.value
            base_weight = config.SENSOR_WEIGHTS.get(type_key, 10)
            
            # Apply severity modifier
            severity_mult = {
                AnomalySeverity.MINOR: 0.5,
                AnomalySeverity.MODERATE: 1.0,
                AnomalySeverity.SEVERE: 1.5,
            }.get(anomaly.severity, 1.0)
            
            contribution = base_weight * severity_mult
            total_risk += contribution
            
            # Generate reason
            reason = self._generate_anomaly_reason(anomaly)
            reasons.append(reason)
        
        # Apply coordination multiplier
        if is_coordinated:
            total_risk *= 1.5
            reasons.append("⚠️ Multiple sensors showing coordinated anomalies - "
                          "indicates potential simultaneous tampering")
        
        # If sabotage likelihood is high, boost score
        if likelihoods["sabotage"] > 0.5:
            total_risk *= 1.2
            reasons.append(f"🔴 Sabotage likelihood: {int(likelihoods['sabotage']*100)}%")
        elif likelihoods["environmental"] > 0.5:
            total_risk *= 0.7  # Reduce if likely environmental
            reasons.append(f"🟢 Likely environmental cause: {int(likelihoods['environmental']*100)}%")
        
        return min(round(total_risk, 2), 100.0), reasons
    
    def _generate_anomaly_reason(self, anomaly: SensorAnomaly) -> str:
        """Generate human-readable reason for an anomaly."""
        sensor_name = anomaly.sensor_type.value.title()
        severity = anomaly.severity.value.title()
        
        type_descriptions = {
            AnomalyType.ENVIRONMENTAL_NOISE: 
                f"🟢 {sensor_name}: Environmental disturbance detected ({severity})",
            AnomalyType.MECHANICAL_WEAR: 
                f"🟡 {sensor_name}: Mechanical wear pattern detected ({severity})",
            AnomalyType.SUDDEN_CHANGE: 
                f"🔴 {sensor_name}: Sudden change detected ({severity}) - "
                f"Deviation: {anomaly.deviation_percent:.1f}%",
            AnomalyType.COORDINATED_ANOMALY: 
                f"🔴 {sensor_name}: Coordinated anomaly ({severity}) - "
                "Multiple sensors affected simultaneously",
            AnomalyType.SENSOR_FAILURE: 
                f"⚠️ {sensor_name}: Sensor malfunction detected",
        }
        
        return type_descriptions.get(
            anomaly.anomaly_type,
            f"{sensor_name}: Anomaly detected ({severity})"
        )
    
    async def get_zone_status(self, zone_id: str) -> SensorStatus:
        """Get sensor status summary for a zone."""
        sensors = sensor_generator._get_zone_sensors(zone_id)
        
        # In real system, would query actual sensor status
        return SensorStatus(
            zone_id=zone_id,
            total_sensors=len(sensors),
            operational=len(sensors) - 1,  # Assume 1 degraded for demo
            degraded=1,
            failed=0,
            last_reading_time=datetime.utcnow()
        )


# Singleton instance
sensor_service = SensorService()
