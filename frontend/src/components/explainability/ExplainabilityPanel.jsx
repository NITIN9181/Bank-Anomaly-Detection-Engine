import React, { useState, useEffect } from 'react';
import FeatureContributionChart from './FeatureContributionChart';
import ConfidenceGauge from './ConfidenceGauge';
import RecommendedActionsCard from './RecommendedActionsCard';
import ExplanationFeedbackBar from './ExplanationFeedbackBar';
import WhatIfSimulator from './WhatIfSimulator';
import { ShieldAlert } from 'lucide-react';

export default function ExplainabilityPanel({ anomalyId, onActionTaken }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
        const response = await fetch(`${API_URL}/anomalies/${anomalyId}/explain`);
        const json = await response.json();
        setData(json);
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    };
    if (anomalyId) {
      fetchData();
    }
  }, [anomalyId]);

  if (loading) {
    return <div className="flex justify-center items-center h-64 text-slate-400">Loading explainability analysis...</div>;
  }

  if (!data) return null;

  // Extract initial features for the what-if simulator
  const initialFeatures = data.feature_contributions.reduce((acc, feat) => {
    acc[feat.feature_name] = feat.value;
    return acc;
  }, {});

  return (
    <div className="bg-slate-900 text-slate-50 p-6 rounded-xl border border-slate-700/50 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-6 h-6 text-sky-400" />
          <div>
            <h2 className="text-xl font-semibold">Explainability Analysis</h2>
            <p className="text-sm text-slate-400">Transaction #{data.transaction_id} • Detected {new Date(data.generated_at).toLocaleString()}</p>
          </div>
        </div>
        <div className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/30 rounded-full text-xs font-semibold uppercase tracking-wider">
          Anomaly Type: {data.detection_layers.find(l => l.triggered)?.layer || 'Unknown'}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (60%) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ConfidenceGauge confidenceData={data} />
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col justify-center">
              <h3 className="text-sm font-semibold text-slate-400 mb-2 uppercase tracking-wider">AI Summary</h3>
              <p className="text-slate-200 leading-relaxed text-sm">
                {data.llm_summary}
              </p>
            </div>
          </div>
          
          <FeatureContributionChart features={data.feature_contributions} />
          
          <ExplanationFeedbackBar anomalyId={anomalyId} />
        </div>

        {/* Right Column (40%) */}
        <div className="lg:col-span-5 space-y-6">
          <RecommendedActionsCard 
            actions={data.recommended_actions} 
            onExecute={onActionTaken} 
          />
          
          <WhatIfSimulator anomalyId={anomalyId} initialFeatures={initialFeatures} />
        </div>
      </div>
    </div>
  );
}
