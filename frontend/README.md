# Bank Anomaly Detection Engine - Frontend

React dashboard for real-time anomaly monitoring and visualization.

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first styling
- **Recharts** - Chart library for trend visualization
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Stitch MCP generated UI components
│   │   ├── TransactionFeed.jsx
│   │   ├── AnomalyCard.jsx
│   │   ├── TrendModal.jsx
│   │   ├── StatsBar.jsx
│   │   └── Layout.jsx
│   ├── hooks/
│   │   └── useInterval.js   # Custom polling hook
│   ├── services/
│   │   └── api.js           # Axios API client
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles + Tailwind
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── vercel.json              # Vercel deployment config
```

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Update .env with your backend URL
# VITE_API_URL=http://localhost:8000/api/v1
```

### Development

```bash
# Start dev server (http://localhost:3000)
npm run dev
```

The dev server includes:
- Hot module replacement (HMR)
- API proxy to backend (avoids CORS issues)
- Source maps for debugging

### Build

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

## Stitch MCP Components

Five core UI components are generated via Google Stitch MCP. See `src/components/README.md` for:
- Exact prompts to use in Stitch
- Expected prop interfaces
- Integration guidelines

## Features

### Real-Time Polling

- **Anomalies**: 5-second interval (real-time feel)
- **Stats**: 10-second interval (KPI updates)
- **Transactions**: 30-second interval (background refresh)

### Browser Notifications

- Tab title flashes when new anomaly detected
- Auto-resets after 3 seconds

### Vendor Trend Analysis

- Click "View Trend" on any anomaly card
- Modal displays 6-month transaction history
- Recharts line graph with anomaly point highlighted
- Rolling average overlay (dashed line)

### Manual Detection Trigger

- "Run Detection" button in action bar
- Triggers backend `/detect` endpoint
- Refreshes all data after completion

### Error Handling

- Toast notifications for API failures
- Graceful degradation on network errors
- Loading states for async operations

## Design System

### Colors (Tailwind Config)

```javascript
anomaly: {
  volumetric: "#EF4444",   // red-500
  deviant: "#F59E0B",      // amber-500
  duplicate: "#8B5CF6",    // violet-500
}
finance: {
  bg: "#0F172A",           // slate-900
  card: "#1E293B",         // slate-800
  text: "#F8FAFC",         // slate-50
  muted: "#94A3B8",        // slate-400
}
```

### Typography

- **Body**: Inter (Google Fonts)
- **Monospace**: Fira Code (amounts, IDs)

### Animations

- **Slide-in**: Anomaly cards enter from right
- **Pulse-dot**: Status indicators
- **Shimmer**: Loading skeleton states

## API Integration

### Endpoints

| Method | Endpoint | Usage |
|--------|----------|-------|
| GET | `/transactions` | Fetch transaction list |
| GET | `/anomalies` | Fetch flagged anomalies |
| GET | `/stats` | Fetch dashboard KPIs |
| POST | `/detect` | Trigger detection pipeline |

### API Client (`src/services/api.js`)

- Axios instance with base URL from env
- Request/response interceptors for logging
- Error handling with console output

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

Environment variables in Vercel dashboard:
- `VITE_API_URL`: Your backend URL (e.g., `https://your-api.onrender.com/api/v1`)

### Manual Build

```bash
npm run build
# Upload dist/ folder to any static host
```

## Development Notes

### Vite vs Create React App

This project uses Vite instead of CRA for:
- Faster dev server startup
- Instant HMR
- Smaller bundle sizes
- Native ESM support

**Key differences:**
- Environment variables use `VITE_` prefix (not `REACT_APP_`)
- Access via `import.meta.env.VITE_API_URL`

### Responsive Breakpoints

- **Mobile**: < 640px (1 column)
- **Tablet**: 640px - 1024px (2 columns)
- **Desktop**: > 1024px (5-column grid: 3 for feed, 2 for anomalies)

### Custom Hooks

**`useInterval(callback, delay)`**
- Declarative setInterval with cleanup
- Pauses when `delay` is `null`
- Prevents stale closure issues

## Troubleshooting

### CORS Errors

If you see CORS errors in console:
1. Check backend CORS middleware allows your frontend origin
2. Use Vite proxy in development (already configured)
3. In production, update backend `origins` list

### API Connection Failed

1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check `.env` file has correct `VITE_API_URL`
3. Check browser console for detailed error messages

### Components Not Rendering

1. Ensure all 5 Stitch components are generated and saved
2. Check component exports are `export default`
3. Verify prop interfaces match expected structure

## License

MIT
