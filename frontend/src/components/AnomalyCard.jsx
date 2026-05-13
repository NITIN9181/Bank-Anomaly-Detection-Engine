/**
 * AnomalyCard Component
 * Generated via Stitch MCP design system: "High-Precision Financial Interface"
 * Dark theme card for displaying flagged financial anomalies.
 */
import React from 'react';

const BADGE_CONFIG = {
  volumetric: {
    bg: 'bg-red-500/15',
    text: 'text-red-400',
    border: 'border-red-500/30',
    label: 'Volumetric',
  },
  deviant_pattern: {
    bg: 'bg-amber-500/15',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    label: 'Deviant',
  },
  duplicate: {
    bg: 'bg-violet-500/15',
    text: 'text-violet-400',
    border: 'border-violet-500/30',
    label: 'Duplicate',
  },
};

function AnomalyCard({ anomaly, onViewTrend }) {
  const { transaction, anomaly_type, z_score, isolation_score, explanation } = anomaly;
  const badge = BADGE_CONFIG[anomaly_type] || BADGE_CONFIG.volumetric;

  const formatAmount = (amount) => {
    const absAmount = Math.abs(amount);
    const prefix = amount < 0 ? '-' : '';
    return `${prefix}$${absAmount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr + 'T00:00:00');
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="slide-in bg-slate-800 rounded-xl border border-slate-700/50 shadow-lg shadow-black/20 overflow-hidden transition-all duration-300 hover:border-slate-600/50 hover:shadow-xl hover:shadow-black/30">
      {/* Header */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="text-lg font-bold text-slate-50 truncate">
              {transaction?.merchant_name || 'Unknown Merchant'}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {formatDate(transaction?.date)}
            </p>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xl font-bold font-mono text-sky-400">
              {formatAmount(transaction?.amount || 0)}
            </p>
          </div>
        </div>

        {/* Badge + Score */}
        <div className="flex items-center gap-2 mt-3">
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${badge.bg} ${badge.text} ${badge.border}`}>
            {badge.label}
          </span>
          {z_score != null && (
            <span className="text-xs text-slate-500 font-mono">
              z={Math.abs(z_score).toFixed(2)}
            </span>
          )}
          {isolation_score != null && (
            <span className="text-xs text-slate-500 font-mono">
              iso={isolation_score.toFixed(3)}
            </span>
          )}
        </div>
      </div>

      {/* Explanation */}
      {explanation && (
        <div className="px-5 py-3 mx-5 mb-3 bg-slate-900/50 rounded-lg border-l-2 border-slate-600">
          <p className="text-sm text-slate-300 italic leading-relaxed">
            "{explanation}"
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="px-5 py-3 border-t border-slate-700/50">
        <button
          onClick={onViewTrend}
          className="w-full px-4 py-2 text-sm font-medium text-slate-300 border border-slate-600 rounded-lg hover:bg-slate-700 hover:text-slate-100 hover:border-slate-500 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
        >
          View Trend →
        </button>
      </div>
    </div>
  );
}

export default AnomalyCard;
