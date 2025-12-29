/**
 * Dashboard Page
 * Content formerly in App.jsx's main view
 */
import React from 'react';
import Dashboard from '../components/Dashboard/Dashboard';
import TrackMap from '../components/Map/TrackMap';
import AlertTimeline from '../components/Alerts/AlertTimeline';
import CameraGrid from '../components/Camera/CameraGrid';

export function DashboardPage({ 
  latestClassification, 
  alertStatus, 
  systemHealth, 
  onSimulate, 
  isSimulating, 
  selectedScenario, 
  onScenarioChange, 
  isEmergencyMode, 
  setEmergencyMode,
  selectedZone,
  setSelectedZone,
  handleAcknowledge,
  handleViewDetails
}) {
  return (
    <div className="content-grid">
      {/* Left Column - Dashboard */}
      <div className="content-main">
        <Dashboard
          latestClassification={latestClassification}
          alertStatus={alertStatus}
          systemHealth={systemHealth}
          onSimulate={onSimulate}
          isSimulating={isSimulating}
          selectedScenario={selectedScenario}
          onScenarioChange={onScenarioChange}
          isEmergencyMode={isEmergencyMode}
          setEmergencyMode={setEmergencyMode}
        />
        
        {/* Camera Grid Preview */}
        <CameraGrid latestClassification={latestClassification} />
      </div>
      
      {/* Right Column - Map & Alerts */}
      <div className="content-sidebar">
        <TrackMap
          selectedZone={selectedZone}
          onZoneSelect={setSelectedZone}
          affectedZones={latestClassification?.zone_id ? [latestClassification.zone_id] : []}
          alerts={alertStatus?.recent_alerts || []}
        />
        
        <AlertTimeline
          alerts={alertStatus?.recent_alerts || []}
          onAcknowledge={handleAcknowledge}
          onViewDetails={handleViewDetails}
        />
      </div>
    </div>
  );
}

export default DashboardPage;
