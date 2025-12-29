import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import App from './App'
import './index.css'

import { WebSocketProvider } from './context/WebSocketContext';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import { SmoothScrollProvider } from './components/3d/SmoothScrollProvider';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <NotificationProvider>
        <SmoothScrollProvider>
          <WebSocketProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </WebSocketProvider>
        </SmoothScrollProvider>
      </NotificationProvider>
    </ThemeProvider>
  </React.StrictMode>,
)
