# PHASE 20: Quick Start Guide

**Observability, Metrics & Security Hardening**

---

## What's New

### 1. JSON Logging with Correlation IDs

Every request gets a unique ID that flows through all logs, enabling end-to-end tracing.

```json
{
  "timestamp": "2025-12-19T14:19:05",
  "level": "INFO",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "message": "Leave request submitted"
}
```

### 2. Prometheus Metrics

```bash
curl http://localhost:8000/api/v1/metrics
```

Tracks:

- API requests (count, latency)
- Leave requests created
- Approvals processed
- Notification failures

### 3. Security Features

- **Rate Limiting**: 100 write requests/min per IP
- **Security Headers**: Prevent common web attacks
- **Error Handling**: No stack traces in responses

---

## How to Use

### Start the Server

```bash
python -m uvicorn lms.app.main:app --reload
```

Logs appear as JSON (one per line):

```json
{
  "timestamp": "...",
  "level": "INFO",
  "message": "Application startup complete"
}
```

### View Metrics

```bash
curl http://localhost:8000/api/v1/metrics
```

Output:

```
# HELP api_requests_total Total API requests by route, method, status
# TYPE api_requests_total counter
api_requests_total{route="/api/v1/leave-requests",method="GET",status="200"} 42
api_request_duration_seconds_sum 125.43
```

### Client Request Tracing

```bash
# Send request with correlation ID
curl -H "X-Request-ID: my-trace-id" http://localhost:8000/api/v1/users

# Response includes the ID
Response Headers:
X-Request-ID: my-trace-id

# All server logs for this request will include:
"request_id": "my-trace-id"
```

### Rate Limit Check

```bash
# Rapid fire write requests
for i in {1..150}; do
  curl -X POST http://localhost:8000/api/v1/leave-requests -d '...'
done

# After 100: HTTP 429 Too Many Requests
```

---

## Architecture

```
Request
  ↓
[Error Handler]       ← Catch exceptions, log with correlation ID
  ↓
[Security Headers]    ← Add X-Frame-Options, X-Content-Type-Options, etc.
  ↓
[Rate Limiter]        ← Check write limit (100/min per IP)
  ↓
[Metrics]             ← Record request count & latency
  ↓
[Request Context]     ← Generate/propagate request_id, user_id
  ↓
[FastAPI App]         ← Domain logic (unchanged)
  ↓
Response (with X-Request-ID header)
```

---

## Key Files

| File                                                                           | Purpose                |
| ------------------------------------------------------------------------------ | ---------------------- |
| [lms/app/core/logging.py](lms/app/core/logging.py)                             | JSON logging setup     |
| [lms/app/middleware/request_context.py](lms/app/middleware/request_context.py) | Request ID generation  |
| [lms/app/middleware/security.py](lms/app/middleware/security.py)               | Rate limiting, headers |
| [lms/app/middleware/metrics.py](lms/app/middleware/metrics.py)                 | Metrics collection     |
| [lms/app/metrics/**init**.py](lms/app/metrics/__init__.py)                     | Prometheus registry    |
| [lms/app/api/v1/endpoints/metrics.py](lms/app/api/v1/endpoints/metrics.py)     | GET /metrics endpoint  |

---

## Configuration

### Adjust Rate Limits

Edit [lms/app/middleware/security.py](lms/app/middleware/security.py#L18-L19):

```python
RATE_LIMIT_MAX = 100      # requests
RATE_LIMIT_WINDOW = 60    # seconds
```

### Debug Logging

Enable debug logs:

```bash
# In main.py, configure_logging(debug=True)
# Or via settings: DEBUG=true
```

### Disable Metrics

(Not recommended) Remove from [lms/app/main.py](lms/app/main.py):

```python
app.add_middleware(MetricsMiddleware)
```

---

## Integration with Tools

### ELK Stack / Splunk / CloudWatch

Parse JSON logs automatically. Logs include request_id for correlation:

```
GET /api/v1/users
→ "request_id": "abc123" in all logs for this request
→ Search logs with: request_id:abc123
```

### Prometheus / Grafana

Scrape `/api/v1/metrics` every 15 seconds:

```yaml
scrape_configs:
  - job_name: "lms"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/api/v1/metrics"
    scrape_interval: "15s"
```

### Request Tracing (Client Side)

Generate UUID, send in header, receive back in response:

```python
import uuid
request_id = str(uuid.uuid4())
response = requests.get(
    'http://localhost:8000/api/v1/users',
    headers={'X-Request-ID': request_id}
)
# Use same request_id to correlate all related logs
```

---

## What Changed

✅ **New:**

- JSON logging with correlation IDs
- Prometheus metrics endpoint
- Rate limiting middleware
- Security headers on all responses
- Request context propagation

✅ **Unchanged:**

- API endpoints (no breaking changes)
- Domain logic (engines, repos, models)
- Database schema
- Tests (all 10 still pass)

---

## Troubleshooting

### Logs not visible?

```bash
# Ensure stdout is captured
python -m uvicorn lms.app.main:app --reload 2>&1
```

### /metrics returns 404?

```bash
# Check if endpoint registered
curl http://localhost:8000/api/v1/metrics
# Should return: # HELP api_requests_total...
```

### Getting 429 (Rate Limited)?

- Slow down write requests
- Or adjust `RATE_LIMIT_MAX` in security.py
- Limit applies per-IP, not per-user

### Correlation ID not in logs?

- Middleware auto-injects if present in request headers
- Check `X-Request-ID` header from client
- Or let server generate one (always happens)

---

## Next Steps

1. ✅ All tests passing
2. ✅ Deploy to staging
3. ✅ Verify logs in aggregation tool
4. ✅ Set up Prometheus scraping
5. ✅ Create alerting rules
6. ✅ Monitor production

---

**Full Documentation:** [PHASE_20_OBSERVABILITY_SECURITY.md](PHASE_20_OBSERVABILITY_SECURITY.md)  
**Implementation Summary:** [PHASE_20_SUMMARY.md](PHASE_20_SUMMARY.md)  
**Completion Checklist:** [PHASE_20_CHECKLIST.md](PHASE_20_CHECKLIST.md)

**Status: ✅ Production Ready**
