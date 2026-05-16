import { memo, useState, useMemo } from 'react';

/**
 * SVG-based graph edge component for financial transaction flows.
 * 
 * Stitch Design System: Technical Risk Intelligence
 * 
 * Edge styles: solid (normal), dashed (suspicious), animated dash (active fraud ring)
 * Width proportional to transaction volume (log scale)
 * Color gradient from source node color to target node color
 * Features: arrowhead, hover tooltip with transaction count and velocity score
 */
const GraphEdge = memo(({ edge, sourceNode, targetNode, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  if (!sourceNode || !targetNode) return null;

  // Calculate edge width based on transaction count (log scale)
  const weight = edge.transaction_count > 0 ? Math.log10(edge.transaction_count + 1) : 0;
  const strokeWidth = Math.min(Math.max(1 + weight * 2, 1), 6);

  // Risk color mapping
  const getRiskColor = (riskScore) => {
    if (riskScore >= 0.8) return '#EF4444';
    if (riskScore >= 0.6) return '#F97316';
    if (riskScore >= 0.3) return '#F59E0B';
    return '#10B981';
  };

  const getNodeRiskColor = (node) => {
    if (!node) return '#64748B';
    return getRiskColor(node.risk_score || 0);
  };

  const sourceColor = getNodeRiskColor(sourceNode);
  const targetColor = getNodeRiskColor(targetNode);
  const edgeColor = getRiskColor(edge.risk_score || 0);

  // Edge state
  const isSuspicious = edge.anomaly_flags && edge.anomaly_flags.length > 0;
  const isFraudRing = edge.risk_score >= 0.8;

  // Calculate positions
  const x1 = sourceNode.x || 0;
  const y1 = sourceNode.y || 0;
  const x2 = targetNode.x || 0;
  const y2 = targetNode.y || 0;

  // Unique gradient ID for this edge
  const gradientId = useMemo(() => `edge-grad-${edge.id}`, [edge.id]);
  const markerId = useMemo(() => `arrow-${edge.id}`, [edge.id]);

  // Calculate curved path (slight Bézier curve for visual clarity)
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const curvature = Math.min(dist * 0.15, 30);

  // Perpendicular offset for curve
  const nx = -dy / (dist || 1);
  const ny = dx / (dist || 1);

  const cx = (x1 + x2) / 2 + nx * curvature;
  const cy = (y1 + y2) / 2 + ny * curvature;

  const pathD = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;

  // Arrowhead position (at ~75% of the path to avoid node overlap)
  const t = 0.75;
  const arrowX = (1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * cx + t * t * x2;
  const arrowY = (1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * cy + t * t * y2;

  // Tangent at arrowhead position for rotation
  const tangentX = 2 * (1 - t) * (cx - x1) + 2 * t * (x2 - cx);
  const tangentY = 2 * (1 - t) * (cy - y1) + 2 * t * (y2 - cy);
  const angle = Math.atan2(tangentY, tangentX) * 180 / Math.PI;

  // Tooltip position (midpoint of curve)
  const tooltipX = (x1 + x2) / 2 + nx * curvature * 0.5;
  const tooltipY = (y1 + y2) / 2 + ny * curvature * 0.5;

  // Dash pattern
  const getDashArray = () => {
    if (isFraudRing) return '6,4';
    if (isSuspicious) return '8,6';
    return 'none';
  };

  return (
    <g
      onClick={() => onClick && onClick(edge)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="cursor-pointer"
    >
      {/* Gradient definition */}
      <defs>
        <linearGradient id={gradientId} x1={x1} y1={y1} x2={x2} y2={y2} gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor={sourceColor} stopOpacity={0.8} />
          <stop offset="100%" stopColor={targetColor} stopOpacity={0.8} />
        </linearGradient>
        <marker
          id={markerId}
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill={edgeColor} opacity={0.9} />
        </marker>
      </defs>

      {/* Invisible hit area for easier interaction */}
      <path
        d={pathD}
        fill="none"
        stroke="transparent"
        strokeWidth={Math.max(strokeWidth + 12, 16)}
        style={{ pointerEvents: 'stroke' }}
      />

      {/* Hover glow effect */}
      {isHovered && (
        <path
          d={pathD}
          fill="none"
          stroke={edgeColor}
          strokeWidth={strokeWidth + 4}
          opacity={0.15}
          style={{ filter: 'blur(3px)' }}
        />
      )}

      {/* Main path */}
      <path
        d={pathD}
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth={isHovered ? strokeWidth + 1 : strokeWidth}
        strokeDasharray={getDashArray()}
        opacity={isHovered ? 0.9 : 0.55}
        style={{
          transition: 'opacity 0.2s, stroke-width 0.2s',
          ...(isFraudRing ? {
            animation: 'edgeMarch 0.8s linear infinite',
          } : {}),
        }}
      />

      {/* Arrowhead */}
      <polygon
        points="0,-4 8,0 0,4"
        fill={edgeColor}
        opacity={isHovered ? 0.95 : 0.7}
        transform={`translate(${arrowX},${arrowY}) rotate(${angle})`}
        style={{ transition: 'opacity 0.2s' }}
      />

      {/* Rich tooltip on hover */}
      {isHovered && (
        <foreignObject
          x={tooltipX + 10}
          y={tooltipY - 50}
          width={190}
          height={100}
          className="pointer-events-none"
        >
          <div
            xmlns="http://www.w3.org/1999/xhtml"
            style={{
              background: 'rgba(15, 23, 42, 0.95)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(71, 85, 105, 0.6)',
              borderRadius: '8px',
              padding: '10px 12px',
              fontFamily: 'Geist, Inter, system-ui, sans-serif',
              boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: '600', color: '#f8fafc', marginBottom: '6px' }}>
              Transaction Flow
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', fontSize: '10px' }}>
              <div style={{ color: '#94a3b8' }}>Transactions</div>
              <div style={{ color: '#cbd5e1', fontFamily: 'JetBrains Mono, monospace', textAlign: 'right' }}>
                {edge.transaction_count}
              </div>
              <div style={{ color: '#94a3b8' }}>Volume</div>
              <div style={{ color: '#cbd5e1', fontFamily: 'JetBrains Mono, monospace', textAlign: 'right' }}>
                ${(edge.total_amount || 0).toLocaleString()}
              </div>
              <div style={{ color: '#94a3b8' }}>Velocity</div>
              <div style={{ color: '#cbd5e1', fontFamily: 'JetBrains Mono, monospace', textAlign: 'right' }}>
                {((edge.velocity_score || 0) * 100).toFixed(0)}%
              </div>
              {edge.time_clustered_txns > 0 && (
                <>
                  <div style={{ color: '#f59e0b' }}>⚡ Clustered</div>
                  <div style={{ color: '#f59e0b', fontFamily: 'JetBrains Mono, monospace', textAlign: 'right' }}>
                    {edge.time_clustered_txns}
                  </div>
                </>
              )}
            </div>
            {edge.anomaly_flags && edge.anomaly_flags.length > 0 && (
              <div style={{ marginTop: '6px', paddingTop: '6px', borderTop: '1px solid rgba(71, 85, 105, 0.4)' }}>
                {edge.anomaly_flags.map((flag, i) => (
                  <span key={i} style={{
                    display: 'inline-block',
                    padding: '1px 5px',
                    marginRight: '3px',
                    borderRadius: '4px',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    color: '#f87171',
                    fontSize: '9px',
                    fontWeight: '600',
                  }}>
                    {flag.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            )}
          </div>
        </foreignObject>
      )}
    </g>
  );
});

GraphEdge.displayName = 'GraphEdge';

export default GraphEdge;
