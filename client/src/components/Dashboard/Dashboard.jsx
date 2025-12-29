/**
 * Main Dashboard Component
 * Combines RiskMeter, SystemStatus, and key information
 */
import React from 'react';
import RiskMeter from './RiskMeter';
import SystemStatus from './SystemStatus';
import SimulatedBadge from '../common/SimulatedBadge';
import CameraFeed from '../Camera/CameraFeed'; // Imported CameraFeed
import EmergencyPanel from './EmergencyPanel';
import { Play, Activity, Gamepad2, ClipboardList, Target, Search, Camera, BarChart2, Zap } from 'lucide-react';
import './Dashboard.css';

export function Dashboard({ 
  latestClassification, 
  alertStatus, 
  systemHealth,
  onSimulate,
  isSimulating,
  selectedScenario,
  onScenarioChange,
  isEmergencyMode,
  setEmergencyMode
}) {
  const classification = latestClassification?.classification || 'SAFE';
  const riskScore = latestClassification?.risk_score || 0;
  const confidence = latestClassification?.confidence || 1;
  const reasons = latestClassification?.primary_reasons || [];
  const actions = latestClassification?.recommended_actions || [];
  
  return (
    <div className="dashboard">
      {/* System Controls */}
      <div className="simulation-controls">
        <span className="simulation-label flex items-center gap-2">
          <Gamepad2 className="w-5 h-5 text-indigo-400" /> System Control:
        </span>
        <select 
          className="scenario-select"
          value={selectedScenario}
          onChange={(e) => onScenarioChange(e.target.value)}
          disabled={isEmergencyMode}
        >
          <option value="normal">Normal Operations</option>
          <option value="environmental">Environmental Event</option>
          <option value="suspicious">Suspicious Activity</option>
          <option value="tampering">Confirmed Tampering</option>
        </select>
        <button 
          className="btn btn-primary"
          onClick={onSimulate}
          disabled={isSimulating || isEmergencyMode}
        >
          {isSimulating ? (
            <span className="flex items-center gap-2"><Activity className="w-4 h-4 animate-spin" /> Analyzing...</span>
          ) : (
             <span className="flex items-center gap-2"><Play className="w-4 h-4" /> Run Analysis</span>
          )}
        </button>
        
        {!isEmergencyMode && (
          <button 
            className="btn btn-outline"
            onClick={() => setEmergencyMode(true)}
            style={{ borderColor: '#ef4444', color: '#ef4444' }}
          >
            <span className="flex items-center gap-2"><Zap className="w-4 h-4" /> TRIGGER EMERGENCY</span>
          </button>
        )}
      </div>
      
      {/* Emergency Panel */}
      {isEmergencyMode && (
        <EmergencyPanel onDeescalate={() => setEmergencyMode(false)} />
      )}
      
      {/* Stats Overview */}
      <SystemStatus alertStatus={alertStatus} systemHealth={systemHealth} />
      
      {/* Main Dashboard Grid */}
      <div className="dashboard-top">
        {/* Risk Meter */}
        <RiskMeter 
          riskScore={riskScore}
          classification={classification}
          confidence={confidence}
        />
        
        {/* Reasons Card */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <span className="icon"><ClipboardList className="w-5 h-5" /></span>
              Analysis Summary
            </h3>
            {latestClassification?.zone_id && (
              <span className="text-muted text-sm">
                Zone: {latestClassification.zone_id}
              </span>
            )}
          </div>
          
          {reasons.length > 0 ? (
            <ul className="reason-list">
              {reasons.map((reason, index) => (
                <li 
                  key={index} 
                  className={`reason-item ${
                    reason.includes('🔴') ? 'danger' : 
                    reason.includes('🟡') || reason.includes('⚠️') ? 'warning' : ''
                  }`}
                >
                  {reason}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted text-sm">
              Run analysis to see diagnostic results
            </p>
          )}
        </div>
      </div>
      
      {/* Recommended Actions */}
      {actions.length > 0 && (
        <div className="dashboard-section">
          <div className="section-header">
            <h3 className="section-title">
              <span><Target className="w-5 h-5 text-cyan-400" /></span>
              Recommended Actions
            </h3>
          </div>
          
          <ul className="action-list">
            {actions.map((action, index) => (
              <li 
                key={index} 
                className={`action-item ${
                  action.includes('CRITICAL') || action.includes('IMMEDIATE') 
                    ? 'critical' : ''
                }`}
              >
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Evidence Preview */}
      <div className="dashboard-section">
        <div className="section-header">
          <h3 className="section-title">
            <span><Search className="w-5 h-5 text-indigo-400" /></span>
            Evidence Preview
          </h3>
        </div>
        
        <div className="evidence-preview">
          <div className="evidence-item">
            <div className="evidence-header">
              <span className="evidence-title flex items-center gap-2">
                <Camera className="w-4 h-4 text-indigo-400" /> CCTV Feed
              </span>
              <SimulatedBadge />
            </div>
            <div className="evidence-content" style={{ height: '280px', padding: 0, overflow: 'hidden', display: 'block', position: 'relative' }}>
              {/* Always show camera feed for preview, or condition on simulation start if preferred. 
                  Showing it always makes it look more "live". */}
               <CameraFeed 
                 id="PREVIEW-01" 
                 name="Live Analysis Feed" 
                 zone={latestClassification?.zone_id || "ZONE-SCAN"} 
                 videoSrc="/cctv/cam_station_entry.mp4" 
                 offset={20}
                 filterStyle={{ filter: 'contrast(1.2) brightness(0.9)' }}
                 isConnected={true}
               />
            </div>

          </div>
          
          <div className="evidence-item">
            <div className="evidence-header">
              <span className="evidence-title flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-purple-400" /> Sensor Data
              </span>
              <SimulatedBadge />
            </div>
            <div className="evidence-content">
              {latestClassification?.classification_id ? (
                <div className="sensor-visualization">
                  {['VIB', 'TILT', 'PRES'].map((type, typeIdx) => (
                    <React.Fragment key={type}>
                      {[1, 2].map((n) => {
                        const sensorScore = latestClassification?.sensor_risk_score || 0;
                        const hasAnomaly = sensorScore > 30 && Math.random() > 0.5;
                        const barHeight = Math.min(20 + sensorScore * 0.7 + (typeIdx * 10) + (n * 5), 95);
                        return (
                          <div key={`${type}-${n}`} className="sensor-bar-wrapper">
                            <div className="sensor-bar-container">
                              <div 
                                className={`sensor-bar ${hasAnomaly ? 'anomaly' : ''}`}
                                style={{ height: `${barHeight}%` }}
                              />
                            </div>
                            <span className="sensor-label">{type}{n}</span>
                          </div>
                        );
                      })}
                    </React.Fragment>
                  ))}
                </div>
              ) : (
                <span className="evidence-placeholder">
                  No sensor data<br/>Run simulation to analyze
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
