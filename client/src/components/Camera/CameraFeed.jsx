/**
 * Camera Feed Component
 * Displays a single camera feed with simulated overlays and visual effects
 */
import React, { useState, useEffect, useRef } from 'react';
import './CameraGrid.css'; // Reusing the grid styles for now, assuming relevant styles are there or will be added

const CameraFeed = ({ 
  id, 
  name, 
  zone, 
  videoSrc, 
  offset = 0, 
  filterStyle = {},
  isConnected = true,
  detections = []
}) => {
  const [time, setTime] = useState(new Date());
  const videoRef = useRef(null);

  // Simulated timestamp with offset
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      if (offset) {
        now.setSeconds(now.getSeconds() + offset);
      }
      setTime(now);
    };

    updateTime(); // Initial set
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, [offset]);

  // Ensure video keeps playing loop
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(e => {
        console.warn('Auto-play prevented:', e);
      });
    }
  }, [videoRef]);

  return (
    <div className={`camera-feed-container ${!isConnected ? 'offline' : ''}`}>
      <div className="feed-video-wrapper" style={filterStyle}>
        <video
          ref={videoRef}
          src={videoSrc}
          className="feed-video"
          autoPlay
          loop
          muted
          playsInline
        />
        {/* Visual simulated noise/artifacts overlay could go here */}
        <div className="feed-scanlines"></div>
      </div>

      {/* Camera Identity Overlays */}
      <div className="feed-overlay-top">
        <div className="cam-id-badge">{id}</div>
        <div className="cam-zone-badge">{zone}</div>
        <div className="rec-indicator">
          <span className="blink-dot">●</span> REC
        </div>
      </div>

      <div className="feed-overlay-bottom">
        <div className="cam-name">{name}</div>
        <div className="cam-meta">
          <span className="cam-label">Simulated Station CCTV Feed</span>
          <span className="cam-time">
            {time.toISOString().replace('T', ' ').split('.')[0]}
          </span>
        </div>
      </div>

      {/* Simulated Detections */}
      {detections.map((det, i) => (
         <div
           key={i}
           className={`detection-box ${det.type}`}
           style={{
             left: `${det.x}%`,
             top: `${det.y}%`,
             width: `${det.w}%`,
             height: `${det.h}%`,
           }}
         >
           <span className="detection-label">{det.label}</span>
         </div>
      ))}

      {!isConnected && (
        <div className="signal-lost-overlay">
          <span>SIGNAL LOST</span>
        </div>
      )}
    </div>
  );
};

export default CameraFeed;
