import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download } from 'lucide-react';
import ExplainabilityPanel from '../components/explainability/ExplainabilityPanel';

export default function ExplainabilityPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const handleActionTaken = (actionId) => {
    console.log(`Executing action: ${actionId}`);
    // Here you would hook into global state or call an API to trigger the action
  };

  const handleExport = () => {
    // Stub for export functionality
    alert("Exporting analysis to PDF/JSON...");
  };

  return (
    <div className="min-h-screen bg-[#0f111a] text-slate-50 p-6 overflow-y-auto">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Bar */}
        <div className="flex justify-between items-center mb-6">
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </button>

          <button 
            onClick={handleExport}
            className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors border border-slate-700 px-3 py-1.5 rounded hover:bg-slate-800"
          >
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </div>

        <ExplainabilityPanel anomalyId={parseInt(id, 10)} onActionTaken={handleActionTaken} />
      </div>
    </div>
  );
}
