import React from 'react';

/**
 * GraphControls Component — Stitch Generated + Enhanced
 * 
 * Stitch Design System: Technical Risk Intelligence
 * 
 * A floating control bar for network graph navigation and filtering.
 * Position: bottom-left, semi-transparent slate-800 background
 * Features: Risk Legend, Zoom Controls, Reset View, Filter Toggles
 */
const GraphControls = ({
  onZoomIn,
  onZoomOut,
  onResetView,
  filters,
  onFilterChange,
  viewMode = 'all',
  onViewModeChange,
}) => {
  const riskLevels = [
    { label: 'Safe', color: 'bg-emerald-500', hex: '#10B981' },
    { label: 'Elevated', color: 'bg-amber-500', hex: '#F59E0B' },
    { label: 'High', color: 'bg-orange-500', hex: '#F97316' },
    { label: 'Critical', color: 'bg-red-500', hex: '#EF4444' },
  ];

  const viewModes = [
    { key: 'all', label: 'All Accounts' },
    { key: 'fraud', label: 'Fraud Rings' },
    { key: 'velocity', label: 'Velocity Links' },
  ];

  return (
    <div className="absolute bottom-6 left-6 flex flex-col gap-3 z-30 pointer-events-none">
      {/* View Mode Toggles */}
      {onViewModeChange && (
        <div className="flex bg-slate-800/85 backdrop-blur-md border border-slate-700/50 rounded-xl shadow-2xl pointer-events-auto ring-1 ring-white/5 p-1.5">
          {viewModes.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => onViewModeChange(key)}
              className={`px-3.5 py-1.5 rounded-lg text-[11px] font-semibold transition-all ${
                viewMode === key
                  ? 'bg-sky-500/20 text-sky-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/40'
              }`}
              style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Main Control Bar */}
      <div className="flex items-center gap-5 p-3.5 bg-slate-800/85 backdrop-blur-md border border-slate-700/50 rounded-xl shadow-2xl pointer-events-auto ring-1 ring-white/5">

        {/* Risk Legend */}
        <div className="flex items-center gap-3.5 pr-5 border-r border-slate-700/40">
          <span
            className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-500"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            Risk
          </span>
          <div className="flex gap-2.5">
            {riskLevels.map((risk) => (
              <div key={risk.label} className="flex items-center gap-1.5 group">
                <div
                  className={`w-2 h-2 rounded-full ${risk.color} transition-transform group-hover:scale-125`}
                  style={risk.label === 'Critical' ? { boxShadow: `0 0 6px ${risk.hex}40` } : {}}
                />
                <span className="text-[10px] text-slate-400 group-hover:text-slate-200 font-medium transition-colors">
                  {risk.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Zoom & Reset Controls */}
        <div className="flex items-center gap-2 pr-5 border-r border-slate-700/40">
          <div className="flex bg-slate-900/50 rounded-lg p-0.5 border border-slate-700/40">
            <button
              onClick={onZoomOut}
              className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
              aria-label="Zoom out"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M20 12H4" />
              </svg>
            </button>
            <button
              onClick={onZoomIn}
              className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
              aria-label="Zoom in"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <button
            onClick={onResetView}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-900/50 hover:bg-slate-700 border border-slate-700/40 rounded-lg text-[10px] font-bold text-slate-400 hover:text-white transition-all"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </button>
        </div>

        {/* Filter Toggles */}
        <div className="flex items-center gap-3.5">
          <span
            className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-500"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            Filter
          </span>
          <div className="flex gap-3">
            {[
              { key: 'showChecking', label: 'Checking' },
              { key: 'showSavings', label: 'Savings' },
              { key: 'showBusiness', label: 'Business' },
            ].map(({ key, label }) => (
              <label key={key} className="flex items-center gap-1.5 cursor-pointer group">
                <div className="relative flex items-center justify-center">
                  <input
                    type="checkbox"
                    checked={filters[key] !== false}
                    onChange={(e) => onFilterChange(key, e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-3.5 h-3.5 border border-slate-600 rounded bg-slate-900 peer-checked:bg-sky-500 peer-checked:border-sky-500 transition-all" />
                  <svg className="absolute w-2.5 h-2.5 text-slate-900 opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-[10px] text-slate-400 group-hover:text-slate-200 font-medium transition-colors">
                  {label}
                </span>
              </label>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default GraphControls;
