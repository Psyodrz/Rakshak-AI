/**
 * WebSocket Context for RAKSHAK-AI
 * 
 * React wrapper around the WebSocket singleton service.
 * The actual connection is managed by the service, not React.
 */
import React, { createContext, useEffect, useState } from 'react';
import wsService from '../services/websocket';

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(wsService.getStatus().isConnected);
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionFailed, setConnectionFailed] = useState(false);

  useEffect(() => {
    // Subscribe to WebSocket events
    const unsubscribe = wsService.subscribe(({ isConnected, message }) => {
      setIsConnected(isConnected);
      setConnectionFailed(wsService.getStatus().connectionFailed);
      if (message) {
        setLastMessage(message);
      }
    });

    return unsubscribe;
  }, []);

  // Heartbeat
  useEffect(() => {
    if (!isConnected) return;
    
    const heartbeat = setInterval(() => {
      wsService.send('ping');
    }, 25000);
    
    return () => clearInterval(heartbeat);
  }, [isConnected]);

  return (
    <WebSocketContext.Provider value={{ isConnected, lastMessage, connectionFailed }}>
      {children}
    </WebSocketContext.Provider>
  );
};
