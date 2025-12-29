"""
Sensor Data Generator - Simulated Vibration, Tilt, and Pressure Sensors
------------------------------------------------------------------------
Generates simulated sensor readings that mimic real IoT sensor output.

In production, this would be replaced with:
- MQTT/gRPC sensor data streams
- Edge computing preprocessing
- Real-time sensor fusion

For hackathon demo, we simulate realistic sensor patterns including:
- Normal baseline readings with noise
- Environmental disturbances (weather, wildlife)
- Mechanical wear patterns
- Sabotage-like sudden anomalies
"""

import random
import uuid
import math
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

from ..models.sensor import (
    SensorType,
    AnomalyType,
    AnomalySeverity,
    SensorReading,
    SensorAnomaly,
)
from ..config import config


class SensorGenerator:
    """
    Simulated sensor data generator.
    
    Produces sensor readings and anomalies that mimic real IoT sensors.
    Can simulate various scenarios from normal operation to sabotage.
    """
    
    # Baseline values for each sensor type
    BASELINES = {
        SensorType.VIBRATION: {
            "normal_mean": 15.0,      # Normal vibration amplitude
            "normal_std": 5.0,        # Standard deviation
            "train_passing_mean": 45.0,
            "train_passing_std": 10.0,
            "unit": "mm/s",
        },
        SensorType.TILT: {
            "normal_mean": 0.0,       # Degrees from baseline
            "normal_std": 0.3,
            "unit": "degrees",
        },
        SensorType.PRESSURE: {
            "normal_mean": 1.0,       # Ratio to expected load
            "normal_std": 0.05,
            "unit": "ratio",
        },
    }
    
    # Anomaly patterns for different scenarios
    SCENARIOS = {
        "normal": {
            "description": "Normal sensor readings",
            "anomaly_probability": 0.0,
            "patterns": [],
        },
        "environmental": {
            "description": "Environmental disturbance (weather, wildlife)",
            "anomaly_probability": 0.3,
            "patterns": [
                {
                    "sensor_types": [SensorType.VIBRATION],
                    "anomaly_type": AnomalyType.ENVIRONMENTAL_NOISE,
                    "severity": AnomalySeverity.MINOR,
                    "deviation_range": (1.5, 2.5),
                },
            ],
        },
        "mechanical": {
            "description": "Mechanical wear patterns",
            "anomaly_probability": 0.5,
            "patterns": [
                {
                    "sensor_types": [SensorType.VIBRATION, SensorType.TILT],
                    "anomaly_type": AnomalyType.MECHANICAL_WEAR,
                    "severity": AnomalySeverity.MODERATE,
                    "deviation_range": (2.0, 3.5),
                },
            ],
        },
        "sabotage": {
            "description": "Sudden sabotage-like anomalies",
            "anomaly_probability": 0.9,
            "patterns": [
                {
                    "sensor_types": [SensorType.VIBRATION, SensorType.TILT, SensorType.PRESSURE],
                    "anomaly_type": AnomalyType.SUDDEN_CHANGE,
                    "severity": AnomalySeverity.SEVERE,
                    "deviation_range": (4.0, 8.0),
                },
                {
                    "sensor_types": [SensorType.TILT, SensorType.PRESSURE],
                    "anomaly_type": AnomalyType.COORDINATED_ANOMALY,
                    "severity": AnomalySeverity.SEVERE,
                    "deviation_range": (5.0, 10.0),
                },
            ],
        },
        "sensor_failure": {
            "description": "Sensor malfunction",
            "anomaly_probability": 0.8,
            "patterns": [
                {
                    "sensor_types": [SensorType.VIBRATION],
                    "anomaly_type": AnomalyType.SENSOR_FAILURE,
                    "severity": AnomalySeverity.MODERATE,
                    "deviation_range": (0, 0),  # Zero reading
                },
            ],
        },
    }
    
    def __init__(self):
        """Initialize the sensor generator."""
        self.last_scenario = None
        # Track sensor IDs per zone for consistency
        self._zone_sensors: Dict[str, List[str]] = {}
    
    def _get_zone_sensors(self, zone_id: str) -> List[Tuple[str, SensorType]]:
        """
        Get or create sensors for a zone.
        Each zone has 3 vibration, 2 tilt, and 2 pressure sensors.
        """
        if zone_id not in self._zone_sensors:
            sensors = []
            for i in range(3):
                sensors.append((f"{zone_id}_VIB_{i:02d}", SensorType.VIBRATION))
            for i in range(2):
                sensors.append((f"{zone_id}_TILT_{i:02d}", SensorType.TILT))
            for i in range(2):
                sensors.append((f"{zone_id}_PRES_{i:02d}", SensorType.PRESSURE))
            self._zone_sensors[zone_id] = sensors
        return self._zone_sensors[zone_id]
    
    def generate_readings(
        self,
        zone_id: str,
        scenario: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Tuple[List[SensorReading], List[SensorAnomaly]]:
        """
        Generate simulated sensor readings for a zone.
        
        Args:
            zone_id: Track zone identifier
            scenario: Specific scenario to simulate (or random if None)
            timestamp: Time of readings
            
        Returns:
            Tuple of (list of readings, list of anomalies)
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Determine scenario
        if scenario and scenario in self.SCENARIOS:
            selected_scenario = scenario
        else:
            # Random scenario weighted towards normal
            roll = random.random()
            if roll < 0.65:
                selected_scenario = "normal"
            elif roll < 0.80:
                selected_scenario = "environmental"
            elif roll < 0.90:
                selected_scenario = "mechanical"
            elif roll < 0.97:
                selected_scenario = "sabotage"
            else:
                selected_scenario = "sensor_failure"
        
        self.last_scenario = selected_scenario
        scenario_data = self.SCENARIOS[selected_scenario]
        
        sensors = self._get_zone_sensors(zone_id)
        readings = []
        anomalies = []
        
        # Generate readings for each sensor
        for sensor_id, sensor_type in sensors:
            reading, anomaly = self._generate_sensor_reading(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                zone_id=zone_id,
                scenario_data=scenario_data,
                timestamp=timestamp
            )
            readings.append(reading)
            if anomaly:
                anomalies.append(anomaly)
        
        # Check for coordinated anomalies
        if selected_scenario == "sabotage" and len(anomalies) >= 2:
            # Multiple sensors showing anomalies = coordinated
            for anomaly in anomalies:
                if anomaly.anomaly_type == AnomalyType.SUDDEN_CHANGE:
                    anomaly.anomaly_type = AnomalyType.COORDINATED_ANOMALY
        
        return readings, anomalies
    
    def _generate_sensor_reading(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        zone_id: str,
        scenario_data: dict,
        timestamp: datetime
    ) -> Tuple[SensorReading, Optional[SensorAnomaly]]:
        """
        Generate a single sensor reading, potentially with anomaly.
        """
        baseline = self.BASELINES[sensor_type]
        
        # Check if this sensor type should have an anomaly
        should_generate_anomaly = False
        anomaly_pattern = None
        
        if random.random() < scenario_data["anomaly_probability"]:
            for pattern in scenario_data["patterns"]:
                if sensor_type in pattern["sensor_types"]:
                    if random.random() < 0.7:  # 70% chance for applicable sensors
                        should_generate_anomaly = True
                        anomaly_pattern = pattern
                        break
        
        # Generate value
        if should_generate_anomaly and anomaly_pattern:
            # Generate anomalous value
            if anomaly_pattern["anomaly_type"] == AnomalyType.SENSOR_FAILURE:
                value = 0.0  # Sensor failure = zero/stuck reading
            else:
                # Deviate from normal
                deviation_mult = random.uniform(*anomaly_pattern["deviation_range"])
                deviation = baseline["normal_std"] * deviation_mult
                sign = random.choice([-1, 1])
                value = baseline["normal_mean"] + (sign * deviation)
        else:
            # Generate normal value with slight noise
            value = random.gauss(baseline["normal_mean"], baseline["normal_std"])
        
        # Ensure non-negative for vibration
        if sensor_type == SensorType.VIBRATION:
            value = max(0, value)
        
        # Determine if sensor is operational
        is_operational = True
        if anomaly_pattern and anomaly_pattern["anomaly_type"] == AnomalyType.SENSOR_FAILURE:
            is_operational = random.random() > 0.3  # 30% chance sensor reports failure
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            zone_id=zone_id,
            value=round(value, 3),
            unit=baseline["unit"],
            timestamp=timestamp,
            is_operational=is_operational,
            battery_level=random.uniform(50, 100) if is_operational else random.uniform(5, 30)
        )
        
        # Create anomaly if applicable
        anomaly = None
        if should_generate_anomaly and anomaly_pattern:
            # SAFETY: Guard against division by zero
            normal_std = baseline["normal_std"]
            normal_mean = baseline["normal_mean"]
            
            # Z-score calculation with zero guard
            if normal_std > 0:
                z_score = abs(value - normal_mean) / normal_std
            else:
                z_score = 0.0  # Cannot calculate z-score without std
            
            # Deviation percent with zero guard
            if abs(normal_mean) > 0.001:  # Avoid near-zero division
                deviation_percent = abs(value - normal_mean) / abs(normal_mean) * 100
            else:
                deviation_percent = 0.0  # Cannot calculate deviation from zero
            
            # Clamp isolation score
            isolation_score = min(z_score / 5.0, 1.0) if z_score >= 0 else 0.0
            
            anomaly = SensorAnomaly(
                anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                anomaly_type=anomaly_pattern["anomaly_type"],
                severity=anomaly_pattern["severity"],
                value_observed=round(value, 3),
                value_expected=round(normal_mean, 3),
                deviation_percent=round(max(deviation_percent, 0.0), 2),
                z_score=round(max(z_score, 0.0), 2),
                isolation_score=isolation_score,
                duration_seconds=random.uniform(1, 60) if anomaly_pattern["anomaly_type"] != AnomalyType.SUDDEN_CHANGE else random.uniform(0.1, 2),
                is_recurring=random.random() < 0.2  # 20% chance it's recurring
            )
        
        return reading, anomaly
    
    def calculate_likelihood_scores(
        self,
        anomalies: List[SensorAnomaly]
    ) -> Dict[str, float]:
        """
        Calculate likelihood scores for different anomaly causes.
        
        Returns probabilities for:
        - Environmental cause
        - Mechanical wear cause
        - Sabotage/intentional cause
        """
        if not anomalies:
            return {
                "environmental": 0.0,
                "mechanical": 0.0,
                "sabotage": 0.0,
            }
        
        # Count anomaly types
        type_counts = {}
        severity_sum = 0
        for anomaly in anomalies:
            type_counts[anomaly.anomaly_type] = type_counts.get(anomaly.anomaly_type, 0) + 1
            if anomaly.severity == AnomalySeverity.MINOR:
                severity_sum += 1
            elif anomaly.severity == AnomalySeverity.MODERATE:
                severity_sum += 2
            elif anomaly.severity == AnomalySeverity.SEVERE:
                severity_sum += 3
        
        # Calculate base likelihoods
        env_score = 0.0
        mech_score = 0.0
        sab_score = 0.0
        
        if AnomalyType.ENVIRONMENTAL_NOISE in type_counts:
            env_score += 0.6
        if AnomalyType.MECHANICAL_WEAR in type_counts:
            mech_score += 0.6
        if AnomalyType.SUDDEN_CHANGE in type_counts:
            sab_score += 0.5
        if AnomalyType.COORDINATED_ANOMALY in type_counts:
            sab_score += 0.7  # Strong indicator of tampering
        
        # Adjust based on severity
        if severity_sum > 4:
            sab_score *= 1.3
        
        # Adjust based on count
        if len(anomalies) > 3:
            sab_score *= 1.2
        
        # Normalize to sum to approximately 1
        total = env_score + mech_score + sab_score + 0.01
        
        return {
            "environmental": min(round(env_score / total, 3) if total > 0 else 0, 1.0),
            "mechanical": min(round(mech_score / total, 3) if total > 0 else 0, 1.0),
            "sabotage": min(round(sab_score / total, 3) if total > 0 else 0, 1.0),
        }
    
    def get_available_scenarios(self) -> List[str]:
        """Return list of available simulation scenarios."""
        return list(self.SCENARIOS.keys())


# Singleton instance
sensor_generator = SensorGenerator()
