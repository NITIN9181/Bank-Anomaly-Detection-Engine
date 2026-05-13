/**
 * TrendModal Component
 * Generated via Stitch MCP design system: "High-Precision Financial Interface"
 * Modal with Recharts line chart for vendor transaction history.
 */
import React, { useEffect, useRef, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
  ReferenceLine,
} from 'recharts';

function TrendModal({ isOpen, onClose, vendorData = [], anomalyPoint = null }) {
  const modalRef = useRef(null);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Click outside to close
  const handleBackdropClick = (e) => {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  };

  // Calculate rolling average
  const chartData = useMemo(() => {
    if (!vendorData.length) return [];
    const windowSize = 3;
    return vendorData.map((point, i) => {
      const start = Math.max(0, i - windowSize + 1);
      const window = vendorData.slice(start, i + 1);
      const avg = window.reduce((sum, p) => sum + p.amount, 0) / window.length;
      return {
        ...point,
        rollingAvg: Math.round(avg * 100) / 100,
      };
    });
  }, [vendorData]);

  // Calculate average for reference line
  const avgAmount = useMemo(() => {
    if (!vendorData.length) return 0;
    return vendorData.reduce((sum, p) => sum + p.amount, 0) / vendorData.length;
  }, [vendorData]);

  const formatCurrency = (value) =>
    `$${Number(value).toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr + 'T00:00:00');
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const isAnomaly =
      anomalyPoint && label === anomalyPoint.date;
    return (
      <div className={`bg-slate-800 border rounded-lg px-4 py-3 shadow-xl ${
        isAnomaly ? 'border-red-500/50' : 'border-slate-600'
      }`}>
        <p className="text-xs text-slate-400 mb-1">{formatDate(label)}</p>
        <p className="text-sm font-mono font-semibold text-slate-100">
          {formatCurrency(payload[0]?.value)}
        </p>
        {payload[1] && (
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Avg: {formatCurrency(payload[1]?.value)}
          </p>
        )}
        {isAnomaly && (
          <p className="text-xs text-red-400 font-semibold mt-1">⚠ Anomalous</p>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div
        ref={modalRef}
        className="bg-slate-900 border border-slate-700/50 rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden animate-in"
        style={{ animation: 'fadeIn 0.2s ease-out' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50">
          <div>
            <h2 className="text-lg font-bold text-slate-50">
              Transaction History
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              6-month performance overview • {vendorData.length} data points
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Chart */}
        <div className="px-6 py-6">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatDate}
                  tick={{ fill: '#94A3B8', fontSize: 11 }}
                  axisLine={{ stroke: '#475569' }}
                  tickLine={{ stroke: '#475569' }}
                />
                <YAxis
                  tickFormatter={formatCurrency}
                  tick={{ fill: '#94A3B8', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#475569' }}
                  tickLine={{ stroke: '#475569' }}
                  width={70}
                />
                <Tooltip content={<CustomTooltip />} />

                {/* Rolling Average (dashed) */}
                <Line
                  type="monotone"
                  dataKey="rollingAvg"
                  stroke="#64748B"
                  strokeDasharray="6 4"
                  strokeWidth={1.5}
                  dot={false}
                  name="Rolling Avg"
                />

                {/* Main Line */}
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke="#38BDF8"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#38BDF8', stroke: '#0F172A', strokeWidth: 2 }}
                  activeDot={{ r: 5, fill: '#38BDF8', stroke: '#0F172A', strokeWidth: 2 }}
                  name="Amount"
                />

                {/* Anomaly Point Highlight */}
                {anomalyPoint && (
                  <ReferenceDot
                    x={anomalyPoint.date}
                    y={anomalyPoint.amount}
                    r={8}
                    fill="transparent"
                    stroke="#EF4444"
                    strokeWidth={2}
                    className="pulse-dot"
                  />
                )}

                {/* Average Reference Line */}
                <ReferenceLine
                  y={avgAmount}
                  stroke="#475569"
                  strokeDasharray="8 4"
                  strokeWidth={1}
                  label={{
                    value: `Avg: ${formatCurrency(avgAmount)}`,
                    position: 'insideTopRight',
                    fill: '#64748B',
                    fontSize: 10,
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-slate-500">
              No trend data available.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-700/50 bg-slate-900/50">
          <p className="text-xs text-slate-500 text-center">
            Data sourced from Plaid Sandbox • Rolling 3-point average
          </p>
        </div>
      </div>
    </div>
  );
}

export default TrendModal;
