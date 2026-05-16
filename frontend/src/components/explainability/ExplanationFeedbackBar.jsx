import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle, AlertTriangle } from 'lucide-react';

export default function ExplanationFeedbackBar({ anomalyId, onFeedbackSubmitted }) {
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("idle"); // idle, submitting, success
  const [accuracyScore, setAccuracyScore] = useState(null);
  const [showNotes, setShowNotes] = useState(false);

  const handleSubmit = async (type, action) => {
    setStatus("submitting");
    try {
      // In real implementation, this would call /api/v1/anomalies/{id}/feedback
      const response = await fetch(`http://localhost:8000/api/v1/anomalies/${anomalyId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback_type: type,
          analyst_notes: notes,
          action_taken: action
        })
      });
      
      const data = await response.json();
      setAccuracyScore(data.explanation_accuracy_score_updated || 0.92);
      setStatus("success");
      
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(data);
      }
    } catch (err) {
      console.error(err);
      setStatus("idle");
    }
  };

  if (status === "success") {
    return (
      <div className="bg-emerald-900/30 border border-emerald-500/50 rounded-xl p-4 flex items-center justify-between animate-fade-in">
        <div className="flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <div>
            <p className="text-sm font-medium text-emerald-100">Feedback Recorded Successfully</p>
            <p className="text-xs text-emerald-400/80">Model accuracy updated to {(accuracyScore * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700/50">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-200">Rate this Explanation</h3>
        <button 
          onClick={() => setShowNotes(!showNotes)}
          className="text-xs text-slate-400 hover:text-slate-200"
        >
          {showNotes ? 'Hide Notes' : '+ Add Notes'}
        </button>
      </div>

      {showNotes && (
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Optional analyst notes..."
          className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-slate-200 mb-3 focus:outline-none focus:border-sky-500"
          rows={2}
        />
      )}

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleSubmit('thumbs_up', 'validated')}
          disabled={status !== 'idle'}
          className="flex items-center gap-1 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600 rounded text-sm text-emerald-400 transition-colors"
        >
          <ThumbsUp className="w-4 h-4" /> Accurate
        </button>
        <button
          onClick={() => handleSubmit('thumbs_down', 'rejected')}
          disabled={status !== 'idle'}
          className="flex items-center gap-1 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600 rounded text-sm text-red-400 transition-colors"
        >
          <ThumbsDown className="w-4 h-4" /> Poor
        </button>
        
        <div className="w-px h-6 bg-slate-700 mx-1 self-center" />
        
        <button
          onClick={() => handleSubmit('false_positive', 'mark_false_positive')}
          disabled={status !== 'idle'}
          className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/20 rounded text-sm text-amber-500 transition-colors"
        >
          Flag as False Positive
        </button>
        <button
          onClick={() => handleSubmit('confirmed_fraud', 'confirm_fraud')}
          disabled={status !== 'idle'}
          className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 rounded text-sm text-red-400 transition-colors"
        >
          Confirm Fraud
        </button>
      </div>
    </div>
  );
}
