import { memo, useState } from 'react';

/**
 * SVG-based graph node component for financial network visualization.
 * 
 * Stitch Design System: Technical Risk Intelligence
 * 
 * Node types: Person (circle), Business (square), Account (rounded rect)
 * Color by risk: green (#10B981), yellow (#F59E0B), orange (#F97316), red (#EF4444)
 * Size proportional to transaction volume
 * Features: hover tooltip, risk score badge, pulse animation for flagged nodes,
 *           halo effect for selected nodes, inner glow on high-risk
 */
const GraphNode = memo(({ node, onClick, isSelected }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Calculate node size based on transaction volume (log scale for better distribution)
  const baseSize = 14;
  const volumeScale = node.total_volume > 0 ? Math.log10(node.total_volume + 1) * 3 : 0;
  const radius = Math.min(Math.max(baseSize + volumeScale, 14), 44);

  // Risk color mapping
  const getRiskColor = (riskScore) => {
    if (riskScore >= 0.8) return '#EF4444'; // Critical
    if (riskScore >= 0.6) return '#F97316'; // High
    if (riskScore >= 0.3) return '#F59E0B'; // Elevated
    return '#10B981'; // Safe
  };

  const getRiskLabel = (riskScore) => {
    if (riskScore >= 0.8) return 'Critical';
    if (riskScore >= 0.6) return 'High';
    if (riskScore >= 0.3) return 'Elevated';
    return 'Safe';
  };

  const getRiskGlowColor = (riskScore) => {
    if (riskScore >= 0.8) return 'rgba(239, 68, 68, 0.4)';
    if (riskScore >= 0.6) return 'rgba(249, 115, 22, 0.3)';
    if (riskScore >= 0.3) return 'rgba(245, 158, 11, 0.2)';
    return 'rgba(16, 185, 129, 0.15)';
  };

  const color = getRiskColor(node.risk_score);
  const glowColor = getRiskGlowColor(node.risk_score);
  const isHighRisk = node.risk_score >= 0.6;

  // Determine shape based on persona/account type
  const renderShape = () => {
    const sharedProps = {
      fill: color,
      fillOpacity: 0.15,
      stroke: color,
      strokeWidth: isSelected ? 2.5 : isHovered ? 2 : 1.5,
      style: { transition: 'all 0.2s ease-out' },
    };

    if (node.persona === 'techstart' || node.account_type === 'business') {
      // Business — Square
      return (
        <rect
          x={-radius}
          y={-radius}
          width={radius * 2}
          height={radius * 2}
          {...sharedProps}
        />
      );
    } else if (node.account_type === 'checking' || node.account_type === 'savings') {
      // Account — Rounded rect
      return (
        <rect
          x={-radius}
          y={-radius}
          width={radius * 2}
          height={radius * 2}
          rx={radius * 0.35}
          ry={radius * 0.35}
          {...sharedProps}
        />
      );
    } else {
      // Person — Circle (default)
      return (
        <circle
          r={radius}
          {...sharedProps}
        />
      );
    }
  };

  // Icon based on account type
  const renderIcon = () => {
    const iconSize = radius * 0.55;
    const iconColor = color;

    if (node.persona === 'techstart' || node.account_type === 'business') {
      // Building icon
      return (
        <g transform={`translate(${-iconSize / 2}, ${-iconSize / 2})`}>
          <rect x={iconSize * 0.1} y={iconSize * 0.3} width={iconSize * 0.8} height={iconSize * 0.7} fill="none" stroke={iconColor} strokeWidth={1.5} rx={1} />
          <line x1={iconSize * 0.35} y1={iconSize * 0.45} x2={iconSize * 0.35} y2={iconSize * 0.6} stroke={iconColor} strokeWidth={1.2} />
          <line x1={iconSize * 0.65} y1={iconSize * 0.45} x2={iconSize * 0.65} y2={iconSize * 0.6} stroke={iconColor} strokeWidth={1.2} />
          <line x1={iconSize * 0.35} y1={iconSize * 0.7} x2={iconSize * 0.35} y2={iconSize * 0.85} stroke={iconColor} strokeWidth={1.2} />
          <line x1={iconSize * 0.65} y1={iconSize * 0.7} x2={iconSize * 0.65} y2={iconSize * 0.85} stroke={iconColor} strokeWidth={1.2} />
        </g>
      );
    } else if (node.account_type === 'checking' || node.account_type === 'savings') {
      // Card/wallet icon
      return (
        <g transform={`translate(${-iconSize / 2}, ${-iconSize / 2})`}>
          <rect x={iconSize * 0.1} y={iconSize * 0.25} width={iconSize * 0.8} height={iconSize * 0.55} fill="none" stroke={iconColor} strokeWidth={1.5} rx={2} />
          <line x1={iconSize * 0.1} y1={iconSize * 0.45} x2={iconSize * 0.9} y2={iconSize * 0.45} stroke={iconColor} strokeWidth={1.2} />
          <circle cx={iconSize * 0.75} cy={iconSize * 0.6} r={iconSize * 0.06} fill={iconColor} />
        </g>
      );
    } else {
      // Person icon
      return (
        <g transform={`translate(${-iconSize / 2}, ${-iconSize / 2})`}>
          <circle cx={iconSize * 0.5} cy={iconSize * 0.3} r={iconSize * 0.18} fill="none" stroke={iconColor} strokeWidth={1.5} />
          <path d={`M${iconSize * 0.2},${iconSize * 0.85} Q${iconSize * 0.2},${iconSize * 0.55} ${iconSize * 0.5},${iconSize * 0.55} Q${iconSize * 0.8},${iconSize * 0.55} ${iconSize * 0.8},${iconSize * 0.85}`} fill="none" stroke={iconColor} strokeWidth={1.5} />
        </g>
      );
    }
  };

  return (
    <g
      onClick={() => onClick && onClick(node)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="cursor-pointer"
      style={{ pointerEvents: 'all' }}
    >
      {/* Selected halo effect */}
      {isSelected && (
        <circle
          r={radius + 10}
          fill="none"
          stroke={color}
          strokeWidth={1}
          opacity={0.3}
          style={{ filter: `drop-shadow(0 0 8px ${glowColor})` }}
        >
          <animate
            attributeName="r"
            values={`${radius + 8};${radius + 14};${radius + 8}`}
            dur="2s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.3;0.15;0.3"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      )}

      {/* Pulse animation for flagged nodes */}
      {node.flagged && !isSelected && (
        <>
          <circle
            r={radius + 4}
            fill="none"
            stroke={color}
            strokeWidth={1.5}
            opacity={0}
          >
            <animate
              attributeName="r"
              values={`${radius};${radius + 16}`}
              dur="1.8s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.5;0"
              dur="1.8s"
              repeatCount="indefinite"
            />
          </circle>
          <circle
            r={radius + 4}
            fill="none"
            stroke={color}
            strokeWidth={1}
            opacity={0}
          >
            <animate
              attributeName="r"
              values={`${radius};${radius + 12}`}
              dur="1.8s"
              begin="0.6s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.3;0"
              dur="1.8s"
              begin="0.6s"
              repeatCount="indefinite"
            />
          </circle>
        </>
      )}

      {/* Background glow for high-risk nodes */}
      {isHighRisk && (
        <circle
          r={radius + 3}
          fill={glowColor}
          stroke="none"
          opacity={isHovered ? 0.5 : 0.25}
          style={{ transition: 'opacity 0.2s', filter: 'blur(4px)' }}
        />
      )}

      {/* Main shape */}
      {renderShape()}

      {/* Inner icon */}
      {renderIcon()}

      {/* Risk score badge (only for elevated+) */}
      {node.risk_score >= 0.3 && (
        <g transform={`translate(${radius * 0.65}, ${-radius * 0.65})`}>
          <circle
            r={radius * 0.28}
            fill={color}
            stroke="#0f172a"
            strokeWidth={1.5}
          />
          <text
            textAnchor="middle"
            dominantBaseline="central"
            fill="#fff"
            fontSize={Math.max(7, radius * 0.22)}
            fontWeight="700"
            fontFamily="JetBrains Mono, monospace"
            className="pointer-events-none select-none"
          >
            {Math.round(node.risk_score * 100)}
          </text>
        </g>
      )}

      {/* Label */}
      <text
        y={radius + 14}
        textAnchor="middle"
        fill={isHovered || isSelected ? '#f8fafc' : '#94a3b8'}
        fontSize="10"
        fontWeight="500"
        fontFamily="Geist, Inter, system-ui, sans-serif"
        className="pointer-events-none select-none"
        style={{ transition: 'fill 0.2s' }}
      >
        {(node.label || '').split(' - ')[0].substring(0, 14)}
      </text>

      {/* Rich tooltip on hover using foreignObject */}
      {isHovered && (
        <foreignObject
          x={radius + 8}
          y={-60}
          width={200}
          height={120}
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
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#f8fafc', marginBottom: '6px' }}>
              {node.label}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <span style={{
                display: 'inline-block',
                padding: '1px 6px',
                borderRadius: '9999px',
                backgroundColor: color,
                color: '#fff',
                fontSize: '9px',
                fontWeight: '700',
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}>
                {getRiskLabel(node.risk_score)}
              </span>
              <span style={{ fontSize: '10px', color: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}>
                {(node.risk_score * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#94a3b8', lineHeight: '1.6' }}>
              <div>Txns: <span style={{ color: '#cbd5e1' }}>{node.transaction_count}</span></div>
              <div>Vol: <span style={{ color: '#cbd5e1' }}>${(node.total_volume || 0).toLocaleString()}</span></div>
              {node.flagged && (
                <div style={{ color: '#f87171', fontWeight: '600', marginTop: '2px' }}>⚠ FLAGGED</div>
              )}
            </div>
          </div>
        </foreignObject>
      )}
    </g>
  );
});

GraphNode.displayName = 'GraphNode';

export default GraphNode;
