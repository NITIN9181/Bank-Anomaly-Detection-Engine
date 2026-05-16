/**
 * Layout Component
 * Generated via Stitch MCP design system: "High-Precision Financial Interface"
 * Dashboard shell with fixed navbar, content area, and footer.
 */
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

function Layout({ children }) {
  const [isLive, setIsLive] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Check backend health to set live status
    const checkHealth = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
        const res = await fetch(`${apiUrl}/health`);
        setIsLive(res.ok);
      } catch {
        setIsLive(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-slate-900 border-b border-slate-700/50">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="text-lg font-bold text-slate-50 tracking-tight">
              Anomaly Engine
            </span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-6 ml-8 mr-auto">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors ${
                location.pathname === '/' ? 'text-sky-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/network"
              className={`text-sm font-medium transition-colors ${
                location.pathname === '/network' ? 'text-sky-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Network Graph
            </Link>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 pulse-dot' : 'bg-slate-500'}`} />
            <span className={`text-xs font-medium uppercase tracking-wider ${isLive ? 'text-green-400' : 'text-slate-500'}`}>
              {isLive ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 pt-14">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 py-4">
        <div className="container mx-auto px-4 flex items-center justify-between">
          <p className="text-xs text-slate-600">
            Bank Anomaly Detection Engine
          </p>
          <p className="text-xs text-slate-600 font-mono">
            v1.0.0
          </p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
