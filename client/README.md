# RAKSHAK-AI Client

React dashboard for the RAKSHAK-AI Railway Track Tampering Detection System.

## ⚠️ Important Notice

**This is a DEMO INTERFACE.** All data displayed is simulated for demonstration purposes. The UI connects to the RAKSHAK-AI server for AI-powered analysis.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (ensure server is running on port 8000)
npm run dev
```

## Features

- **Risk Meter**: Real-time risk score visualization
- **Track Map**: Interactive track zone monitoring
- **Alert Timeline**: Historical and active alerts
- **Evidence Panel**: CCTV and sensor data preview
- **Simulation Controls**: Demo scenario triggers

## Architecture

```
src/
├── components/
│   ├── common/         # Shared components
│   ├── Dashboard/      # Main dashboard
│   ├── Map/            # Track visualization
│   └── Alerts/         # Alert management
├── services/           # API integration
├── hooks/              # Custom React hooks
└── utils/              # Constants & helpers
```

## Usage

1. Start the backend server first: `cd ../server && uvicorn app.main:app --reload`
2. Start the client: `npm run dev`
3. Open `http://localhost:5173`
4. Use simulation controls to test different scenarios

## Design Decisions

- **Dark Mode**: Optimized for control room environments
- **Color Coding**: Safety-critical RED/AMBER/GREEN indicators
- **Clear Labels**: No AI jargon, designed for railway staff
- **Simulated Badges**: Every data point marked as simulated
