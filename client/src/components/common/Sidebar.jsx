/**
 * Sidebar Navigation Component
 */
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Cctv, BarChart2, Settings, Shield } from 'lucide-react';
import './Sidebar.css';

export function Sidebar() {
  const navItems = [
    { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { path: '/monitor', label: 'Monitor', icon: <Cctv size={20} /> },
    { path: '/analytics', label: 'Analytics', icon: <BarChart2 size={20} /> },
    { path: '/settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Shield className="w-8 h-8 text-blue-500" />
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `nav-item ${isActive ? 'active' : ''}`
            }
          >
            {item.icon}
            <span className="nav-label">{item.label}</span>
            <div className="nav-indicator" />
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
