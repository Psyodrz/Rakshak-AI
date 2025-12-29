# RAKSHAK-AI Server

AI System to Detect Intentional Railway Track Tampering.

## ⚠️ Important Notice

**This is a SIMULATION SYSTEM.** All sensor and vision data is simulated for demonstration purposes. The AI/ML logic is real and production-grade.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Endpoint           | Method | Description                          |
| ------------------ | ------ | ------------------------------------ |
| `/vision/analyze`  | POST   | Analyze image for tampering evidence |
| `/sensor/analyze`  | POST   | Analyze sensor data for anomalies    |
| `/intent/classify` | POST   | **CORE** - Classify tampering intent |
| `/alert/status`    | GET    | Get current alert status             |
| `/system/health`   | GET    | System health check                  |
| `/system/simulate` | POST   | Trigger simulation scenario          |

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration & thresholds
├── models/              # Pydantic data models
├── services/            # Core AI services
│   ├── vision_service   # Image analysis
│   ├── sensor_service   # Anomaly detection
│   ├── intent_service   # Classification engine
│   ├── alert_service    # Alert management
│   └── audit_service    # Audit logging
├── simulation/          # Data generators
├── routers/             # API endpoints
└── utils/               # Utilities
```

## Classification Outputs

- **SAFE**: No threat detected
- **SUSPICIOUS**: Anomalies detected, recommend investigation
- **CONFIRMED_TAMPERING**: High confidence tampering, immediate action

## Testing Simulation

```bash
# Trigger a tampering simulation
curl -X POST http://localhost:8000/system/simulate \
  -H "Content-Type: application/json" \
  -d '{"zone_id": "ZONE-001", "scenario": "tampering"}'
```
