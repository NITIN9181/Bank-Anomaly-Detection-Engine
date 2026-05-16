import React, { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Play } from 'lucide-react';
// import { debounce } from 'lodash'; // If you have lodash, otherwise we implement a simple debounce

export default function WhatIfSimulator({ anomalyId, initialFeatures }) {
  const [params, setParams] = useState({
    amount: initialFeatures.amount_deviation || 1000,
    velocity: initialFeatures.velocity_cluster || 1,
  });
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Helper to find initial values safely
  const origAmount = initialFeatures.amount_deviation || 1000;
  const origVelocity = initialFeatures.velocity_cluster || 1;

  const runSimulation = async (currentParams) => {
    setLoading(true);
    try {
      const qs = new URLSearchParams({
        amount: currentParams.amount,
        velocity: currentParams.velocity
      }).toString();
      
      const response = await fetch(`http://localhost:8000/api/v1/anomalies/${anomalyId}/what-if?${qs}`);
      const data = await response.json();
      setSimResult(data);
    } catch (e) {
      console.error(e);
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
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-300">Amount</span>
            <span className="text-slate-100 font-mono">${params.amount}</span>
          </div>
          <input 
            type="range" 
            min="0" max={Math.max(origAmount * 3, 5000)} step="50"
            value={params.amount}
            onChange={(e) => setParams({...params, amount: parseFloat(e.target.value)})}
            className="w-full accent-sky-500"
          />
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-300">Velocity (Tx/hr)</span>
            <span className="text-slate-100 font-mono">{params.velocity}</span>
          </div>
          <input 
            type="range" 
            min="0" max={Math.max(origVelocity * 3, 10)} step="0.5"
            value={params.velocity}
            onChange={(e) => setParams({...params, velocity: parseFloat(e.target.value)})}
            className="w-full accent-amber-500"
          />
        </div>
      </div>

      {loading && <div className="text-slate-400 text-sm animate-pulse">Running simulation...</div>}

      {simResult && !loading && (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 animate-fade-in">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm text-slate-400">Simulated Confidence</span>
            <span className="text-lg font-bold text-slate-100">
              {(simResult.simulated_confidence * 100).toFixed(0)}%
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
