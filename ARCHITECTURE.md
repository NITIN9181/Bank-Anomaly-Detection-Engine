# Architecture Decision Record

## System Overview

The Bank Anomaly Detection Engine is an autonomous, AI-native reconciliation system that ingests synthetic banking data, detects anomalies via dual-layer ML, explains flags with an LLM, and visualizes results in real-time.

## Component Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Plaid Sandbox │────▶│   Ingestion     │────▶│   SQLite        │
│   (Test Data)   │     │   (APScheduler) │     │   (Transactions)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                        ┌─────────────────┐              │
                        │   Feature Eng   │◄─────────────┘
                        │   (Pandas)      │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   Vendor Profiles│
                        │   (SQLite)       │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   Anomaly       │
                        │   Detector      │
                        │   (Sklearn)     │
                        └─────────────────┘
                                │
┌─────────────────┐     ┌─────────────────┐
│   LLM Explainer │────▶│ Explainability  │
│   (NVIDIA NIM)  │     │ 2.0 Engine      │
└─────────────────┘     └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   Anomalies     │
                        │   (SQLite)      │
                        └─────────────────┘
                                │
┌─────────────────┐     ┌─────────────────┐
│   FastAPI       │◄────│   React         │
│   (REST API)    │     │   Dashboard     │
└─────────────────┘     └─────────────────┘
```

## Data Flow

1. **Ingestion**: APScheduler polls Plaid Sandbox every 120 seconds
2. **Storage**: Raw transactions stored in SQLite with deduplication by `plaid_transaction_id`
3. **Feature Engineering**: Rolling 6-month mean/std computed per vendor via Pandas
4. **Detection**: Dual-layer approach:
   - Layer 1: Statistical — Z-Score > 3.0 for clear deviations
   - Layer 2: ML — Isolation Forest for structural anomalies
   - Layer 3: Duplicate — 24-hour window matching
5. **Explanation**: NVIDIA NIM generates natural language descriptions, enriched by the Explainability 2.0 engine (Confidence, Feature Contributions, Recommendations).
6. **Serving**: FastAPI exposes REST endpoints with pagination, and specific `/explain` routes.
7. **Visualization**: React dashboard polls every 5 seconds for real-time updates and presents interactive What-If simulators.

## Technology Decisions

| Decision | Choice | Rationale | Trade-off |
|----------|--------|-----------|-----------| 
| ML Algorithm | Isolation Forest | Unsupervised, no labels needed | Less precise than supervised for known patterns |
| Statistical Layer | Rolling Z-Score | Transparent, interpretable threshold | Misses non-volumetric anomalies |
| LLM | dracarys-llama-3.1-70b | Free endpoint, validated concise output | Rate limits on free tier |
| Database | SQLite | Zero config, survives on Render disk | No concurrent writes, ~50k row limit |
| Backend Framework | FastAPI | Async-native, automatic OpenAPI docs | Smaller ecosystem than Django |
| Frontend Design | Stitch MCP | AI-generated components, rapid iteration | Less control than hand-crafted CSS |
| Deployment | Render + Vercel | Free tier, Git-based deploys | Cold starts on free tier |

## Scaling Path

| Current State | Bottleneck | Next Step | Effort |
|---------------|-----------|-----------|--------|
| SQLite | Concurrent writes | PostgreSQL on Render ($7/mo) | 2 hours |
| Polling | Real-time latency | WebSockets / Server-Sent Events | 4 hours |
| Single user | Demo only | JWT auth + user isolation | 6 hours |
| In-memory model | Cold start | Model persistence + warm pools | 3 hours |
| Single instance | Throughput | Docker + horizontal scaling | 8 hours |

## Security Considerations

- API keys stored as environment variables, never in code
- CORS restricted to known frontend domains
- No PII logged (only `transaction_id` and `amount`)
- SQLite file on persistent disk survives redeploys
- Fallback explanations prevent LLM API exposure

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Ingestion batch | <5s for 100 txns | ~2s |
| Detection latency | <1s per batch | ~0.5s |
| LLM explanation | <2s end-to-end | ~1.5s |
| Dashboard TTFB | <3s | ~2s (after cold start) |
| Polling interval | 5s | 5s |

## Monitoring & Observability

- Health check endpoint: `GET /api/v1/health`
- Render uptime monitoring via health check path
- UptimeRobot free tier for external ping (optional)
- Frontend error boundary for React crashes
- API error logging with structured JSON

## Known Limitations

1. **Render cold start**: Free tier spins down after 15 min inactivity. First request takes ~30s.
2. **NVIDIA rate limits**: Free endpoint has daily quotas. Fallback templates ensure 100% availability.
3. **Plaid Sandbox data**: Synthetic transactions may not trigger anomalies naturally. Manual injection supported for demos.
4. **SQLite concurrency**: Single-writer limitation. Not suitable for multi-user production.
5. **No authentication**: Demo project. Add JWT + role-based access for production.

## Future Enhancements

- [ ] PostgreSQL migration for concurrent analytics
- [ ] WebSocket streaming replacing polling
- [ ] User authentication with role-based views
- [ ] Anomaly resolution workflow (mark resolved / false positive)
- [ ] Batch CSV upload for offline reconciliation
- [ ] Slack/email notifications for critical anomalies
- [ ] Model versioning and A/B testing
- [ ] Automated retraining pipeline

## References

- [Plaid API Documentation](https://plaid.com/docs/)
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Stitch MCP](https://stitch.withgoogle.com/)
- [DualEntry Careers](https://dualentry.com/careers)
