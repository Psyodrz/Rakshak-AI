
import { useContext } from 'react';
import { WebSocketContext } from '../context/WebSocketContext';

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    // Return safe defaults if used outside provider
    return { isConnected: false, lastMessage: null, connectionFailed: true };
  }
  return context;
};
