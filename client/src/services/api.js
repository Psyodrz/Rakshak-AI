/**
 * API Service
 * -----------
 * Centralized API communication with the RAKSHAK-AI server.
 */

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Generic fetch wrapper with error handling
 * 
 * IMPORTANT: For simulation endpoints, we don't throw on non-2xx
 * because the server returns structured error responses.
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    const data = await response.json();
    
    // For simulation endpoint, return data even on error (structured response)
    if (endpoint === '/system/simulate') {
      return data;
    }
    
    if (!response.ok) {
      throw new Error(data.message || data.detail || `HTTP ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Vision Analysis API
 */
export const visionAPI = {
  analyze: (zoneId, imageSource = 'cctv', scenario = null) => 
    fetchAPI('/vision/analyze', {
      method: 'POST',
      body: JSON.stringify({
        zone_id: zoneId,
        image_source: imageSource,
        use_simulated: true,
        simulate_scenario: scenario,
      }),
    }),
  
  getSources: () => fetchAPI('/vision/sources'),
  getStats: () => fetchAPI('/vision/stats'),
};

/**
 * Sensor Analysis API
 */
export const sensorAPI = {
  analyze: (zoneId, scenario = null) =>
    fetchAPI('/sensor/analyze', {
      method: 'POST',
      body: JSON.stringify({
        zone_id: zoneId,
        use_simulated: true,
        simulate_scenario: scenario,
      }),
    }),
  
  getTypes: () => fetchAPI('/sensor/types'),
  getStatus: (zoneId) => fetchAPI(`/sensor/status/${zoneId}`),
};

/**
 * Intent Classification API (Core Intelligence)
 */
export const intentAPI = {
  classify: (zoneId, scenario = null) =>
    fetchAPI('/intent/classify', {
      method: 'POST',
      body: JSON.stringify({
        zone_id: zoneId,
        run_vision_analysis: true,
        run_sensor_analysis: true,
        use_simulated: true,
        simulate_scenario: scenario,
      }),
    }),
  
  getClassifications: () => fetchAPI('/intent/classifications'),
  getThresholds: () => fetchAPI('/intent/thresholds'),
};

/**
 * Alert Management API
 */
export const alertAPI = {
  getStatus: () => fetchAPI('/alert/status'),
  getHistory: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchAPI(`/alert/history${query ? `?${query}` : ''}`);
  },
  getAlert: (alertId) => fetchAPI(`/alert/${alertId}`),
  acknowledge: (alertId, acknowledgedBy, notes = '') =>
    fetchAPI('/alert/acknowledge', {
      method: 'POST',
      body: JSON.stringify({
        alert_id: alertId,
        acknowledged_by: acknowledgedBy,
        notes,
        mark_as_false_positive: false,
      }),
    }),
  resolve: (alertId, resolvedBy, notes, wasActualTampering) =>
    fetchAPI('/alert/resolve', {
      method: 'POST',
      body: JSON.stringify({
        alert_id: alertId,
        resolved_by: resolvedBy,
        resolution_notes: notes,
        was_actual_tampering: wasActualTampering,
      }),
    }),
  getSeverityLevels: () => fetchAPI('/alert/severity-levels'),
};

/**
 * System Management API
 */
export const systemAPI = {
  health: () => fetchAPI('/system/health'),
  simulate: (zoneId = 'ZONE-001', scenario = 'suspicious') =>
    fetchAPI('/system/simulate', {
      method: 'POST',
      body: JSON.stringify({
        zone_id: zoneId,
        scenario,
      }),
    }),
  simulationStatus: () => fetchAPI('/system/simulate/status'),
  simulationReset: () => fetchAPI('/system/simulate/reset', { method: 'POST' }),
  getZones: () => fetchAPI('/system/zones'),
  getScenarios: () => fetchAPI('/system/scenarios'),
  getConfig: () => fetchAPI('/system/config'),
  getAuditRecent: (limit = 50) => fetchAPI(`/system/audit/recent?limit=${limit}`),
  getAuditStats: () => fetchAPI('/system/audit/stats'),
};

/**
 * Combined API object for convenience
 */
export default {
  vision: visionAPI,
  sensor: sensorAPI,
  intent: intentAPI,
  alert: alertAPI,
  system: systemAPI,
};
