import { useEffect, useRef, useState, useCallback, useImperativeHandle, forwardRef } from 'react';
import * as d3 from 'd3';
import GraphNode from './GraphNode';
import GraphEdge from './GraphEdge';

/**
 * D3 Force-Directed Graph Wrapper Component
 * 
 * Wraps a custom D3 force simulation with:
 * - Custom node rendering via GraphNode (Stitch-generated)
 * - Custom link rendering via GraphEdge (Stitch-generated)
 * - Force simulation: link distance=100, charge=-300, collision=30
 * - Zoom/pan via d3-zoom with imperative zoom controls
 * - Auto-zoom to fit on data load
 * - Subtle grid pattern background (slate-900)
 */
const ForceGraph = forwardRef(({
  nodes,
  edges,
  onNodeClick,
  onEdgeClick,
  selectedNodeId,
  width,
  height,
}, ref) => {
  const svgRef = useRef(null);
  const [simulationNodes, setSimulationNodes] = useState([]);
  const [simulationEdges, setSimulationEdges] = useState([]);
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 });
  const simulationRef = useRef(null);
  const zoomRef = useRef(null);
  const [isSimulating, setIsSimulating] = useState(true);

  // Expose zoom controls via ref
  useImperativeHandle(ref, () => ({
    zoomIn: () => {
      if (!svgRef.current || !zoomRef.current) return;
      const svg = d3.select(svgRef.current);
      svg.transition().duration(300).call(zoomRef.current.scaleBy, 1.3);
    },
    zoomOut: () => {
      if (!svgRef.current || !zoomRef.current) return;
      const svg = d3.select(svgRef.current);
      svg.transition().duration(300).call(zoomRef.current.scaleBy, 0.7);
    },
    resetView: () => {
      if (!svgRef.current || !zoomRef.current) return;
      const svg = d3.select(svgRef.current);
      zoomToFit(svg, zoomRef.current);
    },
  }));

  // Zoom-to-fit helper
  const zoomToFit = useCallback((svg, zoom) => {
    if (!simulationNodes.length) return;

    const padding = 80;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

    simulationNodes.forEach(n => {
      if (n.x !== undefined && n.y !== undefined) {
        minX = Math.min(minX, n.x);
        maxX = Math.max(maxX, n.x);
        minY = Math.min(minY, n.y);
        maxY = Math.max(maxY, n.y);
      }
    });

    if (minX === Infinity) return;

    const graphWidth = maxX - minX + padding * 2;
    const graphHeight = maxY - minY + padding * 2;
    const midX = (minX + maxX) / 2;
    const midY = (minY + maxY) / 2;

    const scale = Math.min(
      0.9 * width / graphWidth,
      0.9 * height / graphHeight,
      2  // max zoom
    );

    const translateX = width / 2 - scale * midX;
    const translateY = height / 2 - scale * midY;

    svg.transition()
      .duration(750)
      .ease(d3.easeCubicInOut)
      .call(
        zoom.transform,
        d3.zoomIdentity.translate(translateX, translateY).scale(scale)
      );
  }, [simulationNodes, width, height]);

  // Force simulation setup
  useEffect(() => {
    if (!nodes || !edges || !svgRef.current || nodes.length === 0) return;

    // Create deep copies for simulation
    const nodesCopy = nodes.map(n => ({ ...n }));
    const edgesCopy = edges.map(e => ({ ...e }));

    // Build node map
    const nodeMap = new Map(nodesCopy.map(n => [n.id, n]));

    // Resolve edge source/target references
    edgesCopy.forEach(edge => {
      edge.source = nodeMap.get(edge.source) || edge.source;
      edge.target = nodeMap.get(edge.target) || edge.target;
    });

    setIsSimulating(true);

    // Create simulation with improved spacing parameters
    const simulation = d3.forceSimulation(nodesCopy)
      .force('link', d3.forceLink(edgesCopy)
        .id(d => d.id)
        .distance(150)  // Increased from 100 to 150
        .strength(0.3)  // Reduced from 0.5 to 0.3 for looser connections
      )
      .force('charge', d3.forceManyBody()
        .strength(-800)  // Increased from -300 to -800 for stronger repulsion
      )
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide()
        .radius(50)  // Increased from 30 to 50 for more spacing
        .strength(1.0)  // Increased from 0.8 to 1.0 for stronger collision avoidance
      )
      .force('x', d3.forceX(width / 2).strength(0.05))  // Added gentle centering force
      .force('y', d3.forceY(height / 2).strength(0.05))  // Added gentle centering force
      .alpha(1)
      .alphaDecay(0.015);  // Reduced from 0.02 to 0.015 for longer simulation

    // Update state on tick
    simulation.on('tick', () => {
      setSimulationNodes([...nodesCopy]);
      setSimulationEdges([...edgesCopy]);
    });

    simulation.on('end', () => {
      setIsSimulating(false);
      // Auto zoom to fit when simulation settles
      if (svgRef.current && zoomRef.current) {
        const svg = d3.select(svgRef.current);
        setTimeout(() => zoomToFit(svg, zoomRef.current), 100);
      }
    });

    simulationRef.current = simulation;

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, width, height, zoomToFit]);

  // Zoom behavior setup
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);

    const zoom = d3.zoom()
      .scaleExtent([0.1, 5])
      .on('zoom', (event) => {
        setTransform(event.transform);
      });

    svg.call(zoom);
    zoomRef.current = zoom;

    // Prevent double-click zoom
    svg.on('dblclick.zoom', null);

    return () => {
      svg.on('.zoom', null);
    };
  }, []);

  // Node map for edge rendering
  const nodeMap = new Map(simulationNodes.map(n => [n.id, n]));

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="bg-slate-900"
      style={{ cursor: 'grab' }}
    >
      <defs>
        {/* Grid pattern background */}
        <pattern
          id="grid-pattern"
          width="40"
          height="40"
          patternUnits="userSpaceOnUse"
        >
          <path
            d="M 40 0 L 0 0 0 40"
            fill="none"
            stroke="#1E293B"
            strokeWidth="0.5"
            opacity="0.5"
          />
        </pattern>

        {/* Dot grid pattern (subtle) */}
        <pattern
          id="dot-grid"
          width="20"
          height="20"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="10" cy="10" r="0.5" fill="#334155" opacity="0.4" />
        </pattern>

        {/* Animated dash keyframes for fraud ring edges */}
        <style>
          {`
            @keyframes edgeMarch {
              to { stroke-dashoffset: -20; }
            }
            @keyframes slide-in {
              from { transform: translateX(100%); opacity: 0; }
              to { transform: translateX(0); opacity: 1; }
            }
            .animate-slide-in {
              animation: slide-in 0.3s ease-out;
            }
          `}
        </style>
      </defs>

      {/* Background layers */}
      <rect width={width} height={height} fill="#0f172a" />
      <rect width={width} height={height} fill="url(#grid-pattern)" />
      <rect width={width} height={height} fill="url(#dot-grid)" />

      {/* Simulation activity indicator */}
      {isSimulating && (
        <g transform={`translate(${width - 120}, 20)`}>
          <rect
            x={0}
            y={0}
            width={100}
            height={24}
            rx={12}
            fill="rgba(15, 23, 42, 0.9)"
            stroke="#334155"
            strokeWidth={0.5}
          />
          <circle cx={16} cy={12} r={3} fill="#38bdf8">
            <animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite" />
          </circle>
          <text x={26} y={16} fill="#94a3b8" fontSize="10" fontFamily="JetBrains Mono, monospace">
            Simulating...
          </text>
        </g>
      )}

      {/* Graph content group (transformed by zoom/pan) */}
      <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>
        {/* Render edges */}
        <g className="edges">
          {simulationEdges.map(edge => {
            const sourceNode = typeof edge.source === 'object' ? edge.source : nodeMap.get(edge.source);
            const targetNode = typeof edge.target === 'object' ? edge.target : nodeMap.get(edge.target);

            return (
              <GraphEdge
                key={edge.id}
                edge={edge}
                sourceNode={sourceNode}
                targetNode={targetNode}
                onClick={onEdgeClick}
              />
            );
          })}
        </g>

        {/* Render nodes */}
        <g className="nodes">
          {simulationNodes.map(node => (
            <g key={node.id} transform={`translate(${node.x || 0},${node.y || 0})`}>
              <GraphNode
                node={node}
                onClick={onNodeClick}
                isSelected={node.id === selectedNodeId}
              />
            </g>
          ))}
        </g>
      </g>
    </svg>
  );
});

ForceGraph.displayName = 'ForceGraph';

export default ForceGraph;
