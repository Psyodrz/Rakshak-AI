"""
Image Generator - Simulated CCTV and Drone Imagery
---------------------------------------------------
Generates simulated detection results as if from real CCTV/drone feeds.

In production, this would be replaced with:
- RTSP stream processing
- YOLO/Faster R-CNN inference
- Edge device integration

For hackathon demo, we simulate realistic detection patterns.
"""

import random
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from ..models.vision import (
    DetectionClass,
    ImageSource,
    ImageCondition,
    BoundingBox,
    Detection,
)
from ..config import config


class ImageGenerator:
    """
    Simulated image analysis generator.
    
    Produces detection results that mimic real vision AI output.
    Scenarios can be controlled for demo purposes.
    """
    
    # Detection scenarios with probabilities and typical detections
    SCENARIOS = {
        "normal": {
            "description": "Normal track conditions, no anomalies",
            "detections": [],
            "conditions": [ImageCondition.NORMAL],
        },
        "suspicious": {
            "description": "Some anomalies detected, needs investigation",
            "detections": [
                (DetectionClass.HUMAN_PRESENCE, 0.65, 0.85),
                (DetectionClass.FOREIGN_OBJECT, 0.55, 0.75),
            ],
            "conditions": [ImageCondition.NORMAL, ImageCondition.LOW_LIGHT],
        },
        "tampering": {
            "description": "Strong evidence of intentional tampering",
            "detections": [
                (DetectionClass.MISSING_FISH_PLATE, 0.75, 0.95),
                (DetectionClass.TRACK_DISPLACEMENT, 0.70, 0.90),
                (DetectionClass.HUMAN_PRESENCE, 0.60, 0.85),
                (DetectionClass.TOOL_DETECTION, 0.55, 0.80),
            ],
            "conditions": [ImageCondition.LOW_LIGHT],
        },
        "environmental": {
            "description": "Environmental debris, not intentional",
            "detections": [
                (DetectionClass.FOREIGN_OBJECT, 0.70, 0.90),
            ],
            "conditions": [ImageCondition.RAIN, ImageCondition.NORMAL],
        },
        "low_visibility": {
            "description": "Poor image quality affecting detection",
            "detections": [
                (DetectionClass.FOREIGN_OBJECT, 0.40, 0.60),
            ],
            "conditions": [ImageCondition.FOG, ImageCondition.BLUR],
        },
    }
    
    def __init__(self):
        """Initialize the image generator."""
        self.last_scenario = None
    
    def generate_detections(
        self,
        zone_id: str,
        source: ImageSource,
        scenario: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Tuple[List[Detection], List[ImageCondition]]:
        """
        Generate simulated detections for a zone.
        
        Args:
            zone_id: Track zone identifier
            source: Image source (CCTV, drone, mobile)
            scenario: Specific scenario to simulate (or random if None)
            timestamp: Time of analysis (affects conditions)
            
        Returns:
            Tuple of (list of detections, list of image conditions)
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Determine scenario
        if scenario and scenario in self.SCENARIOS:
            selected_scenario = scenario
        else:
            # Random scenario based on probabilities
            # In real life, most readings are normal
            roll = random.random()
            if roll < 0.6:
                selected_scenario = "normal"
            elif roll < 0.75:
                selected_scenario = "environmental"
            elif roll < 0.85:
                selected_scenario = "suspicious"
            elif roll < 0.95:
                selected_scenario = "low_visibility"
            else:
                selected_scenario = "tampering"
        
        self.last_scenario = selected_scenario
        scenario_data = self.SCENARIOS[selected_scenario]
        
        # Determine image conditions
        conditions = self._determine_conditions(timestamp, scenario_data)
        
        # Generate detections
        detections = []
        for detection_class, min_conf, max_conf in scenario_data["detections"]:
            # Random chance to include each detection
            if random.random() < 0.8:  # 80% chance for each
                detection = self._create_detection(
                    detection_class, 
                    min_conf, 
                    max_conf,
                    conditions
                )
                detections.append(detection)
        
        return detections, conditions
    
    def _determine_conditions(
        self, 
        timestamp: datetime, 
        scenario_data: dict
    ) -> List[ImageCondition]:
        """
        Determine image conditions based on time and scenario.
        
        Night hours (22:00-05:00) typically have low light.
        """
        conditions = []
        hour = timestamp.hour
        
        # Time-based conditions
        if hour >= 22 or hour < 5:
            if ImageCondition.LOW_LIGHT not in scenario_data["conditions"]:
                conditions.append(ImageCondition.LOW_LIGHT)
        
        # Add scenario-specific conditions
        for condition in scenario_data["conditions"]:
            if condition not in conditions:
                # Random chance to add each condition
                if condition == ImageCondition.NORMAL or random.random() < 0.7:
                    conditions.append(condition)
        
        # Ensure at least one condition
        if not conditions:
            conditions.append(ImageCondition.NORMAL)
            
        return conditions
    
    def _create_detection(
        self,
        detection_class: DetectionClass,
        min_confidence: float,
        max_confidence: float,
        conditions: List[ImageCondition]
    ) -> Detection:
        """
        Create a single detection with realistic values.
        
        Confidence is reduced if image quality is poor.
        """
        # Generate raw confidence
        raw_confidence = random.uniform(min_confidence, max_confidence)
        
        # Apply condition penalties
        adjusted_confidence = raw_confidence
        condition_penalty = False
        
        for condition in conditions:
            if condition == ImageCondition.LOW_LIGHT:
                adjusted_confidence *= config.LOW_LIGHT_CONFIDENCE_PENALTY
                condition_penalty = True
            elif condition == ImageCondition.BLUR:
                adjusted_confidence *= 0.6
                condition_penalty = True
            elif condition == ImageCondition.FOG:
                adjusted_confidence *= 0.7
                condition_penalty = True
            elif condition == ImageCondition.PARTIAL_OCCLUSION:
                adjusted_confidence *= 0.8
                condition_penalty = True
        
        # Generate bounding box (random but sensible location)
        bbox = self._generate_bounding_box(detection_class)
        
        return Detection(
            detection_id=f"det_{uuid.uuid4().hex[:8]}",
            class_label=detection_class,
            confidence=min(adjusted_confidence, 1.0),
            bounding_box=bbox,
            raw_confidence=raw_confidence,
            condition_penalty_applied=condition_penalty
        )
    
    def _generate_bounding_box(self, detection_class: DetectionClass) -> BoundingBox:
        """
        Generate a realistic bounding box based on detection class.
        
        Different objects have typical sizes and locations:
        - Track components are usually in lower half of image
        - Humans can be anywhere but typically near tracks
        - Foreign objects vary in size
        """
        if detection_class in [DetectionClass.MISSING_FISH_PLATE, DetectionClass.TRACK_DISPLACEMENT]:
            # Track components - bottom half, relatively small
            x = random.uniform(0.1, 0.7)
            y = random.uniform(0.5, 0.8)
            w = random.uniform(0.05, 0.15)
            h = random.uniform(0.05, 0.1)
        elif detection_class == DetectionClass.HUMAN_PRESENCE:
            # Human - taller than wide, can be various positions
            x = random.uniform(0.1, 0.7)
            y = random.uniform(0.2, 0.6)
            w = random.uniform(0.08, 0.15)
            h = random.uniform(0.2, 0.4)
        elif detection_class == DetectionClass.VEHICLE_NEAR_TRACK:
            # Vehicle - larger box
            x = random.uniform(0.0, 0.5)
            y = random.uniform(0.2, 0.5)
            w = random.uniform(0.2, 0.4)
            h = random.uniform(0.15, 0.3)
        else:
            # Foreign objects, tools - small to medium
            x = random.uniform(0.1, 0.7)
            y = random.uniform(0.4, 0.8)
            w = random.uniform(0.05, 0.2)
            h = random.uniform(0.05, 0.15)
        
        return BoundingBox(
            x_min=x,
            y_min=y,
            x_max=min(x + w, 1.0),
            y_max=min(y + h, 1.0)
        )
    
    def get_available_scenarios(self) -> List[str]:
        """Return list of available simulation scenarios."""
        return list(self.SCENARIOS.keys())


# Singleton instance
image_generator = ImageGenerator()
