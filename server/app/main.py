"""
RAKSHAK-AI Server
-----------------
AI System to Detect Intentional Railway Track Tampering

Main FastAPI application entry point.

This is a SAFETY-CRITICAL SIMULATION SYSTEM.
All hardware inputs are simulated, but AI/ML logic is real and production-grade.
"""

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from .config import config
from .routers import (
    vision_router,
    sensor_router,
    intent_router,
    alert_router,
    system_router,
)
from .utils.logger import logger
from .utils.exceptions import RakshakException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("=" * 60)
    logger.info("RAKSHAK-AI Server Starting")
    logger.info("=" * 60)
    logger.info(f"  Version: {config.API_VERSION}")
    logger.info(f"  Mode: SIMULATION (all data is simulated)")
    logger.info(f"  CORS Origins: {config.CORS_ORIGINS}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("RAKSHAK-AI Server Shutting Down")


# Create FastAPI application
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# Exception handlers
@app.exception_handler(RakshakException)
async def rakshak_exception_handler(request: Request, exc: RakshakException):
    """Handle custom RAKSHAK exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "details": {"type": type(exc).__name__}
        }
    )


# Include routers
app.include_router(vision_router)
app.include_router(sensor_router)
app.include_router(intent_router)
app.include_router(alert_router)
app.include_router(system_router)



# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    from starlette.websockets import WebSocketDisconnect
    from .websockets import manager
    
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client (heartbeat, commands, etc.)
            # This will also detect when the client disconnects
            try:
                data = await websocket.receive_text()
                # Handle any client messages here if needed
                logger.info(f"Received from client: {data}")
            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": config.API_TITLE,
        "version": config.API_VERSION,
        "description": "AI System to Detect Intentional Railway Track Tampering",
        "docs": "/docs",
        "health": "/system/health",
        "simulation_note": "⚠️ This system uses SIMULATED data for demonstration",
        "endpoints": {
            "vision": "/vision/analyze",
            "sensor": "/sensor/analyze",
            "intent": "/intent/classify",
            "alert": "/alert/status",
            "system": "/system/health",
            "simulate": "/system/simulate"
        }
    }


# API summary endpoint
@app.get("/api/summary", tags=["Root"])
async def api_summary():
    """Get a summary of all API capabilities."""
    return {
        "core_endpoints": [
            {
                "path": "/vision/analyze",
                "method": "POST",
                "description": "Analyze CCTV/drone imagery for tampering evidence"
            },
            {
                "path": "/sensor/analyze", 
                "method": "POST",
                "description": "Analyze sensor data for anomalies"
            },
            {
                "path": "/intent/classify",
                "method": "POST",
                "description": "Classify tampering intent (CORE INTELLIGENCE)"
            },
            {
                "path": "/alert/status",
                "method": "GET",
                "description": "Get current alert status"
            },
            {
                "path": "/system/health",
                "method": "GET",
                "description": "System health check"
            },
            {
                "path": "/system/simulate",
                "method": "POST",
                "description": "Trigger demo simulation"
            }
        ],
        "classification_outputs": ["SAFE", "SUSPICIOUS", "CONFIRMED_TAMPERING"],
        "severity_levels": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "simulation_scenarios": ["normal", "environmental", "suspicious", "tampering"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
