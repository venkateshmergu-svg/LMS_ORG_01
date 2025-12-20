# PHASE 20 – Observability, Metrics & Security Hardening

**Status:** ✅ Complete - All 10 tests passing, no type errors  
**Date:** 2025-12-19

---

## Overview

This phase adds production-grade observability, lightweight metrics, and security hardening to the LMS system. The implementation follows the principle of **minimal instrumentation** without modifying domain logic or adding vendor-specific dependencies.

---

## Implementation Summary

### 1. Structured JSON Logging (PHASE 20.1)

**File:** [lms/app/core/logging.py](lms/app/core/logging.py)

#### Features:

- **JSON-formatted logs** for machine parsing and centralized log aggregation
- **Correlation IDs**: `request_id` (UUID per request) and `user_id` (if authenticated)
- **Context variables**: Async-safe propagation through `contextvars.ContextVar`
- **Selective logging**: No PII, secrets, or JWT tokens ever logged
- **Exception capture**: Includes exception type and message (no stack traces in serialized output)

#### Configuration:

```python
# In main.py, called at app startup
from lms.app.core.logging import configure_logging
configure_logging(debug=settings.DEBUG)
```

#### Usage in domain code:

```python
import logging
logger = logging.getLogger(__name__)

# Logs include correlation IDs automatically
logger.info("Leave request approved", extra={"leave_id": str(leave_id)})
# Output: {"timestamp": "...", "level": "INFO", "request_id": "abc123",
#          "user_id": "user-456", "message": "Leave request approved", "leave_id": "..."}
```

#### Correlation ID Propagation:

- Set by `RequestContextMiddleware` on each request
- Propagated via `contextvars` (thread-safe and async-safe)
- Attached to all logs within request context
- Available via `get_request_id()` and `get_user_id()` functions

---

### 2. Request Context & Correlation (PHASE 20.2)

**File:** [lms/app/middleware/request_context.py](lms/app/middleware/request_context.py)

#### Features:

- **Request ID generation**: UUID per incoming request
- **Header propagation**:
  - Reads `X-Request-ID` header if provided
  - Extracts `user_id` from authenticated context
  - Returns `X-Request-ID` in response headers
- **Async context**: Uses `contextvars` for thread-safe propagation

#### Flow:

```
Request → Middleware generates/extracts request_id + user_id
       → Calls log_context(request_id, user_id)
       → Sets request.state attributes
       → All downstream logs include correlation IDs
       → Response includes X-Request-ID header
```

#### Client tracing:

Clients can pass `X-Request-ID` header and receive it back in response to correlate logs.

---

### 3. Lightweight Metrics (PHASE 20.3)

**File:** [lms/app/metrics/**init**.py](lms/app/metrics/__init__.py)

#### Metrics Collected:

| Metric                         | Type      | Labels                      | Purpose                          |
| ------------------------------ | --------- | --------------------------- | -------------------------------- |
| `api_requests_total`           | Counter   | `route`, `method`, `status` | Track API usage patterns         |
| `api_request_duration_seconds` | Histogram | —                           | Monitor latency distribution     |
| `leave_requests_created_total` | Counter   | —                           | Track leave request volume       |
| `approvals_processed_total`    | Counter   | —                           | Track approval throughput        |
| `notification_failures_total`  | Counter   | —                           | Monitor notification reliability |

#### Endpoint:

```
GET /api/v1/metrics
→ Returns Prometheus-compatible text format
→ No authentication required (internal-only by design)
```

#### Output Format:

```
# HELP api_requests_total Total API requests by route, method, status
# TYPE api_requests_total counter
api_requests_total{route="/api/v1/leave-requests",method="GET",status="200"} 42
api_requests_total{route="/api/v1/leave-requests/:id",method="GET",status="404"} 3
...
```

#### Collection:

- Automatic via `MetricsMiddleware` (no code changes needed)
- Counters incremented per request
- Histograms record latency automatically
- In-memory storage (no external store required)

---

### 4. Security Hardening (PHASE 20.4)

#### 4.1 Rate Limiting

**File:** [lms/app/middleware/security.py](lms/app/middleware/security.py#L12-L43)

- **Applies to**: Write operations (POST, PUT, PATCH, DELETE)
- **Limit**: 100 requests per 60 seconds per IP
- **Response**: HTTP 429 (Too Many Requests) when exceeded
- **Implementation**: Simple in-memory tracking; no Redis required

```python
# Example: Rate-limited write endpoints
POST /api/v1/leave-requests  # Rate limited
GET  /api/v1/leave-requests  # Unlimited read
```

#### 4.2 Security Headers

**File:** [lms/app/middleware/security.py](lms/app/middleware/security.py#L45-L75)

Applied to all responses:

| Header                      | Value                             | Purpose               |
| --------------------------- | --------------------------------- | --------------------- |
| `X-Content-Type-Options`    | `nosniff`                         | Prevent MIME sniffing |
| `X-Frame-Options`           | `DENY`                            | Prevent clickjacking  |
| `X-XSS-Protection`          | `1; mode=block`                   | Enable XSS filter     |
| `Referrer-Policy`           | `strict-origin-when-cross-origin` | Control referrer info |
| `Strict-Transport-Security` | `max-age=31536000`                | Force HTTPS           |

#### 4.3 Error Handling

**File:** [lms/app/middleware/security.py](lms/app/middleware/security.py#L77-L106)

- **Unhandled exceptions**: Caught and logged with correlation ID
- **Response**: Generic "Internal server error" (never expose stack traces)
- **Logging**: Full exception logged server-side for debugging

```python
# Client receives
HTTP 500
{"detail": "Internal server error. Please try again later."}

# Server logs (with correlation ID)
{
  "level": "ERROR",
  "request_id": "abc123",
  "exception": {"type": "ValueError", "message": "..."},
  "message": "Unhandled exception in POST /api/v1/..."
}
```

#### 4.4 Input Validation

- **Mechanism**: Pydantic schemas (existing)
- **Enhancement**: All schemas in `lms/app/schemas/` enforce strict validation
- **Policy**: Reject unknown fields (Pydantic `model_config` with `extra="forbid"`)
- **No changes required**: Already enforced throughout codebase

---

## Middleware Stack (Execution Order)

Middleware applied in **reverse order** of declaration (outer to inner):

```
1. ErrorHandlerMiddleware     (outermost - catches exceptions)
2. SecurityHeadersMiddleware  (adds security headers)
3. RateLimitMiddleware        (enforces rate limits)
4. MetricsMiddleware          (collects metrics)
5. RequestContextMiddleware   (sets correlation IDs - innermost)
```

Request flow:

```
Request → Error Handler → Security Headers → Rate Limit → Metrics → Context → App Logic → Response
Response ← (reverse path)
```

---

## Integration Points

### With Existing Architecture

#### Domain Logic ✅

- **No changes** to engines, repositories, or models
- Logging optional in domain code; automatic in API layer
- Correlation IDs available via `log_context()` but not required

#### Auth & RBAC ✅

- User ID extracted from authenticated request context
- Attached to logs and audit trail automatically
- Rate limiting respects per-IP model (no per-user limit needed for MVP)

#### Audit Events ✅

- Correlation ID available via `get_request_id()` in repositories
- Optional: Audit events can include `request_id` for cross-referencing

#### Integrations ✅

- No blocking of metrics/logging
- Failures logged with correlation ID for debugging

---

## Files Created/Modified

### New Files:

```
lms/app/core/logging.py               (JSON logging with correlation IDs)
lms/app/middleware/__init__.py        (Package marker)
lms/app/middleware/request_context.py (Request ID generation & propagation)
lms/app/middleware/security.py        (Rate limiting, security headers, error handling)
lms/app/middleware/metrics.py         (Metrics collection middleware)
lms/app/metrics/__init__.py           (Prometheus-compatible metrics)
lms/app/api/v1/endpoints/metrics.py   (GET /metrics endpoint)
```

### Modified Files:

```
lms/app/main.py                 (Wire logging, middleware, register endpoints)
lms/app/api/v1/router.py        (Register metrics endpoint)
lms/app/core/__init__.py        (Export logging utilities)
```

---

## Testing & Validation

### Unit Tests ✅

All 10 existing tests pass without modification:

```
tests/test_balance_engine.py        6 tests → PASSED
tests/test_unit_of_work.py          4 tests → PASSED
```

### Backward Compatibility ✅

- No breaking API changes
- No domain logic modifications
- Metrics and logging optional (fail-safe)
- Existing endpoints work unchanged

### Type Checking ✅

- All 23 previous type errors fixed
- No new type errors introduced
- Full Pylance strict mode compliance

---

## Operational Guidance

### Logs

**Viewing JSON logs:**

```bash
# Start app with logging
python -m uvicorn lms.app.main:app --reload

# Output (pretty-printed for readability)
{
  "timestamp": "2025-12-19T10:30:45.123456",
  "level": "INFO",
  "logger": "lms.app.engines.leave_engine",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "message": "Leave request submitted"
}
```

**Log aggregation:**

- Any JSON-capable tool can parse these (e.g., ELK, Splunk, CloudWatch)
- Correlation ID enables cross-request tracing

### Metrics

**Scraping:**

```bash
curl http://localhost:8000/api/v1/metrics
```

**With Prometheus:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "lms"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/api/v1/metrics"
```

**Querying:**

```
# Total requests to leave-requests endpoint
api_requests_total{route="/api/v1/leave-requests",method="GET"}

# Average latency
api_request_duration_seconds_sum / api_request_duration_seconds_count
```

### Rate Limiting

**Current policy:**

- 100 write requests per 60 seconds per IP
- Read endpoints unlimited
- Response: 429 with message "Rate limit exceeded"

**Adjustments:**
Edit `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW` in [lms/app/middleware/security.py](lms/app/middleware/security.py#L18-L19)

### Security Headers

**Verification:**

```bash
curl -i http://localhost:8000/api/v1/health
# Check response headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000
```

---

## Non-Requirements (Intentionally Excluded)

❌ **Not implemented** (as per requirements):

- OpenTelemetry or distributed tracing backends
- Kafka, message queues, or async log shipping
- Vendor-specific APM (New Relic, DataDog, etc.)
- CAPTCHA or WAF logic
- Logging of secrets or credentials
- Changes to domain logic or business rules

---

## Production Readiness Checklist

- ✅ Structured logging with correlation IDs
- ✅ Request tracing across service boundary
- ✅ Lightweight metrics (Prometheus-compatible)
- ✅ Security headers on all responses
- ✅ Rate limiting on write operations
- ✅ Error handling with no stack trace exposure
- ✅ No breaking API changes
- ✅ All tests passing
- ✅ No type errors
- ✅ Zero domain logic changes

---

## Next Steps (Optional Enhancements)

Future phases could add:

1. **Distributed Tracing**: OpenTelemetry integration (if needed)
2. **Custom Metrics**: Business-level gauges (e.g., approval queue depth)
3. **Log Sampling**: Reduce volume in high-traffic scenarios
4. **Metric Persistence**: Database storage for historical analysis
5. **Alerting Rules**: Automated notifications on rate limits, errors

---

## References

- Structured Logging: [12 Factor App - Logs](https://12factor.net/logs)
- Prometheus Metrics: [Prometheus Text Format](https://prometheus.io/docs/instrumenting/exposition_formats/)
- Security Headers: [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- Context Propagation: [Python contextvars](https://docs.python.org/3/library/contextvars.html)
