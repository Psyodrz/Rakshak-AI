/**
 * RAKSHAK-AI Client Application
 * Main application component
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import PageTransition from './components/common/PageTransition';
// import Sidebar from './components/common/Sidebar'; // Removed
import Header from './components/common/Header';
import DashboardPage from './pages/DashboardPage';
import LiveMonitorPage from './pages/LiveMonitorPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import Spinner from './components/common/Spinner';
import StatsBar from './components/common/StatsBar';
import { useNotifications } from './context/NotificationContext';
import { systemAPI, alertAPI, intentAPI } from './services/api';
import { POLL_INTERVAL } from './utils/constants';
import './App.css';

function App() {
  // State
  const [systemHealth, setSystemHealth] = useState(null);
  const [alertStatus, setAlertStatus] = useState(null);
  const [latestClassification, setLatestClassification] = useState(null);
  const [selectedZone, setSelectedZone] = useState('ZONE-001');
  const [selectedScenario, setSelectedScenario] = useState('suspicious');
  const [isSimulating, setIsSimulating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scanCount, setScanCount] = useState(0);
  const [isEmergencyMode, setIsEmergencyMode] = useState(false);
  
  // Available zones for rotation
  const ZONES = [
    { id: 'ZONE-001', name: 'Mumbai Central' },
    { id: 'ZONE-002', name: 'Dadar' },
    { id: 'ZONE-003', name: 'Kurla' },
    { id: 'ZONE-004', name: 'Thane' },
    { id: 'ZONE-005', name: 'Kalyan Jn' },
  ];
  
  const location = useLocation();
  
  // Notifications
  const { notify } = useNotifications();
  
  // Fetch initial data
  const fetchData = useCallback(async () => {
    try {
      const [health, alerts] = await Promise.all([
        systemAPI.health().catch(() => ({ status: 'degraded' })),
        alertAPI.getStatus().catch(() => ({ 
          total_active: 0, 
          by_severity: {}, 
          recent_alerts: [] 
        })),
      ]);
      
      setSystemHealth(health);
      setAlertStatus(alerts);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // Initial load
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  // Real-time WebSocket Updates
  const { lastMessage, isConnected, connectionFailed } = useWebSocket();

  // Force dark theme in emergency mode
  useEffect(() => {
    if (isEmergencyMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      // Revert to saved theme or system preference
      const savedTheme = localStorage.getItem('rakshak-theme') || 
        (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
      document.documentElement.setAttribute('data-theme', savedTheme);
    }
  }, [isEmergencyMode]);

  useEffect(() => {
    if (lastMessage) {
      console.log('Real-time event received:', lastMessage);
      
      // Refresh data on any relevant event
      if (lastMessage.type === 'ALERT_NEW' || lastMessage.type === 'ANALYSIS_UPDATE') {
        fetchData();
        
        if (lastMessage.payload) {
          setLatestClassification(lastMessage.payload);
        }
      }
    }
  }, [lastMessage, fetchData]);

  // Fallback polling when WebSocket is not connected
  useEffect(() => {
    if (!isConnected) {
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [isConnected, fetchData]);
  
  // Run simulation
  const handleSimulate = async () => {
    setIsSimulating(true);
    setError(null);
    
    // Rotate to next zone for variety
    const currentIndex = ZONES.findIndex(z => z.id === selectedZone);
    const nextIndex = (currentIndex + 1) % ZONES.length;
    const simulationZone = ZONES[nextIndex].id;
    setSelectedZone(simulationZone);
    
    try {
      const result = await systemAPI.simulate(simulationZone, selectedScenario);
      
      // Handle structured response from production controller
      if (result.success) {
        // Include zone_id in the classification for TrackMap
        setLatestClassification({
          ...result.details,
          zone_id: simulationZone
        });
        setScanCount(prev => prev + 1);
        
        // Show notification based on classification
        const zoneName = ZONES.find(z => z.id === simulationZone)?.name || simulationZone;
        if (result.classification === 'CONFIRMED_TAMPERING') {
          notify.critical(`ALERT at ${zoneName}: ${result.classification}! Risk: ${result.risk_score}`);
        } else if (result.classification === 'SUSPICIOUS') {
          notify.warning(`Suspicious activity at ${zoneName}. Risk: ${result.risk_score}`);
        } else {
          notify.success(`${zoneName} scan complete: ${result.classification}`);
        }
      } else {
        console.error('Simulation failed:', result.message);
        setError(result.message);
        notify.warning('Simulation failed: ' + result.message);
      }
      
      // Refresh alert status after simulation
      const alerts = await alertAPI.getStatus();
      
      // MOCK: Ensure we have a visible critical alert for the map if tampering is confirmed
      // This bridges the gap if the backend alert generation is slightly delayed or mocked differently
      if (result.classification === 'CONFIRMED_TAMPERING') {
        const mockCriticalAlert = {
          alert_id: `sim-critical-${Date.now()}`,
          zone_id: simulationZone,
          severity: 'CRITICAL',
          title: 'Tampering Detected',
          status: 'active',
          created_at: new Date().toISOString()
        };
        
        setAlertStatus(prev => ({
          ...alerts,
          recent_alerts: [mockCriticalAlert, ...(alerts?.recent_alerts || [])]
        }));
      } else {
        setAlertStatus(alerts);
      }
    } catch (err) {
      console.error('Simulation failed:', err);
      setError('Simulation failed: ' + err.message);
    } finally {
      setIsSimulating(false);
    }
  };
  
  // Acknowledge alert
  const handleAcknowledge = async (alertId) => {
    try {
      await alertAPI.acknowledge(alertId, 'Operator', 'Acknowledged via dashboard');
      // Refresh alerts
      const alerts = await alertAPI.getStatus();
      setAlertStatus(alerts);
    } catch (err) {
      console.error('Failed to acknowledge:', err);
    }
  };
  
  // View alert details
  const handleViewDetails = (alertId) => {
    console.log('View details for:', alertId);
    // Would open a modal in full implementation
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="app-container">
        <Header systemStatus="loading" />
        <div className="loading-container">
          <Spinner size={60} />
          <p>Connecting to RAKSHAK-AI Server...</p>
        </div>
      </div>
    );
  }
  
  // Get ambient status for glow effect
  const getAmbientStatus = () => {
    if (!latestClassification) return 'safe';
    if (latestClassification.classification === 'CONFIRMED_TAMPERING') return 'danger';
    if (latestClassification.classification === 'SUSPICIOUS') return 'warning';
    return 'safe';
  };
  
  return (
    <div className={`app-container ${isEmergencyMode ? 'emergency-mode' : ''}`}>
        {/* Ambient glow based on system status */}
        <div className={`ambient-glow ambient-glow--${getAmbientStatus()}`} />
        
        
        {/* Sidebar removed - moved to Header */}

        
        <Header 
          systemStatus={isConnected ? (systemHealth?.status || 'healthy') : 'offline'} 
          wsConnected={isConnected}
        />
        
        <main id="main-content" className="main-content">
          {error && (
            <div className="error-banner">
              ⚠️ {error}
              <button onClick={fetchData} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}
          
          {/* Stats Bar is Global */}
          <StatsBar
            totalScans={scanCount}
            alertsToday={alertStatus?.total_active || 0}
            zonesMonitored={ZONES.length}
            avgResponseTime={latestClassification?.processing_time_ms || 15}
            systemUptime={systemHealth?.uptime || 99.9}
            isConnected={isConnected}
          />
          
          
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={
                <PageTransition>
                  <DashboardPage
                    latestClassification={latestClassification}
                    alertStatus={alertStatus}
                    systemHealth={systemHealth}
                    onSimulate={handleSimulate}
                    isSimulating={isSimulating}
                    selectedScenario={selectedScenario}
                    onScenarioChange={setSelectedScenario}
                    isEmergencyMode={isEmergencyMode}
                    setEmergencyMode={setIsEmergencyMode}
                    selectedZone={selectedZone}
                    setSelectedZone={setSelectedZone}
                    handleAcknowledge={handleAcknowledge}
                    handleViewDetails={handleViewDetails}
                  />
                </PageTransition>
              } />
              <Route path="/monitor" element={
                <PageTransition>
                  <LiveMonitorPage latestClassification={latestClassification} />
                </PageTransition>
              } />
              <Route path="/analytics" element={
                <PageTransition>
                  <AnalyticsPage alertStatus={alertStatus} />
                </PageTransition>
              } />
              <Route path="/settings" element={
                <PageTransition>
                  <SettingsPage />
                </PageTransition>
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </main>
      </div>
  );
}

export default App;

