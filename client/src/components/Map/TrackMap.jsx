/**
 * Modern Track Map Component
 * ==========================
 * 
 * DESIGN: Clean SVG-based track visualization
 * - Smooth animated paths
 * - Subtle glow on active nodes
 * - Grid background with depth illusion
 * - Framer Motion for interactions
 */
import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './TrackMap.css';

// Zone configurations - positions match the SVG track path
// Track path: M 10 50 -> 28 42 -> 48 38 -> 68 45 -> 88 52
const TRACK_ZONES = [
  { id: 'ZONE-001', name: 'Mumbai Central', shortName: 'MMBC', x: 10, y: 50 },
  { id: 'ZONE-002', name: 'Dadar', shortName: 'DDR', x: 28, y: 42 },
  { id: 'ZONE-003', name: 'Kurla', shortName: 'KRL', x: 48, y: 38 },
  { id: 'ZONE-004', name: 'Thane', shortName: 'TNA', x: 68, y: 45 },
  { id: 'ZONE-005', name: 'Kalyan Jn', shortName: 'KYN', x: 88, y: 52 },
];

// Severity colors
const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
  SAFE: '#3b82f6'
};

// Zone node component
function ZoneNode({ zone, isSelected, severity, onClick }) {
  const color = severity ? SEVERITY_COLORS[severity] : SEVERITY_COLORS.SAFE;
  const isAlert = severity && severity !== 'LOW';
  
  return (
    <motion.div
      className={`zone-node ${isSelected ? 'selected' : ''} ${isAlert ? 'alert' : ''}`}
      style={{ 
        left: `${zone.x}%`, 
        top: `${zone.y}%`,
        '--node-color': color,
        x: '-50%',
        y: '-50%'
      }}
      onClick={() => onClick(zone.id)}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ 
        type: "spring", 
        stiffness: 300, 
        damping: 20,
        delay: zone.x / 100 * 0.3
      }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Glow effect */}
      {isAlert && (
        <motion.div 
          className="node-glow"
          animate={{ 
            scale: [1, 1.5, 1],
            opacity: [0.5, 0, 0.5]
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
          style={{ background: color }}
        />
      )}
      
      {/* Node core */}
      <div className="node-core">
        <span className="node-icon">
          {isAlert ? (severity === 'CRITICAL' ? '⚠' : '!') : '●'}
        </span>
      </div>
      
      {/* Label */}
      <div className="node-label">
        <span className="node-name">{zone.shortName}</span>
      </div>
      
      {/* Tooltip */}
      <div className="node-tooltip">
        <div className="tooltip-header">{zone.name}</div>
        <div className="tooltip-id">{zone.id}</div>
        <div className="tooltip-status" style={{ color }}>
          {severity ? `${severity} Alert` : 'Normal Status'}
        </div>
      </div>
    </motion.div>
  );
}

export function TrackMap({ 
  selectedZone, 
  onZoneSelect, 
  affectedZones = [],
  alerts = []
}) {
  // Get severity for a zone
  const getZoneSeverity = (zoneId) => {
    const zoneAlerts = alerts.filter(a => a.zone_id === zoneId && a.status === 'active');
    if (zoneAlerts.length === 0) return null;
    
    if (zoneAlerts.some(a => a.severity === 'CRITICAL')) return 'CRITICAL';
    if (zoneAlerts.some(a => a.severity === 'HIGH')) return 'HIGH';
    if (zoneAlerts.some(a => a.severity === 'MEDIUM')) return 'MEDIUM';
    return 'LOW';
  };
  
  // Generate track path
  const trackPath = useMemo(() => {
    const points = TRACK_ZONES.map(z => `${z.x} ${z.y}`);
    return `M ${points[0]} Q ${points[1]} ${points[2]} T ${points[3]} ${points[4]}`;
  }, []);

  return (
    <motion.div 
      className="card track-map-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <div className="card-header">
        <h3 className="card-title">
          <span className="icon">🗺️</span>
          Track Monitor
        </h3>
        <div className="map-controls">
          <span className="zones-count">{TRACK_ZONES.length} zones</span>
        </div>
      </div>
      
      <div className="map-container">
        {/* Grid background */}
        <div className="map-grid" />
        
        {/* Gradient overlay for depth */}
        <div className="map-depth-overlay" />
        
        {/* Track SVG */}
        <svg className="track-svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="trackLine" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.3" />
            </linearGradient>
            <filter id="trackGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="1" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          
          {/* Track path background */}
          <motion.path
            d={`M 10 50 Q 20 44 28 42 Q 38 38 48 38 Q 58 40 68 45 Q 78 50 88 52`}
            fill="none"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth="4"
            strokeLinecap="round"
          />
          
          {/* Animated track path */}
          <motion.path
            d={`M 10 50 Q 20 44 28 42 Q 38 38 48 38 Q 58 40 68 45 Q 78 50 88 52`}
            fill="none"
            stroke="url(#trackLine)"
            strokeWidth="2"
            strokeLinecap="round"
            filter="url(#trackGlow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
          
          {/* Track ties */}
          {[...Array(15)].map((_, i) => {
            const t = (i + 1) / 16;
            const x = 10 + t * 78;
            const y = 50 - Math.sin(t * Math.PI) * 8 - 4;
            return (
              <motion.line
                key={i}
                x1={x}
                y1={y - 2}
                x2={x}
                y2={y + 6}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="0.5"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 + i * 0.05 }}
              />
            );
          })}
        </svg>
        
        {/* Zone nodes wrapper - matches SVG positioning */}
        <div className="zones-wrapper">
          {TRACK_ZONES.map((zone) => (
            <ZoneNode
              key={zone.id}
              zone={zone}
              isSelected={selectedZone === zone.id}
              severity={getZoneSeverity(zone.id) || (affectedZones.includes(zone.id) ? 'HIGH' : null)}
              onClick={onZoneSelect}
            />
          ))}
        </div>
        
        {/* Legend */}
        <div className="map-legend">
          <div className="legend-item">
            <span className="legend-dot" style={{ background: SEVERITY_COLORS.SAFE }} />
            <span>Normal</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: SEVERITY_COLORS.MEDIUM }} />
            <span>Alert</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: SEVERITY_COLORS.CRITICAL }} />
            <span>Critical</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default TrackMap;
