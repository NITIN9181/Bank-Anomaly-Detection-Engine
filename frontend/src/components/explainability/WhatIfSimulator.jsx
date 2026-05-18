import React, { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Play } from 'lucide-react';
// import { debounce } from 'lodash'; // If you have lodash, otherwise we implement a simple debounce

export default function WhatIfSimulator({ anomalyId, initialFeatures = {} }) {
  // Helper to find initial values safely with fallbacks
  const origAmount = initialFeatures.amount_deviation || initialFeatures.amount || 1000;
  const origVelocity = initialFeatures.velocity_cluster || initialFeatures.velocity_score || 1;

  const [params, setParams] = useState({
    amount: origAmount,
    velocity: origVelocity,
  });
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async (currentParams) => {
    setLoading(true);
    try {
      const qs = new URLSearchParams({
        amount: currentParams.amount,
        velocity: currentParams.velocity
      }).toString();
      
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${API_URL}/anomalies/${anomalyId}/what-if?${qs}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSimResult(data);
    } catch (e) {
      console.error('What-if simulation error:', e);
      setSimResult({ error: 'Failed to run simulation' });
    }
    setLoading(false);
  };

  const handleApply = () => {
    runSimulation(params);
  };

  const handleReset = () => {
    const resetParams = { amount: origAmount, velocity: origVelocity };
    setParams(resetParams);
    setSimResult(null);
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 mt-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-50">What-If Simulator</h3>
        <div className="flex gap-2">
          <button onClick={handleReset} className="p-1.5 text-slate-400 hover:text-slate-200 transition-colors" title="Reset">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button onClick={handleApply} className="flex items-center gap-1 px-3 py-1.5 bg-sky-500/10 text-sky-400 border border-sky-500/30 rounded text-xs hover:bg-sky-500/20 transition-colors">
            <Play className="w-3 h-3" /> Apply
          </button>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <div className="flex justify-between items-center text-sm mb-2">
            <span className="text-slate-300">Amount</span>
            <div className="flex items-center gap-2">
              <span className="text-slate-400 text-xs">$</span>
              <input
                type="number"
                value={params.amount}
                onChange={(e) => setParams({...params, amount: parseFloat(e.target.value) || 0})}
                className="w-24 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100 font-mono text-sm focus:outline-none focus:border-sky-500"
                step="50"
                min="0"
              />
            </div>
          </div>
          <input 
            type="range" 
            min="0" max={Math.max(origAmount * 3, 5000)} step="50"
            value={params.amount}
            onChange={(e) => setParams({...params, amount: parseFloat(e.target.value)})}
            className="w-full accent-sky-500"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>$0</span>
            <span className="text-slate-400">Original: ${origAmount.toFixed(0)}</span>
            <span>${Math.max(origAmount * 3, 5000).toFixed(0)}</span>
          </div>
        </div>
        <div>
          <div className="flex justify-between items-center text-sm mb-2">
            <span className="text-slate-300">Velocity (Tx/hr)</span>
            <input
              type="number"
              value={params.velocity}
              onChange={(e) => setParams({...params, velocity: parseFloat(e.target.value) || 0})}
              className="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-100 font-mono text-sm focus:outline-none focus:border-amber-500"
              step="0.5"
              min="0"
            />
          </div>
          <input 
            type="range" 
            min="0" max={Math.max(origVelocity * 3, 10)} step="0.5"
            value={params.velocity}
            onChange={(e) => setParams({...params, velocity: parseFloat(e.target.value)})}
            className="w-full accent-amber-500"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>0</span>
            <span className="text-slate-400">Original: {origVelocity.toFixed(1)}</span>
            <span>{Math.max(origVelocity * 3, 10).toFixed(1)}</span>
          </div>
        </div>
      </div>

      {loading && <div className="text-slate-400 text-sm animate-pulse">Running simulation...</div>}

      {simResult && simResult.error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
          {simResult.error}
        </div>
      )}

      {simResult && !loading && !simResult.error && (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 animate-fade-in">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm text-slate-400">Simulated Confidence</span>
            <span className="text-lg font-bold text-slate-100">
              {((simResult.simulated_confidence || 0) * 100).toFixed(0)}%
            </span>
          </div>
          
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm text-slate-400">Would Still Flag?</span>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${simResult.would_still_flag ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {simResult.would_still_flag ? 'YES' : 'NO'}
            </span>
          </div>

          {simResult.changed_features?.length > 0 && (
            <div className="text-xs space-y-2 border-t border-slate-700 pt-3">
              {simResult.changed_features.map((f, i) => (
                <div key={i} className="text-slate-300">
                  <span className="font-medium text-sky-400">{f.feature_name}:</span> {f.impact}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
