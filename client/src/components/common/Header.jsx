/**
 * Modern Header Component
 * =======================
 * 
 * DESIGN: Glassmorphism with subtle blur
 * - Clean typography
 * - Status indicators with glow
 * - Keyboard accessible controls
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../../context/ThemeContext';
import { useNotifications } from '../../context/NotificationContext';
import { NavLink, Link } from 'react-router-dom';
import './Header.css';
import { Bell, BellOff, Sun, Moon, Shield, LayoutDashboard, Cctv, BarChart2, Settings } from 'lucide-react';

export function Header({ systemStatus = 'healthy', wsConnected = true }) {
  const { theme, toggleTheme } = useTheme();
  const { soundEnabled, setSoundEnabled } = useNotifications();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  
  // Status configuration
  const statusConfig = {
    healthy: { color: '#10b981', label: 'OPERATIONAL', icon: '●' },
    offline: { color: '#ef4444', label: 'OFFLINE', icon: '●' },
    degraded: { color: '#f59e0b', label: 'DEGRADED', icon: '●' }
  };
  
  const status = statusConfig[systemStatus] || statusConfig.healthy;
  
  return (
    <motion.header 
      className="header"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* Left: Logo & Brand */}
      {/* Left: Logo & Brand */}
      <Link to="/" className="header-brand">
        <div className="header-logo">
          <svg viewBox="0 0 40 40" className="logo-icon">
            <defs>
              <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#1d4ed8" />
              </linearGradient>
            </defs>
            <path 
              d="M20 2 L34 8 L34 20 C34 30 20 38 20 38 C20 38 6 30 6 20 L6 8 Z" 
              fill="url(#shieldGrad)"
            />
            <g fill="#fff" opacity="0.9">
              <rect x="12" y="14" width="16" height="2" rx="1" />
              <rect x="12" y="20" width="16" height="2" rx="1" />
              <rect x="14" y="12" width="2" height="12" rx="1" />
              <rect x="19" y="12" width="2" height="12" rx="1" />
              <rect x="24" y="12" width="2" height="12" rx="1" />
            </g>
          </svg>
        </div>
        <div className="header-title">
          <h1>RAKSHAK-AI</h1>
          <span className="header-subtitle">Railway Track Safety System</span>
        </div>
      </Link>
      
      {/* Center: Navigation - Desktop */}
      <nav className="header-nav hidden md:flex items-center gap-1">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard className="w-4 h-4" />
          <span>Overview</span>
        </NavLink>
        <NavLink to="/monitor" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Cctv className="w-4 h-4" />
          <span>Monitor</span>
        </NavLink>
        <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <BarChart2 className="w-4 h-4" />
          <span>Analytics</span>
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>
      </nav>
      
      {/* Live Badge (Mobile only or moved) */}
      <div className="header-center md:hidden">
        <span className="demo-badge">
          <span className="demo-dot" />
          LIVE
        </span>
      </div>
      
      {/* Right: Controls & Status */}
      <div className="header-controls">
        {/* Theme Toggle */}
        <motion.button
          className="header-btn"
          onClick={toggleTheme}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5" />}
        </motion.button>
        
        {/* Sound Toggle */}
        <motion.button
          className={`header-btn ${!soundEnabled ? 'muted' : ''}`}
          onClick={() => setSoundEnabled(!soundEnabled)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title={soundEnabled ? 'Mute alerts' : 'Enable alerts'}
          aria-label="Toggle sound"
        >
          {soundEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5 text-gray-400" />}
        </motion.button>
        
        {/* Divider */}
        <div className="header-divider" />
        
        {/* WebSocket Status */}
        <div className={`connection-status ${wsConnected ? 'connected' : ''}`}>
          <motion.span 
            className="connection-dot"
            animate={wsConnected ? { 
              scale: [1, 1.2, 1],
              opacity: [1, 0.8, 1]
            } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span className="connection-label">
            {wsConnected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
        
        {/* System Status */}
        <div className="system-status" style={{ '--status-color': status.color }}>
          <span className="status-indicator">{status.icon}</span>
          <span className="status-label">{status.label}</span>
        </div>
        
        {/* Time Display */}
        <div className="header-time">
          <span className="time-value">
            {currentTime.toLocaleTimeString('en-IN', { 
              hour: '2-digit', 
              minute: '2-digit',
              second: '2-digit',
              hour12: false 
            })}
          </span>
          <span className="time-zone">IST</span>
        </div>
      </div>
    </motion.header>
  );
}

export default Header;
