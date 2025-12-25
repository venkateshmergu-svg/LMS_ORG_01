"""API v1 router."""

from fastapi import APIRouter

from .endpoints import (
    approvals,
    audit,
    auth,
    integrations,
    leave,
    leave_requests,
    metrics,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(leave.router, prefix="/leave", tags=["leave"])
api_router.include_router(
    leave_requests.router, prefix="/leave-requests", tags=["leave-requests"]
)
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(
    integrations.router, prefix="/integrations", tags=["integrations"]
)
api_router.include_router(metrics.router, prefix="", tags=["observability"])
