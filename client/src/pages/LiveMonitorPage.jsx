/**
 * Live Monitor Page
 * Dedicated full-screen camera monitoring
 */
import React from 'react';
import CameraGrid from '../components/Camera/CameraGrid';
import { Cctv } from 'lucide-react';

export function LiveMonitorPage({ latestClassification }) {
  return (
    <div className="page-container p-6">
      <div className="flex items-center gap-3 mb-6">
        <Cctv className="w-8 h-8 text-indigo-400" />
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Live Surveillance
        </h1>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        {/* Main Feed */}
        <div className="card p-4">
          <CameraGrid latestClassification={latestClassification} />
        </div>
        
        {/* Additional Feeds (Mocked for visual density) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
           {[1, 2, 3, 4].map(id => (
             <div key={id} className="card p-2 bg-black/40 border border-white/10 aspect-video flex items-center justify-center relative overflow-hidden group">
               <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/60 rounded text-xs font-mono text-emerald-400 flex items-center gap-1">
                 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                 CAM-0{id + 4}
               </div>
               <div className="text-white/20 font-mono text-sm">NO SIGNAL</div>
               {/* Scanline effect */}
               <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent -translate-y-full group-hover:translate-y-full transition-transform duration-1000" />
             </div>
           ))}
        </div>
      </div>
    </div>
  );
}

export default LiveMonitorPage;
