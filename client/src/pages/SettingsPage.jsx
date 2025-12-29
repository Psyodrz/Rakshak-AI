/**
 * Settings Page
 */
import React from 'react';
import { Settings, Bell, Volume2, Shield, Moon, Monitor } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import { useTheme } from '../context/ThemeContext';

export function SettingsPage() {
  const { soundEnabled, setSoundEnabled } = useNotifications();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="page-container p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Settings className="w-8 h-8 text-gray-400" />
        <h1 className="text-2xl font-bold text-gray-100">System Settings</h1>
      </div>

      <div className="grid gap-6">
        {/* Preferences */}
        <div className="card">
          <div className="card-header border-b border-white/10 p-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Monitor className="w-5 h-5 text-blue-400" /> Preferences
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${theme === 'dark' ? 'bg-indigo-500/20' : 'bg-yellow-500/20'}`}>
                  {theme === 'dark' ? <Moon className="w-5 h-5 text-indigo-400" /> : <Settings className="w-5 h-5 text-yellow-400" />}
                </div>
                <div>
                  <div className="font-medium">Dark Mode</div>
                  <div className="text-sm text-gray-400">Use system dark theme</div>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={theme === 'dark'}
                  onChange={toggleTheme}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="card">
          <div className="card-header border-b border-white/10 p-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Bell className="w-5 h-5 text-rose-400" /> Notifications
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${soundEnabled ? 'bg-emerald-500/20' : 'bg-gray-700/50'}`}>
                  <Volume2 className={`w-5 h-5 ${soundEnabled ? 'text-emerald-400' : 'text-gray-400'}`} />
                </div>
                <div>
                  <div className="font-medium">Sound Alerts</div>
                  <div className="text-sm text-gray-400">Play audio for critical alerts</div>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={soundEnabled}
                  onChange={() => setSoundEnabled(!soundEnabled)}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="card">
          <div className="card-header border-b border-white/10 p-4">
             <h2 className="text-lg font-semibold flex items-center gap-2">
              <Shield className="w-5 h-5 text-emerald-400" /> System Information
            </h2>
          </div>
          <div className="p-4 grid grid-cols-2 gap-4">
            <div className="p-3 bg-white/5 rounded-lg border border-white/5">
              <div className="text-sm text-gray-400">Version</div>
              <div className="font-mono text-lg">v2.4.1-RC</div>
            </div>
            <div className="p-3 bg-white/5 rounded-lg border border-white/5">
              <div className="text-sm text-gray-400">Node ID</div>
              <div className="font-mono text-lg">RX-001</div>
            </div>
            <div className="p-3 bg-white/5 rounded-lg border border-white/5">
              <div className="text-sm text-gray-400">License</div>
              <div className="font-mono text-lg text-emerald-400">Active</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
