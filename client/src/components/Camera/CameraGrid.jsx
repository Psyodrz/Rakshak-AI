/**
 * Camera Feed Grid Component
 * 4-panel simulated camera view with detection overlays
 */
import React, { useState } from 'react';
import SimulatedBadge from '../common/SimulatedBadge';
import CameraFeed from './CameraFeed';
import './CameraGrid.css';

// Video sources - using absolute paths from public
const VIDEO_SOURCES = {
  ENTRY: '/cctv/cam_station_entry.mp4',
  PLATFORM: '/cctv/cam_platform.mp4',
};

const CAMERA_FEEDS = [
  { 
    id: 'CAM-001', 
    name: 'Entry Gate Main', 
    zone: 'ZONE-001',
    videoSrc: VIDEO_SOURCES.ENTRY,
    offset: 0,
    filterStyle: { filter: 'contrast(1.1)' }
  },
  { 
    id: 'CAM-002', 
    name: 'Platform 1 North', 
    zone: 'ZONE-002',
    videoSrc: VIDEO_SOURCES.PLATFORM,
    offset: 5, // 5 seconds offset
    filterStyle: { filter: 'sepia(0.2) brightness(0.95)' }
  },
  { 
    id: 'CAM-003', 
    name: 'Entry Gate Side', 
    zone: 'ZONE-001',
    videoSrc: VIDEO_SOURCES.ENTRY,
    offset: 12, // 12 seconds offset to look different
    filterStyle: { filter: 'hue-rotate(5deg) contrast(0.9)' }
  },
  { 
    id: 'CAM-004', 
    name: 'Platform 1 South', 
    zone: 'ZONE-002',
    videoSrc: VIDEO_SOURCES.PLATFORM,
    offset: 8, // 8 seconds offset
    filterStyle: { filter: 'grayscale(0.1) brightness(1.05)' }
  },
];

const VIEW_MODES = {
  NORMAL: { name: 'Normal', filter: 'none', overlay: 'rgba(0,0,0,0)' },
  NIGHT: { name: 'Night Vision', filter: 'brightness(1.5) contrast(1.2) saturate(0) sepia(1) hue-rotate(70deg)', overlay: 'rgba(0,255,0,0.05)' },
  THERMAL: { name: 'Thermal', filter: 'brightness(1.2) contrast(1.3) saturate(0.5) hue-rotate(180deg)', overlay: 'rgba(255,100,0,0.1)' },
};

export function CameraGrid({ latestClassification }) {
  const [viewMode, setViewMode] = useState('NORMAL');
  const [selectedCamera, setSelectedCamera] = useState(null);
  
  // Generate simulated detections based on classification
  const getDetections = (cameraId) => {
    if (!latestClassification || latestClassification.classification === 'SAFE') {
      return [];
    }
    
    // Logic to distribute simulated detections to specific cameras
    // For demo purposes, we'll assign 'TAMPERING' to CAM-001 and 'SUSPICIOUS' to CAM-002
    
    if (cameraId === 'CAM-001' && latestClassification.classification === 'CONFIRMED_TAMPERING') {
      return [
        { x: 30, y: 60, w: 15, h: 20, label: 'Person', type: 'danger' },
      ];
    }
    
    if (cameraId === 'CAM-002' && latestClassification.classification === 'SUSPICIOUS') {
      return [
        { x: 40, y: 55, w: 12, h: 18, label: 'Motion', type: 'warning' },
      ];
    }
    
    return [];
  };

  const currentViewModeStyle = VIEW_MODES[viewMode];
  
  return (
    <div className="card camera-grid-card">
      <div className="card-header">
        <h3 className="card-title">
          <span className="icon">📹</span>
          Live Camera Feeds
        </h3>
        <div className="camera-controls">
          <div className="view-mode-selector">
            {Object.keys(VIEW_MODES).map(mode => (
              <button
                key={mode}
                className={`mode-btn ${viewMode === mode ? 'active' : ''}`}
                onClick={() => setViewMode(mode)}
              >
                {VIEW_MODES[mode].name}
              </button>
            ))}
          </div>
          <SimulatedBadge />
        </div>
      </div>
      
      <div className="camera-grid">
        {CAMERA_FEEDS.map(camera => {
           // Merge individual camera filter with global view mode
           const mergedFilter = {
             filter: `${camera.filterStyle.filter || ''} ${currentViewModeStyle.filter !== 'none' ? currentViewModeStyle.filter : ''}`.trim()
           };
           
           return (
            <CameraFeed
              key={camera.id}
              {...camera}
              filterStyle={mergedFilter}
              detections={getDetections(camera.id)}
              isConnected={true}
            />
          );
        })}
      </div>
    </div>
  );
}

export default CameraGrid;
