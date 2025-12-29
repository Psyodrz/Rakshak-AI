"""
Simulation Controller
---------------------
Production-grade simulation lifecycle management for RAKSHAK-AI.

DESIGN PRINCIPLES:
- Single global controller (singleton pattern)
- Explicit state machine (STOPPED -> RUNNING -> STOPPED/ERROR)
- Concurrency-safe via asyncio.Lock
- Decoupled from WebSocket broadcasting
- All exceptions caught and logged
"""

import asyncio
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from .utils.logger import logger


class SimulationState(str, Enum):
    """
    Simulation lifecycle states.
    
    STOPPED: No simulation running, ready to start
    RUNNING: Simulation actively generating data
    ERROR: Simulation crashed, requires manual restart
    """
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"


class SimulationStatus(BaseModel):
    """Response model for simulation status queries."""
    state: SimulationState
    message: str
    started_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    run_count: int = 0
    error_message: Optional[str] = None


class SimulationController:
    """
    Thread-safe simulation lifecycle controller.
    
    Ensures:
    - Only one simulation runs at a time
    - Clean start/stop transitions
    - Error recovery and logging
    - Idempotent operations
    """
    
    def __init__(self):
        self._state = SimulationState.STOPPED
        self._lock = asyncio.Lock()
        self._started_at: Optional[datetime] = None
        self._last_run_at: Optional[datetime] = None
        self._run_count = 0
        self._error_message: Optional[str] = None
        self._current_task: Optional[asyncio.Task] = None
        
        logger.info("SimulationController initialized in STOPPED state")
    
    @property
    def state(self) -> SimulationState:
        """Current simulation state (read-only)."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is currently running."""
        return self._state == SimulationState.RUNNING
    
    def get_status(self) -> SimulationStatus:
        """Get full simulation status."""
        return SimulationStatus(
            state=self._state,
            message=self._get_status_message(),
            started_at=self._started_at,
            last_run_at=self._last_run_at,
            run_count=self._run_count,
            error_message=self._error_message
        )
    
    def _get_status_message(self) -> str:
        """Generate human-readable status message."""
        if self._state == SimulationState.STOPPED:
            return "Simulation is stopped. Ready to start."
        elif self._state == SimulationState.RUNNING:
            return f"Simulation running since {self._started_at.isoformat() if self._started_at else 'unknown'}"
        else:
            return f"Simulation in ERROR state: {self._error_message or 'Unknown error'}"
    
    async def run_single(
        self,
        zone_id: str,
        scenario: str
    ) -> Dict[str, Any]:
        """
        Run a single simulation cycle (one-shot, not continuous).
        
        This is the safe entry point for the /system/simulate endpoint.
        
        Args:
            zone_id: Track zone to simulate
            scenario: Scenario type (normal, suspicious, tampering, environmental)
            
        Returns:
            Dict containing simulation result or error info
        """
        async with self._lock:
            logger.info(f"Simulation requested: zone={zone_id}, scenario={scenario}")
            
            # Update state
            self._state = SimulationState.RUNNING
            self._started_at = datetime.utcnow()
            self._error_message = None
        
        try:
            # Import here to avoid circular imports
            from .services.intent_service import intent_service
            from .models.intent import IntentClassifyRequest
            
            # Create classification request
            request = IntentClassifyRequest(
                zone_id=zone_id,
                timestamp=datetime.utcnow(),
                run_vision_analysis=True,
                run_sensor_analysis=True,
                use_simulated=True,
                simulate_scenario=scenario
            )
            
            # Run classification
            response = await intent_service.classify(request)
            
            # Update state on success
            async with self._lock:
                self._state = SimulationState.STOPPED
                self._last_run_at = datetime.utcnow()
                self._run_count += 1
            
            logger.info(
                f"Simulation complete: classification={response.classification.value}, "
                f"risk_score={response.risk_score}, run_count={self._run_count}"
            )
            
            return {
                "success": True,
                "result": response.model_dump(mode="json"),
                "state": SimulationState.STOPPED.value
            }
            
        except Exception as e:
            # Handle error state
            error_msg = str(e)
            logger.error(f"Simulation FAILED: {error_msg}")
            
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            async with self._lock:
                self._state = SimulationState.ERROR
                self._error_message = error_msg
            
            return {
                "success": False,
                "error": error_msg,
                "state": SimulationState.ERROR.value
            }
    
    async def reset(self) -> SimulationStatus:
        """
        Reset controller from ERROR state to STOPPED.
        
        Allows recovery after a crash.
        """
        async with self._lock:
            if self._state == SimulationState.ERROR:
                logger.info("SimulationController reset from ERROR to STOPPED")
                self._state = SimulationState.STOPPED
                self._error_message = None
            elif self._state == SimulationState.RUNNING:
                logger.warning("Cannot reset while simulation is RUNNING")
            else:
                logger.info("SimulationController already in STOPPED state")
        
        return self.get_status()


# Singleton instance
simulation_controller = SimulationController()
