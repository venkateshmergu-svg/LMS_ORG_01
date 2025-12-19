"""Leave domain schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ..core.enums import LeaveRequestStatus, WorkflowStepStatus
from .common import APIModel, TimestampMixin


class LeaveRequestCreate(BaseModel):
    user_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    total_days: float
    reason: Optional[str] = None


class LeaveRequestResponse(APIModel, TimestampMixin):
    id: UUID
    request_number: str
    user_id: UUID
    leave_type_id: UUID
    policy_id: Optional[UUID] = None

    start_date: date
    end_date: date
    total_days: float

    status: LeaveRequestStatus

    submitted_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    decided_by: Optional[UUID] = None


class SubmitResponse(APIModel):
    id: UUID
    status: LeaveRequestStatus
    submitted_at: Optional[datetime] = None


class ApprovalAction(BaseModel):
    """Request payload for approval action."""
    actor_user_id: UUID
    comment: Optional[str] = None


class ApprovalResponse(APIModel):
    """Response after approval/rejection."""
    leave_request_id: UUID
    status: LeaveRequestStatus
    is_final: bool  # True if workflow is complete


class WithdrawalRequest(BaseModel):
    """Request payload for withdrawal."""
    actor_user_id: UUID
    reason: Optional[str] = None


class LeaveRequestCommentCreate(BaseModel):
    user_id: UUID
    comment: str
    is_internal: bool = False
