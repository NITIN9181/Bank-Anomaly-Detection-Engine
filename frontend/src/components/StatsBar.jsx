/**
 * StatsBar Component
 * Generated via Stitch MCP design system: "High-Precision Financial Interface"
 */
import React from 'react';
import { Activity, AlertTriangle, TrendingUp, Building2 } from 'lucide-react';

function StatsBar({ stats = {} }) {
  const {
    total_transactions = 0,
    total_anomalies = 0,
    flag_rate_percent = 0,
    top_anomalous_vendor = null,
  } = stats;

  const hasAnomalies = total_anomalies > 0;

  const cards = [
    {
      label: 'Total Transactions',
      value: total_transactions.toLocaleString(),
      icon: Activity,
      iconColor: 'text-sky-400',
      iconBg: 'bg-sky-400/10',
      glow: false,
    },
    {
      label: 'Total Anomalies',
      value: total_anomalies.toLocaleString(),
      icon: AlertTriangle,
      iconColor: hasAnomalies ? 'text-red-400' : 'text-slate-400',
      iconBg: hasAnomalies ? 'bg-red-400/10' : 'bg-slate-400/10',
      glow: hasAnomalies,
    },
    {
      label: 'Flag Rate',
      value: `${flag_rate_percent.toFixed(2)}%`,
      icon: TrendingUp,
      iconColor: flag_rate_percent > 5 ? 'text-amber-400' : 'text-green-400',
      iconBg: flag_rate_percent > 5 ? 'bg-amber-400/10' : 'bg-green-400/10',
      glow: false,
    },
    {
      label: 'Top Vendor',
      value: top_anomalous_vendor || '—',
      icon: Building2,
      iconColor: 'text-violet-400',
      iconBg: 'bg-violet-400/10',
      glow: false,
      isText: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div
            key={i}
            className={`bg-slate-800 rounded-lg border border-slate-700/50 p-5 transition-all duration-300 hover:border-slate-600/50 ${
              card.glow
                ? 'shadow-[0_0_20px_rgba(239,68,68,0.15)] border-red-500/30 hover:shadow-[0_0_25px_rgba(239,68,68,0.25)]'
                : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  {card.label}
                </p>
                <p className={`font-bold font-mono truncate ${
                  card.isText ? 'text-lg text-slate-200' : 'text-2xl text-slate-50'
                }`}>
                  {card.value}
                </p>
              </div>
              <div className={`p-2.5 rounded-lg ${card.iconBg} flex-shrink-0`}>
                <Icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default StatsBar;
