import { useEffect, useRef, useState } from 'react';
import AnomalyCard from './components/AnomalyCard';
import Layout from './components/Layout';
import StatsBar from './components/StatsBar';
import TransactionFeed from './components/TransactionFeed';
import TrendModal from './components/TrendModal';
import useInterval from './hooks/useInterval';
import { getAnomalies, getStats, getTransactions, triggerDetect } from './services/api';

function App() {
  // State management
  const [transactions, setTransactions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [stats, setStats] = useState({
    total_transactions: 0,
    total_anomalies: 0,
    flag_rate_percent: 0,
    top_anomalous_vendor: null,
  });
  const [selectedVendorData, setSelectedVendorData] = useState([]);
  const [selectedAnomalyPoint, setSelectedAnomalyPoint] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const prevAnomalyCount = useRef(0);
  const [error, setError] = useState(null);

  // Data fetching functions
  const fetchTransactions = async () => {
    try {
      const response = await getTransactions(100, 0);
      setTransactions(response.data.items || []);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    }
  };

  const fetchAnomalies = async () => {
    try {
      const response = await getAnomalies('flagged', 50, 0);
      const newAnomalies = response.data.items || [];

      // Browser tab flash: only trigger after initial load (prevAnomalyCount > 0)
      if (newAnomalies.length > prevAnomalyCount.current && prevAnomalyCount.current > 0) {
        const originalTitle = document.title;
        document.title = `(1) Anomaly Detected - Bank Anomaly Engine`;
        setTimeout(() => {
          document.title = originalTitle;
        }, 3000);
      }
      prevAnomalyCount.current = newAnomalies.length;

      setAnomalies(newAnomalies);
    } catch (err) {
      console.error('Failed to fetch anomalies:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await getStats();
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleViewTrend = (anomaly) => {
    // Modal data: filter vendor transactions, sort chronologically, format for Recharts
    const vendorTxns = transactions.filter(
      (t) => t.merchant_name === anomaly.transaction.merchant_name
    );

    // Sort by date
    const sorted = vendorTxns.sort((a, b) => new Date(a.date) - new Date(b.date));

    // Format for Recharts
    const chartData = sorted.map((t) => ({
      date: t.date,
      amount: t.amount,
    }));

    setSelectedVendorData(chartData);
    setSelectedAnomalyPoint({
      date: anomaly.transaction.date,
      amount: anomaly.transaction.amount,
    });
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedVendorData([]);
    setSelectedAnomalyPoint(null);
  };

  const handleTriggerDetect = async () => {
    try {
      setIsLoading(true);
      await triggerDetect();
      // Refresh data after detection
      await Promise.all([fetchTransactions(), fetchAnomalies(), fetchStats()]);
    } catch (err) {
      setError('Detection failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    const loadInitial = async () => {
      setIsLoading(true);
      await Promise.all([fetchTransactions(), fetchAnomalies(), fetchStats()]);
      setIsLoading(false);
    };
    loadInitial();
  }, []);

  // Polling strategy: 5s for anomalies (real-time feel), 10s for stats, 30s for transactions
  useInterval(() => {
    fetchAnomalies();
  }, 5000);

  useInterval(() => {
    fetchStats();
  }, 10000);

  // Periodic transaction refresh every 30s
  useInterval(() => {
    fetchTransactions();
  }, 30000);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-6">
        {/* Stats Bar */}
        <StatsBar stats={stats} />

        {/* Action Bar */}
        <div className="flex justify-between items-center mt-6 mb-4">
          <h2 className="text-xl font-semibold text-finance-text">Live Feed</h2>
          <button
            onClick={handleTriggerDetect}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition"
          >
            {isLoading ? 'Processing...' : 'Run Detection'}
          </button>
        </div>

        {/* Error Toast */}
        {error && (
          <div className="mb-4 p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
            {error}
            <button onClick={() => setError(null)} className="ml-4 text-sm underline">
              Dismiss
            </button>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Transaction Feed - 60% */}
          <div className="lg:col-span-3">
            <TransactionFeed transactions={transactions} isLoading={isLoading} />
          </div>

          {/* Anomaly Panel - 40% */}
          <div className="lg:col-span-2">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-finance-text">
                Flagged Anomalies ({anomalies.length})
              </h3>
            </div>

            {anomalies.length === 0 ? (
              <div className="p-8 text-center text-finance-muted bg-finance-card rounded-xl">
                <svg
                  className="w-12 h-12 mx-auto mb-4 text-finance-muted"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p>All clear. No anomalies detected in current window.</p>
              </div>
            ) : (
              <div className="space-y-4 max-h-[800px] overflow-y-auto pr-2">
                {anomalies.map((anomaly) => (
                  <AnomalyCard
                    key={anomaly.id}
                    anomaly={anomaly}
                    onViewTrend={() => handleViewTrend(anomaly)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Trend Modal */}
        <TrendModal
          isOpen={modalOpen}
          onClose={handleCloseModal}
          vendorData={selectedVendorData}
          anomalyPoint={selectedAnomalyPoint}
        />
      </div>
    </Layout>
  );
}

export default App;
