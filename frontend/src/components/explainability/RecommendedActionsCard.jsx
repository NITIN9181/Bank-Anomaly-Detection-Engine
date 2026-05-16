import React from 'react';
import { Phone, Shield, Search, Copy, User, Check } from 'lucide-react';

const iconMap = {
  phone: Phone,
  shield: Shield,
  search: Search,
  copy: Copy,
  user: User,
  check: Check
};

export default function RecommendedActionsCard({ actions = [], onExecute }) {
  if (!actions.length) return null;

  const getBorderColor = (priority) => {
    if (priority === 1) return 'border-l-red-500';
    if (priority === 2) return 'border-l-amber-500';
    return 'border-l-slate-500';
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50">
      <h3 className="text-lg font-semibold text-slate-50 mb-4">Recommended Actions</h3>
      <div className="space-y-3">
        {actions.map((action, idx) => {
          const IconComponent = iconMap[action.icon] || Check;
          
          return (
            <div 
              key={action.action_id}
              className={`bg-slate-900 rounded-lg p-4 border border-slate-700 border-l-4 ${getBorderColor(action.priority)} hover:bg-slate-700/40 transition-colors group flex items-start justify-between`}
              style={{ animationDelay: `${idx * 150}ms` }}
            >
              <div className="flex gap-3">
                <div className="mt-1 bg-slate-800 p-1.5 rounded text-slate-300">
                  <IconComponent className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-medium text-slate-200">{action.label}</h4>
                    {action.automation_possible && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        Auto
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-xs">
                    {action.description}
                  </p>
                  <div className="mt-2 text-[10px] text-slate-500 font-mono">
                    Est. {action.estimated_time}
                  </div>
                </div>
              </div>
              <button
                onClick={() => onExecute(action.action_id)}
                className="px-3 py-1.5 text-xs font-medium text-amber-500 border border-amber-500/50 rounded hover:bg-amber-500/10 transition-colors"
              >
                Execute
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
