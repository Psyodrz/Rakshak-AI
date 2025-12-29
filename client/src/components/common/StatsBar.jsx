/**
 * Modern Stats Bar Component
 * ==========================
 * 
 * DESIGN: Horizontal stats bar with animated counters
 * - Glassmorphism cards
 * - Framer Motion number transitions
 * - Subtle hover effects
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './StatsBar.css';
import { Scan, AlertTriangle, MapPin, Zap, Activity } from 'lucide-react';

// Animated counter hook
function useAnimatedValue(value, duration = 800) {
  const [displayValue, setDisplayValue] = useState(0);
  
  useEffect(() => {
    let startTime;
    let animationFrame;
    const startValue = displayValue;
    const endValue = value;
    
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Ease out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(startValue + (endValue - startValue) * easeProgress);
      
      setDisplayValue(current);
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);
  
  return displayValue;
}

// Stat card component
function StatCard({ icon, label, value, suffix = '', trend, delay = 0 }) {
  const animatedValue = useAnimatedValue(value);
  
  return (
    <motion.div 
      className="stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-value">
          <motion.span
            key={value}
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {animatedValue.toLocaleString()}{suffix}
          </motion.span>
        </div>
        <div className="stat-label">{label}</div>
      </div>
      {trend && (
        <div className={`stat-trend ${trend > 0 ? 'up' : 'down'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </div>
      )}
    </motion.div>
  );
}

// Connection indicator
function ConnectionIndicator({ isConnected }) {
  return (
    <motion.div 
      className={`connection-indicator ${isConnected ? 'connected' : ''}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.5 }}
    >
      <div className="indicator-wrapper">
        <motion.div 
          className="connection-pulse"
          animate={isConnected ? {
            scale: [1, 1.5, 1],
            opacity: [0.8, 0, 0.8]
          } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <div className="connection-dot" />
      </div>
      <span className="connection-text">
        {isConnected ? 'System Active' : 'Disconnected'}
      </span>
    </motion.div>
  );
}

export function StatsBar({ 
  totalScans = 0,
  alertsToday = 0,
  zonesMonitored = 5,
  avgResponseTime = 0,
  systemUptime = 99.9,
  isConnected = true
}) {
  return (
    <div className="stats-bar">
      <div className="stats-grid">
        <StatCard
          icon={<Scan className="w-5 h-5 text-blue-400" />}
          label="Total Scans"
          value={totalScans}
          delay={0}
        />
        <StatCard
          icon={<AlertTriangle className="w-5 h-5 text-orange-400" />}
          label="Alerts Today"
          value={alertsToday}
          delay={0.1}
        />
        <StatCard
          icon={<MapPin className="w-5 h-5 text-pink-500" />}
          label="Zones Active"
          value={zonesMonitored}
          delay={0.2}
        />
        <StatCard
          icon={<Zap className="w-5 h-5 text-yellow-400" />}
          label="Avg Response"
          value={Math.round(avgResponseTime)}
          suffix="ms"
          delay={0.3}
        />
        <StatCard
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
          label="Uptime"
          value={systemUptime}
          suffix="%"
          delay={0.4}
        />
      </div>
      
      <ConnectionIndicator isConnected={isConnected} />
    </div>
  );
}

export default StatsBar;
