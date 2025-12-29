/**
 * Analytics Page
 * Detailed reports and graphs
 */
import React from 'react';
import { BarChart2, TrendingUp, AlertOctagon } from 'lucide-react';

export function AnalyticsPage({ alertStatus }) {
  return (
    <div className="page-container p-6">
       <div className="flex items-center gap-3 mb-6">
        <BarChart2 className="w-8 h-8 text-purple-400" />
        <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Analytics & Reports
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card p-4 flex items-center justify-between bg-gradient-to-br from-indigo-900/40 to-black">
          <div>
             <div className="text-gray-400 text-sm">Total Alerts (24h)</div>
             <div className="text-3xl font-bold mt-1">{alertStatus?.alerts_last_24h || 24}</div>
          </div>
          <div className="p-3 bg-indigo-500/20 rounded-full">
            <TrendingUp className="w-6 h-6 text-indigo-400" />
          </div>
        </div>
        
        <div className="card p-4 flex items-center justify-between bg-gradient-to-br from-rose-900/40 to-black">
          <div>
             <div className="text-gray-400 text-sm">Critical Incidents</div>
             <div className="text-3xl font-bold mt-1 text-rose-500">{alertStatus?.by_severity?.CRITICAL || 0}</div>
          </div>
          <div className="p-3 bg-rose-500/20 rounded-full">
            <AlertOctagon className="w-6 h-6 text-rose-500" />
          </div>
        </div>
      </div>

      {/* Placeholder Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-4 h-64 flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Alert Distribution</h3>
          <div className="flex-1 flex items-end justify-between px-4 gap-2">
            {[40, 65, 30, 85, 50, 60, 45].map((h, i) => (
              <div key={i} className="w-full bg-indigo-500/30 hover:bg-indigo-500/50 transition-colors rounded-t" style={{ height: `${h}%` }}></div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500 px-4">
             <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
          </div>
        </div>
        
        <div className="card p-4 h-64 flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Response Time Trend</h3>
           <div className="flex-1 flex items-center justify-center relative">
             <svg className="w-full h-full overflow-visible" preserveAspectRatio="none">
               <path d="M0,80 Q20,70 40,60 T80,50 T120,60 T160,40 T200,30" fill="none" stroke="#10b981" strokeWidth="3" vectorEffect="non-scaling-stroke" />
               <path d="M0,80 Q20,70 40,60 T80,50 T120,60 T160,40 T200,30 L200,100 L0,100 Z" fill="url(#grad)" opacity="0.2" vectorEffect="non-scaling-stroke" />
               <defs>
                 <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                   <stop offset="0%" stopColor="#10b981" stopOpacity="0.5" />
                   <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
                 </linearGradient>
               </defs>
             </svg>
           </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
