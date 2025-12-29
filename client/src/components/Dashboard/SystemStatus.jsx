/**
 * System Status Component
 * Shows key system metrics in card format
 */
import React from 'react';
import './Dashboard.css';
import { Bell, Siren, AlertTriangle, BarChart2 } from 'lucide-react';

export function SystemStatus({ alertStatus, systemHealth }) {
  const stats = [
    {
      label: 'Active Alerts',
      value: alertStatus?.total_active || 0,
      color: alertStatus?.total_active > 0 ? 'var(--color-danger)' : 'var(--color-success)',
      icon: <Bell className="w-5 h-5" />
    },
    {
      label: 'Critical',
      value: alertStatus?.by_severity?.CRITICAL || 0,
      color: 'var(--color-danger)',
      icon: <Siren className="w-5 h-5 text-red-500" />
    },
    {
      label: 'High',
      value: alertStatus?.by_severity?.HIGH || 0,
      color: '#f97316',
      icon: <AlertTriangle className="w-5 h-5 text-yellow-500" />
    },
    {
      label: 'Alerts (24h)',
      value: alertStatus?.alerts_last_24h || 0,
      color: 'var(--color-text-primary)',
      icon: <BarChart2 className="w-5 h-5 text-blue-400" />
    }
  ];
  
  return (
    <div className="system-status-grid">
      {stats.map((stat, index) => (
        <div key={index} className="stat-card">
          <div className="stat-header">
            <span className="stat-icon">{stat.icon}</span>
            <span className="stat-label">{stat.label}</span>
          </div>
          <div className="stat-value" style={{ color: stat.color }}>
            {stat.value}
          </div>
        </div>
      ))}
    </div>
  );
}

export default SystemStatus;
