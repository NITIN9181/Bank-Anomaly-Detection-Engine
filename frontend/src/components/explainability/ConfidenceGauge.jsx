import React, { useEffect, useState } from 'react';

export default function ConfidenceGauge({ confidenceData }) {
  const [fill, setFill] = useState(0);
  const score = confidenceData?.overall_confidence || 0;
  const breakdown = confidenceData?.confidence_breakdown || {};

  useEffect(() => {
    // Animate fill on load
    setTimeout(() => setFill(score * 100), 100);
  }, [score]);

  const getColorClass = (val) => {
    if (val < 50) return 'text-emerald-500 stroke-emerald-500 bg-emerald-500';
    if (val < 70) return 'text-amber-500 stroke-amber-500 bg-amber-500';
    if (val < 85) return 'text-orange-500 stroke-orange-500 bg-orange-500';
    return 'text-red-500 stroke-red-500 bg-red-500';
  };

  const colorClasses = getColorClass(fill);
  
  // SVG arc calculation
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (fill / 100) * circumference;

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col items-center">
      <h3 className="text-lg font-semibold text-slate-50 mb-6 w-full text-left">Confidence</h3>
      
      <div className="relative w-32 h-32 mb-6">
        {/* Background Circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-slate-700"
          />
          {/* Progress Circle */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={`transition-all duration-1000 ease-out-cubic ${colorClasses.split(' ')[1]}`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${colorClasses.split(' ')[0]}`}>
            {fill.toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="w-full space-y-2 text-xs">
        <LayerBar label="Statistical" val={breakdown.statistical_layer * 100} />
        <LayerBar label="ML Model" val={breakdown.ml_layer * 100} />
        <LayerBar label="Duplicate" val={breakdown.duplicate_layer * 100} />
        <LayerBar label="Agreement" val={breakdown.layer_agreement * 100} />
      </div>
    </div>
  );
}

function LayerBar({ label, val }) {
  const width = Math.max(0, Math.min(100, val || 0));
  return (
    <div className="flex justify-between items-center w-full">
      <span className="text-slate-400 w-20">{label}</span>
      <div className="flex-1 bg-slate-900 h-1.5 rounded-full mx-2 overflow-hidden">
        <div className="bg-slate-500 h-full rounded-full" style={{ width: `${width}%` }} />
      </div>
      <span className="text-slate-300 font-mono w-8 text-right">{width.toFixed(0)}%</span>
    </div>
  );
}
