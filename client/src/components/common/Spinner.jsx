/**
 * Loading Spinner Component
 */
import React from 'react';

export function Spinner({ size = 40 }) {
  return (
    <div 
      className="spinner" 
      style={{ width: size, height: size }}
    />
  );
}

export default Spinner;
