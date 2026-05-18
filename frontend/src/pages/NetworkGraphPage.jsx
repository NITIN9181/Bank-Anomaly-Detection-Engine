import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ForceGraph from '../components/graph/ForceGraph';
import GraphDetailsPanel from '../components/graph/GraphDetailsPanel';
import GraphControls from '../components/graph/GraphControls';

/**
 * Network Graph Visualization Page
 * 
 * Stitch Design System: Technical Risk Intelligence
 * 
 * Interactive force-directed graph showing account relationships,
 * transaction flows, and fraud ring detection.
 * 
 * Data source: /api/v1/graph/network
 * Engine: D3-force via ForceGraph wrapper
 * Simulation: link distance=100, charge=-300, collision=30
 */
const NetworkGraphPage = () => {
  const navigate = useNavigate();
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [viewMode, setViewMode] = useState('all');
  const [filters, setFilters] = useState({
    showNormal: true,
    showElevated: true,
    showHighRisk: true,
    showCritical: true,
    showChecking: true,
    showSavings: true,
    showBusiness: true,
  });
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  const graphRef = useRef(null);

  // ─── Data Fetching ───
  const fetchGraphData = useCallback(async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${API_URL}/graph/network?window_hours=24`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setGraphData(data);
      setError(null);

      // Update tab title on fraud ring detection
      if (data.rings && data.rings.length > 0) {
        document.title = `(⚠️) Fraud Ring Detected - Bank Anomaly Engine`;
      } else {
        document.title = 'Network Graph - Bank Anomaly Engine';
      }
    } catch (err) {
      console.error('Failed to fetch graph data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  // Poll for updates every 10 seconds
  useEffect(() => {
    const interval = setInterval(fetchGraphData, 10000);
    return () => clearInterval(interval);
  }, [fetchGraphData]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // ─── Filtering Logic ───
  const getFilteredData = useCallback(() => {
    if (!graphData) return { nodes: [], edges: [] };

    let filteredNodes = graphData.nodes;

    // View mode filter
    if (viewMode === 'fraud') {
      // Show only nodes that are part of fraud rings
      const fraudNodeIds = new Set();
      if (graphData.rings) {
        graphData.rings.forEach(ring => {
          ring.accounts?.forEach(id => fraudNodeIds.add(id));
        });
      }
      // Also show flagged nodes
      filteredNodes = filteredNodes.filter(node =>
        node.flagged || fraudNodeIds.has(node.id) || node.risk_score >= 0.8
      );
    } else if (viewMode === 'velocity') {
      // Show nodes connected to high-velocity edges
      const velocityNodeIds = new Set();
      graphData.edges
        .filter(e => e.velocity_score >= 0.5)
        .forEach(e => {
          velocityNodeIds.add(typeof e.source === 'object' ? e.source.id : e.source);
          velocityNodeIds.add(typeof e.target === 'object' ? e.target.id : e.target);
        });
      filteredNodes = filteredNodes.filter(node => velocityNodeIds.has(node.id));
    }

    // Risk level filters
    filteredNodes = filteredNodes.filter(node => {
      const riskLevel = node.risk_score >= 0.8 ? 'Critical' :
                        node.risk_score >= 0.6 ? 'HighRisk' :
                        node.risk_score >= 0.3 ? 'Elevated' : 'Normal';

      if (!filters[`show${riskLevel}`]) return false;

      // Account type filters
      const accountType = (node.account_type || '').charAt(0).toUpperCase() + (node.account_type || '').slice(1);
      if (filters[`show${accountType}`] === false) return false;

      return true;
    });

    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

    // Filter edges to only include connections between visible nodes
    let filteredEdges = graphData.edges.filter(edge => {
      const sourceId = typeof edge.source === 'object' ? edge.source.id : edge.source;
      const targetId = typeof edge.target === 'object' ? edge.target.id : edge.target;
      return filteredNodeIds.has(sourceId) && filteredNodeIds.has(targetId);
    });

    // In velocity mode, further filter edges
    if (viewMode === 'velocity') {
      filteredEdges = filteredEdges.filter(e => e.velocity_score >= 0.3);
    }

    return { nodes: filteredNodes, edges: filteredEdges };
  }, [graphData, filters, viewMode]);

  // ─── Event Handlers ───
  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  const handleEdgeClick = useCallback((edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  const handleClosePanel = useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
  }, []);

  const handleFilterChange = useCallback((filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  }, []);

  const handleZoomIn = useCallback(() => {
    graphRef.current?.zoomIn();
  }, []);

  const handleZoomOut = useCallback(() => {
    graphRef.current?.zoomOut();
  }, []);

  const handleResetView = useCallback(() => {
    graphRef.current?.resetView();
  }, []);

  const handleViewModeChange = useCallback((mode) => {
    setViewMode(mode);
  }, []);

  // ─── Loading State ───
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-5">
            {/* Outer ring */}
            <div className="absolute inset-0 rounded-full border-2 border-slate-700" />
            {/* Spinning arc */}
            <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-sky-400 animate-spin" />
            {/* Inner dot */}
            <div className="absolute inset-[6px] rounded-full bg-slate-800 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
            </div>
          </div>
          <p className="text-slate-400 text-sm" style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}>
            Loading network graph...
          </p>
          <p className="text-slate-600 text-xs mt-1 font-mono">
            Fetching accounts and connections
          </p>
        </div>
      </div>
    );
  }

  // ─── Error State ───
  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="bg-slate-800/80 border border-red-500/30 rounded-xl p-8 max-w-md shadow-2xl">
          <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-red-500/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-red-300 font-semibold text-center mb-2" style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}>
            Error Loading Graph
          </h3>
          <p className="text-red-400/80 text-sm text-center mb-5 font-mono">{error}</p>
          <button
            onClick={fetchGraphData}
            className="w-full bg-red-600 hover:bg-red-500 text-white px-4 py-2.5 rounded-lg transition-all text-sm font-semibold shadow-lg shadow-red-600/20 active:scale-[0.98]"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  // ─── Main Render ───
  const filteredData = getFilteredData();
  const isPanelOpen = selectedNode || selectedEdge;
  const graphWidth = isPanelOpen ? windowSize.width - 400 : windowSize.width;
  const graphHeight = windowSize.height - 64; // Account for header

  return (
    <div className="min-h-screen bg-slate-900">
      {/* ── Header ── */}
      <header className="bg-slate-800/90 backdrop-blur-md border-b border-slate-700/60 px-6 py-3.5 z-20 relative">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Back Button */}
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-100 transition-all group"
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
              <span className="text-sm font-medium hidden sm:inline">Back</span>
            </button>
            
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1
                className="text-lg font-semibold text-slate-50 tracking-tight"
                style={{ fontFamily: 'Geist, Inter, system-ui, sans-serif' }}
              >
                Fraud Network Graph
              </h1>
              <p className="text-[11px] text-slate-500 mt-0.5" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                {graphData?.metadata?.total_nodes || 0} accounts • {graphData?.metadata?.total_edges || 0} connections
                {graphData?.rings && graphData.rings.length > 0 && (
                  <span className="ml-2 text-red-400 font-semibold">
                    • ⚠ {graphData.rings.length} fraud ring{graphData.rings.length > 1 ? 's' : ''}
                  </span>
                )}
                {filteredData.nodes.length !== (graphData?.metadata?.total_nodes || 0) && (
                  <span className="ml-2 text-sky-400">
                    • Showing {filteredData.nodes.length} filtered
                  </span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick stats */}
            <div className="hidden md:flex items-center gap-4 mr-4">
              {[
                { label: 'HIGH RISK', value: graphData?.nodes?.filter(n => n.risk_score >= 0.6).length || 0, color: 'text-orange-400' },
                { label: 'FLAGGED', value: graphData?.nodes?.filter(n => n.flagged).length || 0, color: 'text-red-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="text-center">
                  <div className={`text-sm font-bold ${color}`} style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    {value}
                  </div>
                  <div className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider">{label}</div>
                </div>
              ))}
            </div>

            {/* Refresh button */}
            <button
              onClick={fetchGraphData}
              className="flex items-center gap-2 bg-slate-700/50 hover:bg-slate-600/60 border border-slate-600/40 text-slate-300 hover:text-white px-3.5 py-2 rounded-lg transition-all text-xs font-semibold"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* ── Graph Container ── */}
      <div className="relative" style={{ height: graphHeight }}>
        <ForceGraph
          ref={graphRef}
          nodes={filteredData.nodes}
          edges={filteredData.edges}
          onNodeClick={handleNodeClick}
          onEdgeClick={handleEdgeClick}
          selectedNodeId={selectedNode?.id}
          width={graphWidth}
          height={graphHeight}
        />

        {/* ── Controls ── */}
        <GraphControls
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onResetView={handleResetView}
          filters={filters}
          onFilterChange={handleFilterChange}
          viewMode={viewMode}
          onViewModeChange={handleViewModeChange}
        />

        {/* ── Empty state overlay ── */}
        {filteredData.nodes.length === 0 && !loading && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center pointer-events-auto">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/60 border border-slate-700/40 flex items-center justify-center">
                <svg className="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <p className="text-slate-400 text-sm font-medium">No accounts match current filters</p>
              <p className="text-slate-600 text-xs mt-1">Try adjusting risk level or account type filters</p>
              <button
                onClick={() => {
                  setFilters({
                    showNormal: true,
                    showElevated: true,
                    showHighRisk: true,
                    showCritical: true,
                    showChecking: true,
                    showSavings: true,
                    showBusiness: true,
                  });
                  setViewMode('all');
                }}
                className="mt-4 px-4 py-2 bg-slate-700/50 hover:bg-slate-600/60 border border-slate-600/40 text-slate-300 rounded-lg text-xs font-medium transition-all"
              >
                Reset All Filters
              </button>
            </div>
          </div>
        )}

        {/* ── Details Panel ── */}
        <GraphDetailsPanel
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          onClose={handleClosePanel}
        />
      </div>
    </div>
  );
};

export default NetworkGraphPage;
