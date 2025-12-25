"""
Leave request and workflow models.

Performance indexes added for common query patterns:
- user_id + status: filtering user's requests by status
- status + start_date + end_date: date range queries for approved requests
- user_id + start_date + end_date: overlap checking
"""
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..core.enums import DelegationType, LeaveRequestStatus, WorkflowStepStatus
from .base import BaseModel


class LeaveRequest(BaseModel):
    """
    Leave Request model - stores leave applications.
    """
    __tablename__ = 'leave_requests'
    
    # Request number for reference
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey('leave_types.id'), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey('leave_policies.id'), nullable=True)
    
    # Leave period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Duration
    total_days = Column(Float, nullable=False)
    
    # Half day / partial day support
    is_half_day_start = Column(Boolean, default=False)
    is_half_day_end = Column(Boolean, default=False)
    start_session = Column(String(20), nullable=True)  # 'morning', 'afternoon'
    end_session = Column(String(20), nullable=True)
    
    # Request details
    reason = Column(Text, nullable=True)
    contact_during_leave = Column(String(255), nullable=True)
    
    # Document attachments (stored as JSON array of file references)
    attachments = Column(JSONB, default=list)
    
    # Status
    status: Any = Column(SQLEnum(LeaveRequestStatus), default=LeaveRequestStatus.DRAFT, nullable=False, index=True)
    
    # Workflow tracking
    current_workflow_step = Column(Integer, default=0)
    
    # Submission tracking
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Final decision tracking
    decided_at = Column(DateTime(timezone=True), nullable=True)
    decided_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    decision_remarks = Column(Text, nullable=True)
    
    # Cancellation tracking
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Override/adjustment metadata
    is_backdated = Column(Boolean, default=False)
    is_lop = Column(Boolean, default=False)  # Loss of Pay
    
    # Additional metadata
    extra_metadata = Column("metadata", JSONB, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="leave_requests", foreign_keys=[user_id])
    leave_type = relationship("LeaveType", back_populates="requests")
    workflow_steps = relationship("WorkflowStep", back_populates="leave_request", order_by="WorkflowStep.step_order")
    leave_dates = relationship("LeaveRequestDate", back_populates="leave_request")
    comments = relationship("LeaveRequestComment", back_populates="leave_request")
    
    # Performance indexes for common query patterns
    __table_args__ = (
        Index('ix_leave_request_user_status', 'user_id', 'status'),
        Index('ix_leave_request_status_dates', 'status', 'start_date', 'end_date'),
        Index('ix_leave_request_user_dates', 'user_id', 'start_date', 'end_date'),
    )


class LeaveRequestDate(BaseModel):
    """
    Leave Request Date model - individual dates within a leave request.
    Allows for non-consecutive leave days and per-day tracking.
    """
    __tablename__ = 'leave_request_dates'
    
    leave_request_id = Column(UUID(as_uuid=True), ForeignKey('leave_requests.id'), nullable=False)
    
    leave_date = Column(Date, nullable=False)
    day_value = Column(Float, default=1.0)  # 0.5 for half-day, 1.0 for full day
    
    is_holiday = Column(Boolean, default=False)
    is_weekend = Column(Boolean, default=False)
    holiday_name = Column(String(255), nullable=True)
    
    # Relationships
    leave_request = relationship("LeaveRequest", back_populates="leave_dates")
    
    __table_args__ = (
        UniqueConstraint('leave_request_id', 'leave_date', name='uq_request_date'),
    )


class LeaveRequestComment(BaseModel):
    """
    Leave Request Comment model - comments/notes on leave requests.
    """
    __tablename__ = 'leave_request_comments'
    
    leave_request_id = Column(UUID(as_uuid=True), ForeignKey('leave_requests.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # HR/Manager only visibility
    
    # Relationships
    leave_request = relationship("LeaveRequest", back_populates="comments")


class WorkflowConfiguration(BaseModel):
    """
    Workflow Configuration model - defines approval workflows.
    """
    __tablename__ = 'workflow_configurations'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Targeting criteria (JSON)
    # e.g., {"leave_type_codes": ["ANNUAL"], "min_days": 3}
    criteria = Column(JSONB, default=dict)
    
    # Priority for matching (higher = checked first)
    priority = Column(Integer, default=0)
    
    # Auto-approval settings
    auto_approve_enabled = Column(Boolean, default=False)
    auto_approve_max_days = Column(Float, nullable=True)
    
    # Escalation settings
    escalation_enabled = Column(Boolean, default=False)
    escalation_hours = Column(Integer, nullable=True)  # Hours before escalation
    
    effective_from = Column(DateTime(timezone=True), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    steps = relationship("WorkflowStepConfiguration", back_populates="workflow", order_by="WorkflowStepConfiguration.step_order")


class WorkflowStepConfiguration(BaseModel):
    """
    Workflow Step Configuration model - defines steps in a workflow.
    """
    __tablename__ = 'workflow_step_configurations'
    
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('workflow_configurations.id'), nullable=False)
    
    step_order = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    
    # Approver type
    approver_type = Column(String(50), nullable=False)  # 'reporting_manager', 'department_head', 'hr', 'specific_user', 'role'
    
    # Specific approver (for 'specific_user' or 'role' type)
    specific_approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approver_role = Column(String(50), nullable=True)
    
    # Skip conditions (JSON)
    skip_conditions = Column(JSONB, default=dict)
    
    # Can delegate
    allow_delegation = Column(Boolean, default=True)
    
    # Escalation settings for this step
    escalation_hours = Column(Integer, nullable=True)
    escalate_to_type = Column(String(50), nullable=True)  # Same options as approver_type
    escalate_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    workflow = relationship("WorkflowConfiguration", back_populates="steps")


class WorkflowStep(BaseModel):
    """
    Workflow Step model - actual step instances for leave requests.
    """
    __tablename__ = 'workflow_steps'
    
    leave_request_id = Column(UUID(as_uuid=True), ForeignKey('leave_requests.id'), nullable=False)
    step_config_id = Column(UUID(as_uuid=True), ForeignKey('workflow_step_configurations.id'), nullable=True)
    
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    
    # Assigned approver
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Status
    status: Any = Column(SQLEnum(WorkflowStepStatus), default=WorkflowStepStatus.PENDING, nullable=False)
    
    # Action tracking
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    action_remarks = Column(Text, nullable=True)
    
    # Delegation tracking
    delegated_from_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    delegated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Escalation tracking
    escalated_from_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    escalation_reason = Column(Text, nullable=True)
    
    # Due date for escalation calculation
    due_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    leave_request = relationship("LeaveRequest", back_populates="workflow_steps")


class Delegation(BaseModel):
    """
    Delegation model - tracks approval delegation settings.
    """
    __tablename__ = 'delegations'
    
    delegator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    delegate_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    delegation_type: Any = Column(SQLEnum(DelegationType), nullable=False)
    
    # For specific request delegation
    leave_request_id = Column(UUID(as_uuid=True), ForeignKey('leave_requests.id'), nullable=True)
    
    # For temporary delegation
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Scope restrictions (JSON)
    # e.g., {"leave_types": ["ANNUAL"], "max_days": 5}
    scope = Column(JSONB, default=dict)
    
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    delegator = relationship("User", back_populates="delegations_given", foreign_keys=[delegator_id])
    delegate = relationship("User", back_populates="delegations_received", foreign_keys=[delegate_id])
