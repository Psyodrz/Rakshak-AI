/**
 * Simulated Badge Component
 * Shows that data is from simulation, not real sensors
 */
import React from 'react';

export function SimulatedBadge({ className = '' }) {
  return (
    <span className={`simulated-badge ${className}`}>
      ⚡ Simulated
    </span>
  );
}

export default SimulatedBadge;
