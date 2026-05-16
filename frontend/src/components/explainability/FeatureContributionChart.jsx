import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

export default function FeatureContributionChart({ features = [] }) {
  // Sort descending by score
  const sortedFeatures = [...features].sort((a, b) => b.contribution_score - a.contribution_score);

  const getCategoryColor = (category) => {
    switch (category) {
      case 'volumetric': return 'bg-red-500';
      case 'behavioral': return 'bg-amber-500';
      case 'structural': return 'bg-violet-500';
      case 'temporal': return 'bg-blue-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50">
      <h3 className="text-lg font-semibold text-slate-50 mb-4">Feature Contributions</h3>
      <div className="space-y-4">
        {sortedFeatures.map((feat) => {
          const widthPct = Math.max(2, feat.contribution_score * 100);
          return (
            <div key={feat.feature_name} className="group cursor-pointer">
              <div className="flex justify-between items-end mb-1 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-slate-200">{feat.display_name}</span>
                  {feat.direction === 'positive' ? 
                    <ArrowUp className="w-3 h-3 text-red-400" /> : 
                    <ArrowDown className="w-3 h-3 text-emerald-400" />
                  }
                </div>
                <span className="text-slate-400 font-mono">{(feat.contribution_score * 100).toFixed(0)}%</span>
              </div>
              
              <div className="w-full bg-slate-900 rounded-full h-2 mb-2 overflow-hidden">
                <div 
                  className={`h-2 rounded-full ${getCategoryColor(feat.category)} transition-all duration-1000 ease-out`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>

              {/* Expandable details on hover */}
              <div className="hidden group-hover:block text-xs text-slate-400 bg-slate-900/50 p-2 rounded border border-slate-700/30">
                <p className="mb-1">{feat.description}</p>
                <div className="flex justify-between font-mono">
                  <span>Actual: {typeof feat.value === 'number' ? feat.value.toFixed(2) : feat.value}</span>
                  <span className="opacity-50">Baseline: {typeof feat.baseline === 'number' ? feat.baseline.toFixed(2) : feat.baseline}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
