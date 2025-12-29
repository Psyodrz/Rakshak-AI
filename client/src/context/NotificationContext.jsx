/**
 * Notification Context
 * Manages toast notifications and browser alerts
 */
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import './Notifications.css';
import { AlertOctagon, AlertTriangle, CheckCircle, Info } from 'lucide-react';

const NotificationContext = createContext(null);

let notificationId = 0;

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  
  // Keep track of notifications for check in callbacks
  const notificationsRef = React.useRef(notifications);
  useEffect(() => {
    notificationsRef.current = notifications;
  }, [notifications]);
  
  // Play alert sound
  const playSound = useCallback((type) => {
    if (!soundEnabled) return;
    
    // Create audio context for sound
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      if (type === 'critical') {
        oscillator.frequency.value = 880;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.3;
      } else if (type === 'warning') {
        oscillator.frequency.value = 660;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.2;
      } else {
        oscillator.frequency.value = 440;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.1;
      }
      
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15);
    } catch (e) {
      console.log('Audio not supported');
    }
  }, [soundEnabled]);
  
  // Add notification
  const addNotification = useCallback((message, type = 'info', duration = 5000) => {
    // Deduplicate: Don't add if identical message exists
    if (notificationsRef.current.some(n => n.message === message && n.type === type)) {
      return -1;
    }
    
    const id = ++notificationId;
    
    setNotifications(prev => [...prev, { id, message, type, timestamp: Date.now() }]);
    
    // Play sound for warnings and criticals
    if (type === 'critical' || type === 'warning') {
      playSound(type);
    }
    
    // Browser notification for critical
    if (type === 'critical' && Notification.permission === 'granted') {
      new Notification('🚨 RAKSHAK-AI Alert', {
        body: message,
        icon: '/favicon.ico',
        tag: 'rakshak-critical',
      });
    }
    
    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
    
    return id;
  }, [playSound]);
  
  // Remove notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);
  
  // Request browser notification permission
  const requestPermission = useCallback(async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }, []);
  
  // Convenience methods
  const notify = {
    info: (msg, duration) => addNotification(msg, 'info', duration),
    success: (msg, duration) => addNotification(msg, 'success', duration),
    warning: (msg, duration) => addNotification(msg, 'warning', duration),
    critical: (msg, duration) => addNotification(msg, 'critical', duration || 0), // Critical stays until dismissed
  };
  
  return (
    <NotificationContext.Provider value={{ 
      notifications, 
      addNotification, 
      removeNotification, 
      notify,
      soundEnabled,
      setSoundEnabled,
      requestPermission
    }}>
      {children}
      
      {/* Toast Container */}
      <div className="toast-container">
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            className={`toast toast-${notification.type}`}
          >
            <span className="toast-icon">
              {notification.type === 'critical' ? <AlertOctagon size={18} /> :
               notification.type === 'warning' ? <AlertTriangle size={18} /> :
               notification.type === 'success' ? <CheckCircle size={18} /> : <Info size={18} />}
            </span>
            <span className="toast-message">{notification.message}</span>
            <button 
              className="toast-close"
              onClick={() => removeNotification(notification.id)}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}

export default NotificationContext;
