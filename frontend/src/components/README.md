# Stitch MCP Generated Components

This directory contains 5 React components generated via Google Stitch MCP.

## Components to Generate

Run the prompts from Phase 3 Part A in Stitch MCP and save the generated code to these files:

1. **TransactionFeed.jsx** - Financial transaction table with status indicators
2. **AnomalyCard.jsx** - Anomaly display card with explanation and trend button
3. **TrendModal.jsx** - Modal with Recharts line graph for vendor trends
4. **StatsBar.jsx** - KPI dashboard with 4 stat cards
5. **Layout.jsx** - Main dashboard layout shell with navbar and footer

## Expected Props

### TransactionFeed.jsx
```javascript
{
  transactions: Array<{
    id: number;
    date: string;
    merchant_name: string;
    amount: number;
    status: 'normal' | 'flagged';
  }>;
  isLoading: boolean;
}
```

### AnomalyCard.jsx
```javascript
{
  anomaly: {
    id: number;
    transaction: {
      id: number;
      amount: number;
      date: string;
      merchant_name: string;
    };
    anomaly_type: 'volumetric' | 'deviant_pattern' | 'duplicate';
    z_score: number | null;
    isolation_score: number | null;
    explanation: string;
    detected_at: string;
    status: string;
  };
  onViewTrend: () => void;
}
```

### TrendModal.jsx
```javascript
{
  isOpen: boolean;
  onClose: () => void;
  vendorData: Array<{ date: string; amount: number }>;
  anomalyPoint: { date: string; amount: number } | null;
}
```

### StatsBar.jsx
```javascript
{
  stats: {
    total_transactions: number;
    total_anomalies: number;
    flag_rate_percent: number;
    top_anomalous_vendor: string | null;
  };
}
```

### Layout.jsx
```javascript
{
  children: React.ReactNode;
}
```

## Integration Notes

- All components should export as default: `export default ComponentName`
- Use TailwindCSS classes from `tailwind.config.js` (anomaly.*, finance.*)
- Dark theme throughout (slate-900 bg, slate-800 cards)
- Responsive breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Include animations: slide-in, pulse-dot, shimmer (defined in index.css)
