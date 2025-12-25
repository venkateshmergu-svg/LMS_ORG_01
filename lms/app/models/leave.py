"""
Leave type, policy, and balance models.
"""
from typing import Any, cast

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
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

from ..core.enums import AccrualFrequency, CarryForwardType, EligibilityType, LeaveUnit
from .base import BaseModel


class LeaveType(BaseModel):
    """
    Leave Type model - defines categories of leave.
    Examples: Annual Leave, Sick Leave, Maternity Leave, etc.
    """
    __tablename__ = 'leave_types'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    
    code = Column(String(50), nullable=False, index=True)  # e.g., 'ANNUAL', 'SICK'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Basic settings
    unit: Any = Column(SQLEnum(LeaveUnit), default=LeaveUnit.DAYS, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Display
    color_code = Column(String(7), nullable=True)  # Hex color for UI
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    
    # Constraints
    requires_document = Column(Boolean, default=False)
    requires_reason = Column(Boolean, default=True)
    min_days_per_request = Column(Float, default=0.5)
    max_days_per_request = Column(Float, nullable=True)
    
    # Settings JSON for extensibility
    settings = Column(JSONB, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="leave_types")
    policies = relationship("LeavePolicy", back_populates="leave_type")
    balances = relationship("LeaveBalance", back_populates="leave_type")
    requests = relationship("LeaveRequest", back_populates="leave_type")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_leave_type_org_code'),
    )


class LeavePolicy(BaseModel):
    """
    Leave Policy model - configurable rules for leave allocation and usage.
    Policies can be assigned to specific user groups via policy assignments.
    """
    __tablename__ = 'leave_policies'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey('leave_types.id'), nullable=False)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Effective dates
    effective_from = Column(DateTime(timezone=True), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)  # NULL = no end date
    
    # Accrual settings
    accrual_frequency: Any = Column(SQLEnum(AccrualFrequency), nullable=False)
    accrual_amount = Column(Float, nullable=False)  # Amount per accrual period
    accrual_cap = Column(Float, nullable=True)  # Max balance cap, NULL = unlimited
    
    # Pro-rata settings for mid-year joins
    prorate_on_join = Column(Boolean, default=True)
    prorate_on_exit = Column(Boolean, default=True)
    
    # Carry-forward settings
    carry_forward_type: Any = Column(SQLEnum(CarryForwardType), default=CarryForwardType.NONE)
    carry_forward_limit = Column(Float, nullable=True)  # Max carry-forward amount
    carry_forward_expiry_months = Column(Integer, nullable=True)  # Months until expiry
    
    # Eligibility
    eligibility_type: Any = Column(SQLEnum(EligibilityType), default=EligibilityType.IMMEDIATE)
    eligibility_tenure_days = Column(Integer, nullable=True)  # Days to wait if tenure-based
    
    # Eligibility rules as JSON for complex conditions
    # e.g., {"employment_type": ["full_time"], "location": ["US", "UK"]}
    eligibility_rules = Column(JSONB, default=dict)
    
    # Encashment settings
    encashment_allowed = Column(Boolean, default=False)
    encashment_min_balance = Column(Float, nullable=True)  # Min balance to retain
    encashment_max_days = Column(Float, nullable=True)  # Max days to encash per year
    
    # LOP (Loss of Pay) settings
    lop_after_exhaustion = Column(Boolean, default=False)  # Allow LOP after balance exhausted
    
    # Negative balance settings
    allow_negative_balance = Column(Boolean, default=False)
    negative_balance_limit = Column(Float, nullable=True)
    
    # Weekend/Holiday settings
    include_weekends = Column(Boolean, default=False)
    include_holidays = Column(Boolean, default=False)
    
    # Advanced settings as JSON
    # Can include: sandwich rules, clubbing rules, etc.
    advanced_settings = Column(JSONB, default=dict)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="leave_policies")
    leave_type = relationship("LeaveType", back_populates="policies")
    assignments = relationship("PolicyAssignment", back_populates="policy")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_leave_policy_org_code'),
        CheckConstraint('accrual_amount >= 0', name='ck_accrual_amount_positive'),
    )


class PolicyAssignment(BaseModel):
    """
    Policy Assignment model - links policies to users/groups.
    Supports assignment by department, job level, or individual user.
    """
    __tablename__ = 'policy_assignments'
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey('leave_policies.id'), nullable=False)
    
    # Assignment target (one of these should be set)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    
    # Attribute-based assignment criteria (for flexible targeting)
    # e.g., {"employment_type": "full_time", "grade": "senior"}
    criteria = Column(JSONB, default=dict)
    
    # Priority for conflict resolution (higher = takes precedence)
    priority = Column(Integer, default=0)
    
    effective_from = Column(DateTime(timezone=True), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    policy = relationship("LeavePolicy", back_populates="assignments")


class LeaveBalance(BaseModel):
    """
    Leave Balance model - tracks current leave balances per user per leave type.
    """
    __tablename__ = 'leave_balances'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey('leave_types.id'), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey('leave_policies.id'), nullable=False)
    
    # Period (typically fiscal year)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Balance components
    opening_balance = Column(Float, default=0.0, nullable=False)  # Start of period
    accrued = Column(Float, default=0.0, nullable=False)  # Total accrued
    used = Column(Float, default=0.0, nullable=False)  # Total used
    pending = Column(Float, default=0.0, nullable=False)  # Pending approval
    adjusted = Column(Float, default=0.0, nullable=False)  # Manual adjustments
    carried_forward = Column(Float, default=0.0, nullable=False)  # From previous period
    encashed = Column(Float, default=0.0, nullable=False)  # Encashed leaves
    expired = Column(Float, default=0.0, nullable=False)  # Expired carry-forward
    
    # Last accrual tracking
    last_accrual_date = Column(DateTime(timezone=True), nullable=True)
    next_accrual_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="balances")
    transactions = relationship("BalanceTransaction", back_populates="balance")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'leave_type_id', 'period_start', name='uq_user_leave_type_period'),
        # Performance indexes for common query patterns
        Index('ix_balance_user_type_period', 'user_id', 'leave_type_id', 'period_start', 'period_end'),
        Index('ix_balance_user_period', 'user_id', 'period_start', 'period_end'),
    )
    
    @property
    def available_balance(self) -> float:
        """Calculate available balance."""
        opening_balance = cast(float, self.opening_balance)
        accrued = cast(float, self.accrued)
        carried_forward = cast(float, self.carried_forward)
        adjusted = cast(float, self.adjusted)
        used = cast(float, self.used)
        pending = cast(float, self.pending)
        encashed = cast(float, self.encashed)
        expired = cast(float, self.expired)

        return float(opening_balance + accrued + carried_forward + adjusted - used - pending - encashed - expired)


class BalanceTransaction(BaseModel):
    """
    Balance Transaction model - audit log for all balance changes.
    Append-only for complete audit trail.
    """
    __tablename__ = 'balance_transactions'
    
    balance_id = Column(UUID(as_uuid=True), ForeignKey('leave_balances.id'), nullable=False)
    leave_request_id = Column(UUID(as_uuid=True), ForeignKey('leave_requests.id'), nullable=True)
    
    transaction_type = Column(String(50), nullable=False)  # accrual, usage, adjustment, etc.
    amount = Column(Float, nullable=False)  # Positive for credit, negative for debit
    
    # Balance snapshot after transaction
    balance_after = Column(Float, nullable=False)
    
    # Metadata
    reference = Column(String(255), nullable=True)  # Reference number/description
    remarks = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    balance = relationship("LeaveBalance", back_populates="transactions")


class AccrualSchedule(BaseModel):
    """
    Accrual Schedule model - tracks scheduled accrual runs.
    """
    __tablename__ = 'accrual_schedules'
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey('leave_policies.id'), nullable=False)
    
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    users_processed = Column(Integer, default=0)
    total_accrued = Column(Float, default=0.0)
    
    error_message = Column(Text, nullable=True)
