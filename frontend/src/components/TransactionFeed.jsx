/**
 * TransactionFeed Component
 * Generated via Stitch MCP design system: "High-Precision Financial Interface"
 * Dark theme transaction table with flagged row indicators.
 */
import React from 'react';

const SkeletonRow = () => (
  <tr className="animate-pulse">
    <td className="px-4 py-3"><div className="h-4 w-24 bg-slate-700 rounded" /></td>
    <td className="px-4 py-3"><div className="h-4 w-32 bg-slate-700 rounded" /></td>
    <td className="px-4 py-3 text-right"><div className="h-4 w-20 bg-slate-700 rounded ml-auto" /></td>
    <td className="px-4 py-3"><div className="h-4 w-16 bg-slate-700 rounded" /></td>
  </tr>
);

function TransactionFeed({ transactions = [], isLoading = false }) {
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
    <div className="bg-slate-900 rounded-lg border border-slate-700/50 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-700/50">
        <h2 className="text-lg font-semibold text-slate-50 tracking-tight">
          Recent Transactions
        </h2>
        <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-medium">
          Live feed • {transactions.length} records
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10">
            <tr className="bg-slate-800/90 backdrop-blur-sm border-b border-slate-700/50">
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Date
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Merchant
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {isLoading ? (
              Array.from({ length: 8 }).map((_, i) => <SkeletonRow key={i} />)
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-4 py-12 text-center text-slate-500">
                  No transactions available.
                </td>
              </tr>
            ) : (
              transactions.map((txn, index) => {
                const isFlagged = txn.status === 'flagged';
                return (
                  <tr
                    key={txn.id || index}
                    className={`
                      group transition-all duration-200 ease-out
                      ${isFlagged
                        ? 'border-l-4 border-l-red-500 bg-red-500/5 hover:bg-red-500/10'
                        : 'border-l-4 border-l-green-500/60 bg-slate-900 hover:bg-slate-800/70'
                      }
                    `}
                  >
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                      {formatDate(txn.date)}
                    </td>
                    <td className="px-4 py-3 text-slate-200 font-medium whitespace-nowrap">
                      {txn.merchant_name || 'Unknown'}
                    </td>
                    <td className={`px-4 py-3 text-right font-mono font-medium whitespace-nowrap ${
                      isFlagged ? 'text-red-400' : 'text-slate-200'
                    }`}>
                      {formatAmount(txn.amount)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {isFlagged ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/15 text-red-400">
                          <span className="w-2 h-2 rounded-full bg-red-500 pulse-dot" />
                          Flagged
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/15 text-green-400">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          Normal
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TransactionFeed;
