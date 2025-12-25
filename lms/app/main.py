from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .core.config import get_settings
from .core.logging import configure_logging
from .core.security import get_authenticated_user
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

# Dev-only: Override auth dependency to accept any Bearer token
if settings.DEBUG:
    from .core.auth_dev_stub import get_authenticated_user_stub

    app.dependency_overrides[get_authenticated_user] = get_authenticated_user_stub

# Add middleware (order matters - they wrap in reverse order)
# 1. Error handling (outermost)
app.add_middleware(ErrorHandlerMiddleware)
# 2. CORS
cors_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
cors_origin_regex = settings.CORS_ALLOW_ORIGIN_REGEX.strip() or None
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 3. Security headers
app.add_middleware(SecurityHeadersMiddleware)
# 4. Rate limiting
app.add_middleware(RateLimitMiddleware)
# 5. Metrics collection
app.add_middleware(MetricsMiddleware)
# 6. Request context (correlation IDs - innermost)
app.add_middleware(RequestContextMiddleware)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")
