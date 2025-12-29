/**
 * Modern Risk Meter Component
 * ===========================
 * 
 * DESIGN: Radial gauge with smooth animated transitions
 * - Color interpolation based on risk level
 * - Glowing effect on status change
 * - Framer Motion for smooth value changes
 */
import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './RiskMeter.css';

// Status configurations
const STATUS_CONFIG = {
  SAFE: {
    color: '#10b981',
    gradient: ['#10b981', '#059669'],
    glow: 'rgba(16, 185, 129, 0.4)',
    label: 'SAFE',
    icon: '✓'
  },
  SUSPICIOUS: {
    color: '#f59e0b',
    gradient: ['#f59e0b', '#d97706'],
    glow: 'rgba(245, 158, 11, 0.4)',
    label: 'SUSPICIOUS',
    icon: '⚠'
  },
  CONFIRMED_TAMPERING: {
    color: '#ef4444',
    gradient: ['#ef4444', '#dc2626'],
    glow: 'rgba(239, 68, 68, 0.5)',
    label: 'CRITICAL',
    icon: '!'
  }
};

export function RiskMeter({ 
  riskScore = 0, 
  classification = 'SAFE', 
  confidence = 1 
}) {
  const config = STATUS_CONFIG[classification] || STATUS_CONFIG.SAFE;
  
  // Calculate gauge progress (0-100 -> 0-270 degrees)
  const gaugeAngle = useMemo(() => {
    return Math.min(Math.max(riskScore, 0), 100) * 2.7; // 270 degree arc
  }, [riskScore]);
  
  // SVG arc path calculation
  const createArcPath = (radius, startAngle, endAngle) => {
    const start = polarToCartesian(60, 60, radius, endAngle);
    const end = polarToCartesian(60, 60, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    
    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
  };
  
  const polarToCartesian = (cx, cy, r, angle) => {
    const rad = (angle - 135) * Math.PI / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad)
    };
  };

  return (
    <div className="risk-meter-container">
      {/* Ambient glow behind meter */}
      <motion.div 
        className="risk-meter-glow"
        animate={{ 
          boxShadow: `0 0 80px 20px ${config.glow}`,
          opacity: classification === 'CONFIRMED_TAMPERING' ? [0.5, 0.8, 0.5] : 0.6
        }}
        transition={{ 
          duration: classification === 'CONFIRMED_TAMPERING' ? 1 : 0.5,
          repeat: classification === 'CONFIRMED_TAMPERING' ? Infinity : 0
        }}
      />
      
      {/* Main gauge */}
      <div className="risk-meter-gauge">
        <svg viewBox="0 0 120 120" className="gauge-svg">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={config.gradient[0]} />
              <stop offset="100%" stopColor={config.gradient[1]} />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Background track */}
          <path
            d={createArcPath(50, 0, 270)}
            fill="none"
            className="gauge-track"
            strokeWidth="8"
            strokeLinecap="round"
          />
          
          {/* Animated progress arc */}
          <motion.path
            d={createArcPath(50, 0, 270)}
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            filter="url(#glow)"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: gaugeAngle / 270 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
          
          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = tick * 2.7;
            const point = polarToCartesian(60, 60, 42, angle);
            return (
              <circle
                key={tick}
                cx={point.x}
                cy={point.y}
                r="2"
                className="gauge-tick"
              />
            );
          })}
        </svg>
        
        {/* Center content */}
        <div className="gauge-center">
          <motion.div 
            className="risk-value"
            key={riskScore}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            style={{ color: config.color }}
          >
            {Math.round(riskScore)}
          </motion.div>
          <div className="risk-label">RISK SCORE</div>
        </div>
      </div>
      
      {/* Status badge */}
      <AnimatePresence mode="wait">
        <motion.div 
          key={classification}
          className="risk-status"
          initial={{ scale: 0.8, opacity: 0, y: 10 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.8, opacity: 0, y: -10 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          style={{ 
            background: `linear-gradient(135deg, ${config.gradient[0]}, ${config.gradient[1]})`,
            boxShadow: `0 4px 20px ${config.glow}`
          }}
        >
          <span className="status-icon">{config.icon}</span>
          <span className="status-label">{config.label}</span>
        </motion.div>
      </AnimatePresence>
      
      {/* Confidence indicator */}
      <div className="confidence-bar">
        <span className="confidence-label">Confidence</span>
        <div className="confidence-track">
          <motion.div 
            className="confidence-fill"
            initial={{ width: 0 }}
            animate={{ width: `${confidence * 100}%` }}
            transition={{ duration: 0.5 }}
            style={{ background: config.color }}
          />
        </div>
        <span className="confidence-value">{Math.round(confidence * 100)}%</span>
      </div>
    </div>
  );
}

export default RiskMeter;
