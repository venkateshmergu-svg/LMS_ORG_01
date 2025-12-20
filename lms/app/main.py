from fastapi import FastAPI

from .api.v1.router import api_router
from .core.config import get_settings
from .core.logging import configure_logging
from .middleware.metrics import MetricsMiddleware
from .middleware.request_context import RequestContextMiddleware
from .middleware.security import (
    ErrorHandlerMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)

settings = get_settings()

# Configure structured logging
configure_logging(debug=settings.DEBUG)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Add middleware (order matters - they wrap in reverse order)
# 1. Error handling (outermost)
app.add_middleware(ErrorHandlerMiddleware)
# 2. Security headers
app.add_middleware(SecurityHeadersMiddleware)
# 3. Rate limiting
app.add_middleware(RateLimitMiddleware)
# 4. Metrics collection
app.add_middleware(MetricsMiddleware)
# 5. Request context (correlation IDs - innermost)
app.add_middleware(RequestContextMiddleware)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")
