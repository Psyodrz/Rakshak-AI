/**
 * Emergency Panel Component
 * =========================
 * 
 * Displays controls for managing emergency situations.
 * Included dispatch buttons, status indicators, and de-escalation control.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { useNotifications } from '../../context/NotificationContext';
import './EmergencyPanel.css';
import { Siren, ShieldAlert, Truck, Flame, Lock, Volume2 } from 'lucide-react';

export function EmergencyPanel({ onDeescalate }) {
  const [activeActions, setActiveActions] = React.useState([]);
  const { notify } = useNotifications();

  const toggleAction = (action) => {
    if (activeActions.includes(action)) {
      setActiveActions(prev => prev.filter(a => a !== action));
      notify.info(`${action.toUpperCase()} disengaged`);
    } else {
      setActiveActions(prev => [...prev, action]);
      
      // Simulation feedback
      switch(action) {
        case 'police':
          notify.success('🚓 POLICE UNITS DISPATCHED to location');
          break;
        case 'medical':
          notify.success('🚑 MEDICAL TEAM alert sent');
          break;
        case 'fire':
          notify.success('🚒 FIRE BRIGADE responders notified');
          break;
        case 'lockdown':
          notify.critical('🔒 LOCKDOWN PROTOCOL INITIATED - All exits sealing...');
          break;
        case 'alarm':
          notify.warning('📢 EMERGENCY ALARM TRIGGERED');
          break;
        default:
          break;
      }
    }
  };

  return (
    <motion.div 
      className="emergency-panel"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
    >
      <div className="emergency-header">
        <div className="emergency-status">
          <span className="status-icon"><ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" /></span>
          <div className="status-text">
            <h2>CODE RED: LOCKDOWN ACTIVE</h2>
            <p>CRITICAL THREAT DETECTED - AUTHORIZED PERSONNEL ONLY</p>
          </div>
        </div>
        <button 
          className="btn-deescalate"
          onClick={onDeescalate}
        >
          DE-ESCALATE / STAND DOWN
        </button>
      </div>

      <div className="emergency-grid">
        <div className="emergency-column">
          <h3>DISPATCH UNITS</h3>
          <div className="action-buttons">
            <button 
              className={`btn-action police ${activeActions.includes('police') ? 'active' : ''}`}
              onClick={() => toggleAction('police')}
            >
              <div className="flex items-center gap-2"><Siren className="w-5 h-5" /> POLICE DISPATCH {activeActions.includes('police') && '✓'}</div>
            </button>
            <button 
              className={`btn-action medical ${activeActions.includes('medical') ? 'active' : ''}`}
              onClick={() => toggleAction('medical')}
            >
              <div className="flex items-center gap-2"><Truck className="w-5 h-5" /> MEDICAL TEAM {activeActions.includes('medical') && '✓'}</div>
            </button>
            <button 
              className={`btn-action fire ${activeActions.includes('fire') ? 'active' : ''}`}
              onClick={() => toggleAction('fire')}
            >
              <div className="flex items-center gap-2"><Flame className="w-5 h-5" /> FIRE BRIGADE {activeActions.includes('fire') && '✓'}</div>
            </button>
          </div>
        </div>

        <div className="emergency-column">
          <h3>SYSTEM CONTROLS</h3>
          <div className="action-buttons">
            <button 
              className={`btn-action lockdown ${activeActions.includes('lockdown') ? 'active' : ''}`}
              onClick={() => toggleAction('lockdown')}
            >
              <div className="flex items-center gap-2"><Lock className="w-5 h-5" /> SEAL ALL EXITS {activeActions.includes('lockdown') && 'ENFORCED'}</div>
            </button>
            <button 
              className={`btn-action alarm ${activeActions.includes('alarm') ? 'active' : ''}`}
              onClick={() => toggleAction('alarm')}
            >
              <div className="flex items-center gap-2"><Volume2 className="w-5 h-5" /> TRIGGER ALARM {activeActions.includes('alarm') && 'SOUNDING'}</div>
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default EmergencyPanel;
