/**
 * Individual Alert Card Component
 */
import React from 'react';
import { SEVERITY_COLORS } from '../../utils/constants';
import './Alerts.css';
import { AlertOctagon, AlertTriangle, Info, MapPin } from 'lucide-react';

export function AlertCard({ 
  alert, 
  onAcknowledge, 
  onViewDetails 
}) {
  const {
    alert_id,
    severity,
    status,
    title,
    description,
    zone_id,
    risk_score,
    created_at,
    acknowledged,
    acknowledged_by,
  } = alert;
  
  const severityColor = SEVERITY_COLORS[severity] || SEVERITY_COLORS.LOW;
  const timeAgo = getTimeAgo(created_at);
  
  const severityIcon = {
    CRITICAL: <AlertOctagon className="w-6 h-6 text-red-500" />,
    HIGH: <AlertTriangle className="w-6 h-6 text-yellow-500" />,
    MEDIUM: <Info className="w-6 h-6 text-blue-400" />,
    LOW: <MapPin className="w-6 h-6 text-gray-400" />,
  }[severity] || <Info className="w-6 h-6 text-gray-400" />;
  
  return (
    <div 
      className={`alert-card severity-${severity?.toLowerCase()}`}
      style={{ borderLeftColor: severityColor }}
    >
      <div className="alert-icon">
        {severityIcon}
      </div>
      
      <div className="alert-content">
        <div className="alert-header">
          <span className="alert-title">{title}</span>
          <span className="alert-time">{timeAgo}</span>
        </div>
        
        <p className="alert-description">{description}</p>
        
        <div className="alert-meta">
          <span className="alert-zone">{zone_id}</span>
          <span className="alert-score" style={{ color: severityColor }}>
            Risk: {risk_score?.toFixed(0)}%
          </span>
          {acknowledged && (
            <span className="alert-acknowledged">
              ✓ Acknowledged by {acknowledged_by}
            </span>
          )}
        </div>
        
        {status === 'active' && !acknowledged && (
          <div className="alert-actions">
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => onAcknowledge?.(alert_id)}
            >
              Acknowledge
            </button>
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => onViewDetails?.(alert_id)}
            >
              View Details
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper to format time ago
function getTimeAgo(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export default AlertCard;
