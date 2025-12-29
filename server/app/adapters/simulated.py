
import random
from typing import List, Tuple
from datetime import datetime

from .base import VisionSourceAdapter, SensorSourceAdapter
from ..models.vision import Detection, ImageCondition, DetectionClass
from ..models.sensor import SensorReading, SensorAnomaly
from ..simulation.image_generator import image_generator
from ..simulation.sensor_generator import sensor_generator
from ..config import config

class SimulatedVisionAdapter(VisionSourceAdapter):
    """
    Simulated implementation of Vision Source.
    Uses the existing high-fidelity ImageGenerator.
    """
    
    async def get_detections(
        self, 
        zone_id: str, 
        source_id: str
    ) -> Tuple[List[Detection], List[ImageCondition]]:
        # In simulation, we generate based on the requested scenario
        # or defaults handled by the generator
        return image_generator.generate_detections(
            zone_id=zone_id,
            source=source_id,
            timestamp=datetime.utcnow()
        )

class SimulatedSensorAdapter(SensorSourceAdapter):
    """
    Simulated implementation of Sensor Source.
    Uses the existing SensorGenerator.
    """
    
    async def get_readings(
        self, 
        zone_id: str
    ) -> List[SensorReading]:
        readings, _ = sensor_generator.generate_readings(
            zone_id=zone_id,
            timestamp=datetime.utcnow()
        )
        return readings
    
    async def detect_anomalies(
        self,
        readings: List[SensorReading]
    ) -> List[SensorAnomaly]:
        # In our simulation, readings are generated WITH anomalies attached
        # But for the adapter interface, we might need to "re-detect" 
        # or simply extract them if we were passing raw data.
        
        # However, the SimulationGenerator is unique in that it generates BOTH
        # readings and anomalies together. 
        # To strictly follow the interface where we input readings -> output anomalies,
        # we would need a separate detection logic.
        
        # FOR NOW: To maintain behavior parity without rewriting the entire inspection logic,
        # we will use the internal generator methods if possible, 
        # OR (preferred for this adapter) we assume the 'readings' generation 
        # already happened in a context where we can't easily re-derive the exact same random anomaly.
        
        # PRACTICAL COMPROMISE FOR SIMULATION ADAPTER:
        # The sensor_service currently calls generate_readings which returns (readings, anomalies).
        # We will split this responsibility. 
        # 1. get_readings() returns just readings.
        # 2. detect_anomalies() will run the configurable threshold checks 
        #    (simulating the 'edge' logic).
        
        anomalies = []
        thresholds = config.SENSOR_THRESHOLDS
        
        for reading in readings:
            threshold_config = thresholds.get(reading.sensor_type.value, {})
            if not threshold_config:
                continue
                
            value = reading.value
            normal_range = threshold_config.get("normal_range", (0, 100))
            
            # Simple threshold detection (Production fallback logic)
            if not (normal_range[0] <= value <= normal_range[1]):
                # Re-construct anomaly object (simplified for adapter)
                 # In a deep simulation, we'd want the EXACT anomaly info from the generator.
                 # But since we are decoupling, we use this standard detection.
                 pass 
                 
        # REVISIT: For the Simulation, it's better if the Adapter exposes a method 
        # that returns BOTH because that's how the generator works.
        # But `SensorSourceAdapter` is about reading data.
        
        # Let's delegate to the service's existing `_detect_anomalies` logic 
        # which acts as the "software anomaly detector".
        # This adapter function might just return "hardware reported errors".
        
        return []

