
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from datetime import datetime
from ..models.vision import Detection, ImageCondition, DetectionClass
from ..models.sensor import SensorReading, SensorAnomaly

class VisionSourceAdapter(ABC):
    """
    Abstract interface for Vision Data Sources.
    
    Implementations can be:
    - SimulatedVisionAdapter (Current)
    - RTSPVisionAdapter (Future: YOLO/OpenCV)
    - DroneFeedAdapter (Future: Drone SDK)
    """
    
    @abstractmethod
    async def get_detections(
        self, 
        zone_id: str, 
        source_id: str
    ) -> Tuple[List[Detection], List[ImageCondition]]:
        """Get detections from this source."""
        pass

class SensorSourceAdapter(ABC):
    """
    Abstract interface for Sensor Data Sources.
    
    Implementations can be:
    - SimulatedSensorAdapter (Current)
    - IoTSensorAdapter (Future: MQTT/PLC)
    """
    
    @abstractmethod
    async def get_readings(
        self, 
        zone_id: str
    ) -> List[SensorReading]:
        """Get raw sensor readings."""
        pass
    
    @abstractmethod
    async def detect_anomalies(
        self,
        readings: List[SensorReading]
    ) -> List[SensorAnomaly]:
        """
        Detect anomalies in readings.
        Note: In some hardware, this might be done on-edge.
        """
        pass
