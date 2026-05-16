import { useState } from 'react';

/**
 * Sidebar panel component for displaying account/edge details.
 * 
 * Stitch Design System: Technical Risk Intelligence
 * 
 * Dark theme (slate-800 bg, slate-50 text)
 * Sections: Header (name + risk badge), Metrics Grid, Transaction List, 
 *           Fraud Ring Alert, Account Info
 * Actions: "Investigate" button (amber), "Mark Safe" button (slate)
 */
const GraphDetailsPanel = ({ selectedNode, selectedEdge, onClose }) => {
  const [activeTab, setActiveTab] = useState('details');

  if (!selectedNode && !selectedEdge) return null;

  const getRiskBadgeColor = (riskScore) => {
    if (riskScore >= 0.8) return 'bg-red-500';
    if (riskScore >= 0.6) return 'bg-orange-500';
    if (riskScore >= 0.3) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const getRiskBadgeBg = (riskScore) => {
    if (riskScore >= 0.8) return 'bg-red-500/10 border-red-500/30';
    if (riskScore >= 0.6) return 'bg-orange-500/10 border-orange-500/30';
    if (riskScore >= 0.3) return 'bg-amber-500/10 border-amber-500/30';
    return 'bg-emerald-500/10 border-emerald-500/30';
  };

  const getRiskLabel = (riskScore) => {
    if (riskScore >= 0.8) return 'Critical';
    if (riskScore >= 0.6) return 'High Risk';
    if (riskScore >= 0.3) return 'Elevated';
    return 'Safe';
  };

  const getRiskTextColor = (riskScore) => {
    if (riskScore >= 0.8) return 'text-red-400';
    if (riskScore >= 0.6) return 'text-orange-400';
    if (riskScore >= 0.3) return 'text-amber-400';
    return 'text-emerald-400';
  };

  // Risk score progress bar
  const RiskBar = ({ score }) => {
    const percentage = Math.round(score * 100);
    const barColor = score >= 0.8 ? 'bg-red-500' : score >= 0.6 ? 'bg-orange-500' : score >= 0.3 ? 'bg-amber-500' : 'bg-emerald-500';
    return (
      <div className="mt-3">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            Risk Score
          </span>
          <span className={`text-sm font-bold ${getRiskTextColor(score)}`} style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            {percentage}%
          </span>
        </div>
        <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${barColor} transition-all duration-500 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  };

  // Metric card component
  const MetricCard = ({ label, value, sublabel, highlight }) => (
    <div className={`bg-slate-900/60 border border-slate-700/50 rounded-lg p-3 ${highlight ? 'ring-1 ring-amber-500/20' : ''}`}>
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
        {label}
      </div>
      <div className="text-lg font-bold text-slate-50" style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}>
        {value}
      </div>
      {sublabel && (
        <div className="text-[10px] text-slate-500 mt-0.5">{sublabel}</div>
      )}
    </div>
  );

  // Render node details
  if (selectedNode) {
    return (
      <div className="fixed right-0 top-0 h-full w-[400px] bg-slate-800/95 backdrop-blur-md border-l border-slate-700/60 shadow-2xl overflow-y-auto z-40 animate-slide-in">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800/98 backdrop-blur-md border-b border-slate-700/60 p-5 z-10">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-slate-50 truncate" style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}>
                {selectedNode.label}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5 font-mono">{selectedNode.id}</p>
            </div>
            <button
              onClick={onClose}
              className="ml-3 p-1.5 rounded-lg hover:bg-slate-700/60 text-slate-400 hover:text-slate-200 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Risk badge + score bar */}
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getRiskBadgeBg(selectedNode.risk_score)}`}>
            <span className={`w-2 h-2 rounded-full ${getRiskBadgeColor(selectedNode.risk_score)}`} />
            <span className={`text-xs font-semibold ${getRiskTextColor(selectedNode.risk_score)}`}>
              {getRiskLabel(selectedNode.risk_score)}
            </span>
          </div>

          <RiskBar score={selectedNode.risk_score} />
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-slate-700/60 px-5">
          <div className="flex gap-1">
            {['details', 'activity'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2.5 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 ${
                  activeTab === tab
                    ? 'text-sky-400 border-sky-400'
                    : 'text-slate-500 border-transparent hover:text-slate-300 hover:border-slate-600'
                }`}
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab === 'details' && (
          <>
            {/* Fraud Ring Alert */}
            {selectedNode.flagged && (
              <div className="p-5 border-b border-slate-700/60">
                <div className="bg-red-900/15 border border-red-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2.5 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-red-500/15 flex items-center justify-center">
                      <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-red-400">Fraud Ring Alert</h4>
                      <p className="text-xs text-red-400/70">Automated pattern detected</p>
                    </div>
                  </div>
                  <p className="text-xs text-red-300/80 leading-relaxed">
                    This account matches known patterns for automated fund dispersion. Review transaction links and velocity patterns.
                  </p>
                </div>
              </div>
            )}

            {/* Metrics Grid */}
            <div className="p-5 border-b border-slate-700/60">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                Key Metrics
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <MetricCard
                  label="Transactions"
                  value={selectedNode.transaction_count}
                />
                <MetricCard
                  label="Total Volume"
                  value={`$${(selectedNode.total_volume || 0).toLocaleString()}`}
                />
                <MetricCard
                  label="Balance"
                  value={`$${(selectedNode.balance || 0).toLocaleString()}`}
                />
                <MetricCard
                  label="Account Type"
                  value={
                    <span className="capitalize text-base">
                      {selectedNode.account_type}
                    </span>
                  }
                />
              </div>
            </div>

            {/* Account Information */}
            <div className="p-5">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                Account Info
              </h4>
              <div className="space-y-2.5">
                {[
                  { label: 'Persona', value: selectedNode.persona },
                  { label: 'Status', value: selectedNode.status },
                  { label: 'Account Type', value: selectedNode.account_type },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between items-center py-1.5 border-b border-slate-700/30">
                    <span className="text-xs text-slate-500">{label}</span>
                    <span className="text-xs text-slate-200 capitalize font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'activity' && (
          <div className="p-5">
            <div className="text-center py-12">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-slate-700/30 flex items-center justify-center">
                <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm text-slate-500">Activity timeline coming soon</p>
              <p className="text-xs text-slate-600 mt-1">Transaction history and events</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="sticky bottom-0 p-5 bg-slate-800/98 backdrop-blur-md border-t border-slate-700/60">
          <div className="flex gap-3">
            <button className="flex-1 bg-amber-600 hover:bg-amber-500 text-white font-semibold py-2.5 px-4 rounded-lg transition-all text-sm shadow-lg shadow-amber-600/20 hover:shadow-amber-500/30 active:scale-[0.98]">
              Investigate
            </button>
            <button className="flex-1 bg-slate-700/60 hover:bg-slate-600/80 text-slate-200 font-semibold py-2.5 px-4 rounded-lg transition-all text-sm border border-slate-600/50 active:scale-[0.98]">
              Mark Safe
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render edge details
  if (selectedEdge) {
    return (
      <div className="fixed right-0 top-0 h-full w-[400px] bg-slate-800/95 backdrop-blur-md border-l border-slate-700/60 shadow-2xl overflow-y-auto z-40 animate-slide-in">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800/98 backdrop-blur-md border-b border-slate-700/60 p-5 z-10">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold text-slate-50" style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}>
                Transaction Flow
              </h3>
              <p className="text-xs text-slate-500 mt-0.5 font-mono">{selectedEdge.id}</p>
            </div>
            <button
              onClick={onClose}
              className="ml-3 p-1.5 rounded-lg hover:bg-slate-700/60 text-slate-400 hover:text-slate-200 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getRiskBadgeBg(selectedEdge.risk_score)}`}>
            <span className={`w-2 h-2 rounded-full ${getRiskBadgeColor(selectedEdge.risk_score)}`} />
            <span className={`text-xs font-semibold ${getRiskTextColor(selectedEdge.risk_score)}`}>
              {getRiskLabel(selectedEdge.risk_score)}
            </span>
          </div>

          <RiskBar score={selectedEdge.risk_score} />
        </div>

        {/* Metrics Grid */}
        <div className="p-5 border-b border-slate-700/60">
          <h4 className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            Flow Metrics
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="Transactions" value={selectedEdge.transaction_count} />
            <MetricCard label="Total Amount" value={`$${(selectedEdge.total_amount || 0).toLocaleString()}`} />
            <MetricCard
              label="Velocity Score"
              value={`${((selectedEdge.velocity_score || 0) * 100).toFixed(0)}%`}
              highlight={selectedEdge.velocity_score >= 0.6}
            />
            <MetricCard
              label="Time Clustered"
              value={selectedEdge.time_clustered_txns || 0}
              highlight={selectedEdge.time_clustered_txns > 0}
            />
          </div>
        </div>

        {/* Anomaly Flags */}
        {selectedEdge.anomaly_flags && selectedEdge.anomaly_flags.length > 0 && (
          <div className="p-5 border-b border-slate-700/60">
            <h4 className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              Anomaly Flags
            </h4>
            <div className="space-y-2">
              {selectedEdge.anomaly_flags.map((flag, idx) => (
                <div key={idx} className="flex items-center gap-2.5 py-2 px-3 bg-red-900/10 border border-red-500/20 rounded-lg">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                  <span className="text-xs text-red-300 capitalize font-medium">{flag.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Link Information */}
        <div className="p-5">
          <h4 className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-3" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            Link Info
          </h4>
          <div className="space-y-2.5">
            {[
              { label: 'Link Type', value: (selectedEdge.link_type || '').replace(/_/g, ' ') },
              { label: 'Link Strength', value: `${((selectedEdge.link_strength || 0) * 100).toFixed(0)}%` },
              { label: 'Last Transaction', value: selectedEdge.last_transaction ? new Date(selectedEdge.last_transaction).toLocaleDateString() : 'N/A' },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center py-1.5 border-b border-slate-700/30">
                <span className="text-xs text-slate-500">{label}</span>
                <span className="text-xs text-slate-200 capitalize font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default GraphDetailsPanel;
