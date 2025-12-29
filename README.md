# RAKSHAK-AI

**AI System to Detect Intentional Railway Track Tampering**

> **CLASSIFICATION**: INTERNAL USE ONLY  
> **VERSION**: 1.0.0 (Production Candidate)

---

## 1. Executive Summary

RAKSHAK-AI is a mission-critical safety system designed to detect, classify, and alert on intentional sabotage attempts against railway infrastructure. Unlike traditional maintenance systems that look for wear-and-tear, RAKSHAK-AI correlates multi-modal data (Computer Vision, IoT Sensors, and Temporal Context) to identify **malicious intent**.

**Key Capabilities:**

- **Real-time Anomaly Detection**: Sub-second analysis of sensor and vision feeds.
- **Intent Classification**: Distinguishes between environmental noise, mechanical failure, and deliberate tampering.
- **Zero-Trust Architecture**: Operates fully locally (Edge/On-Premise) with no cloud dependencies.

---

## 2. System Architecture

The system follows a strict modular architecture designed for government integration.

### 2.1 Backend (`/server`)

Built on **FastAPI** (Python), utilizing a Hexagonal Architecture (Ports & Adapters).

- **Adapters Layer**: Abstracts hardware specifics. Current implementation uses high-fidelity physics-based simulators. Ready for PLCs/SCADA integration.
- **Ingestion Pipeline**: Async processing of high-frequency sensor data.
- **Core Intelligence (`IntentService`)**: The decision engine. Uses weighted risk scoring to fuse multi-modal data.
- **Real-time Bus**: WebSockets for immediate command-center dissemination.

### 2.2 Frontend (`/client`)

Built on **React/Vite**, designed as a "Glass Cockpit" for railway operators.

- **High-Contrast Interface**: Optimized for 24/7 control room environments.
- **Live Monitoring**: 0-latency map and graph updates via WebSockets.
- **Chain of Custody**: Immutable audit logs visible in the UI.

---

## 3. Data Sources & Simulation

> [!NOTE] > **simulation_mode = true**

To demonstrate capability without compromising active critical infrastructure, this instance runs in **High-Fidelity Simulation Mode**.

| Data Type         | Real World Source                   | Simulation Implementation                                                                         |
| ----------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Vision**        | Track-side CCTV, Drone Feeds (RTSP) | Generative probabilistic models implementing YOLO detection patterns (fog, low-light, occlusion). |
| **Vibration**     | Piezoelectric Accelerometers        | Statistical noise models with sudden-impulse injection for "hammer/crowbar" signatures.           |
| **Tilt/Pressure** | Gyroscopic/Strain Gauges            | Physics-based drift models.                                                                       |

**Integration Path for Live Data:**

1. Implement `VisionSource` interface in `app/adapters/real_vision.py`.
2. Connect RTSP stream to `cv2` ingestion.
3. Update `config.py` to switch `DATA_SOURCE = "REAL"`.
   **NO CORE LOGIC CHANGE REQUIRED.**

---

## 4. Security & Compliance

- **Audit Trail**: Every classification decision includes a unique `classification_id` and explainable `risk_factors`.
- **Air-Gapped Ready**: No external API calls. No telemetry.
- **Role-Based Access**: Structure supports detailed granular permissions (currently running in Admin mode for demo).

---

## 5. Operations Guide

### 5.1 Prerequisites

- Node.js v18+
- Python 3.9+
- Modern Web Browser (Chrome/Firefox/Edge)

### 5.2 Start System

**Control Center (Client)**

```bash
cd client
npm install
npm run dev
```

**Intelligence Core (Server)**

```bash
cd server
pip install -r requirements.txt
npm start  # Wrapper for uvicorn
```

---

_Designed and Engineered for Public Safety._
