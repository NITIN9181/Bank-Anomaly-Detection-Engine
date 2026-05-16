import { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const AdversarialTestPanel = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runTests = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/tests/adversarial', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (passed) => {
    return passed ? 'bg-green-500' : 'bg-red-500';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'text-green-400',
      medium: 'text-yellow-400',
      high: 'text-red-400',
      critical: 'text-red-600'
    };
    return colors[severity] || 'text-gray-400';
  };

  const renderRobustnessScore = () => {
    if (!results?.summary) return null;

    const score = results.summary.overall_robustness_score;
    const percentage = Math.round(score * 100);
    
    const data = [
      { name: 'Passed', value: percentage },
      { name: 'Failed', value: 100 - percentage }
    ];

    const COLORS = ['#10b981', '#ef4444'];

    return (
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-xl font-semibold text-white mb-4">Overall Robustness Score</h3>
        
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="flex-1 text-center">
            <div className="text-6xl font-bold text-white mb-2">
              {percentage}%
            </div>
            <div className="text-slate-400 text-sm">
              {results.summary.passed}/{results.summary.total_tests} tests passed
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTestCard = (testName, testData) => {
    const passed = testData.passed;
    const statusColor = getStatusColor(passed);
    const severityColor = getSeverityColor(testData.severity);

    return (
      <div key={testName} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h4 className="text-lg font-semibold text-white mb-1">
              {testData.test_name.replace(/_/g, ' ').toUpperCase()}
            </h4>
            <p className="text-slate-400 text-sm">{testData.description}</p>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor} text-white`}>
            {passed ? 'PASSED' : 'FAILED'}
          </div>
        </div>

        {/* Metrics Table */}
        {testData.metrics && Object.keys(testData.metrics).length > 0 && (
          <div className="mb-4">
            <h5 className="text-sm font-semibold text-slate-300 mb-2">Metrics</h5>
            <div className="bg-slate-900 rounded p-3">
              <table className="w-full text-sm">
                <tbody>
                  {Object.entries(testData.metrics).map(([key, value]) => (
                    <tr key={key} className="border-b border-slate-700 last:border-0">
                      <td className="py-2 text-slate-400">{key.replace(/_/g, ' ')}</td>
                      <td className="py-2 text-white text-right font-mono">
                        {typeof value === 'number' ? value.toFixed(3) : String(value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Details List */}
        {testData.details && testData.details.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-slate-300 mb-2">Details</h5>
            <ul className="space-y-1">
              {testData.details.map((detail, idx) => (
                <li key={idx} className="text-sm text-slate-400 flex items-start">
                  <span className="mr-2">•</span>
                  <span>{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Severity Badge */}
        <div className="mt-4 pt-4 border-t border-slate-700">
          <span className="text-xs text-slate-500">Severity: </span>
          <span className={`text-xs font-semibold ${severityColor}`}>
            {testData.severity?.toUpperCase()}
          </span>
        </div>
      </div>
    );
  };

  const renderCriticalVulnerabilities = () => {
    if (!results?.summary?.critical_vulnerabilities || results.summary.critical_vulnerabilities.length === 0) {
      return null;
    }

    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold text-red-400 mb-3 flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Critical Vulnerabilities Detected
        </h3>
        <ul className="space-y-2">
          {results.summary.critical_vulnerabilities.map((vuln, idx) => (
            <li key={idx} className="text-red-300 flex items-center">
              <span className="mr-2">⚠️</span>
              <span className="font-mono">{vuln.replace(/_/g, ' ')}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Adversarial Robustness Testing</h1>
          <p className="text-slate-400">
            Red-team testing framework to validate detection system resilience against attack patterns
          </p>
        </div>

        {/* Run Tests Button */}
        <div className="mb-8">
          <button
            onClick={runTests}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Tests...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Run Adversarial Tests
              </>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-400">Error: {error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Timestamp */}
            <div className="text-slate-400 text-sm">
              Test run: {new Date(results.timestamp).toLocaleString()}
            </div>

            {/* Critical Vulnerabilities Banner */}
            {renderCriticalVulnerabilities()}

            {/* Robustness Score */}
            {renderRobustnessScore()}

            {/* Test Result Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {results.tests && Object.entries(results.tests).map(([testName, testData]) => 
                renderTestCard(testName, testData)
              )}
            </div>

            {/* Warning Footer */}
            {results.warning && (
              <div className="bg-yellow-900/20 border border-yellow-500 rounded-lg p-4">
                <p className="text-yellow-400 text-sm">⚠️ {results.warning}</p>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!results && !loading && (
          <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-xl font-semibold text-slate-400 mb-2">No Test Results</h3>
            <p className="text-slate-500">Click "Run Adversarial Tests" to start testing system robustness</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdversarialTestPanel;
