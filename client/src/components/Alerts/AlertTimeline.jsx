/**
 * Alert Timeline Component
 * Shows historical alerts and current status
 */
import React from 'react';
import AlertCard from './AlertCard';
import './Alerts.css';
import { Bell, ShieldCheck } from 'lucide-react';

export function AlertTimeline({ 
  alerts = [], 
  onAcknowledge,
  onViewDetails 
}) {
  // Sort alerts by time, most recent first
  const sortedAlerts = [...alerts].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
  
  if (sortedAlerts.length === 0) {
    return (
      <div className="card alert-timeline-card">
        <div className="card-header">
          <h3 className="card-title">
            <span className="icon"><Bell className="w-5 h-5" /></span>
            Alert Timeline
          </h3>
        </div>
        
        <div className="empty-state">
          <div className="secure-shield">
            <span className="empty-icon"><ShieldCheck className="w-12 h-12 text-emerald-500" /></span>
            <div className="shield-pulse"></div>
          </div>
          <p className="empty-text">All Systems Secure</p>
          <p className="empty-subtext">Continuous monitoring active</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="card alert-timeline-card">
      <div className="card-header">
        <h3 className="card-title">
          <span className="icon"><Bell className="w-5 h-5" /></span>
          Alert Timeline
        </h3>
        <span className="badge badge-warning">
          {sortedAlerts.filter(a => a.status === 'active').length} Active
        </span>
      </div>
      
      <div className="alert-list">
        {sortedAlerts.slice(0, 10).map((alert) => (
          <AlertCard
            key={alert.alert_id}
            alert={alert}
            onAcknowledge={onAcknowledge}
            onViewDetails={onViewDetails}
          />
        ))}
      </div>
      
      {sortedAlerts.length > 10 && (
        <div className="alert-more">
          <button className="btn btn-outline">
            View All ({sortedAlerts.length} total)
          </button>
        </div>
      )}
    </div>
  );
}

export default AlertTimeline;
