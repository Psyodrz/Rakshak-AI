/**
 * Application Constants
 */

export const SEVERITY_COLORS = {
  LOW: '#22c55e',      // Green
  MEDIUM: '#f59e0b',   // Amber
  HIGH: '#f97316',     // Orange
  CRITICAL: '#ef4444', // Red
};

export const CLASSIFICATION_COLORS = {
  SAFE: '#22c55e',
  SUSPICIOUS: '#f59e0b',
  CONFIRMED_TAMPERING: '#ef4444',
};

export const CLASSIFICATION_LABELS = {
  SAFE: 'Safe',
  SUSPICIOUS: 'Suspicious',
  CONFIRMED_TAMPERING: 'Confirmed Tampering',
};

export const SIMULATION_SCENARIOS = [
  { id: 'normal', label: 'Normal Operations' },
  { id: 'environmental', label: 'Environmental Event' },
  { id: 'suspicious', label: 'Suspicious Activity' },
  { id: 'tampering', label: 'Confirmed Tampering' },
];

export const POLL_INTERVAL = 5000; // 5 seconds
