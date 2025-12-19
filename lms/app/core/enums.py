"""
Enumeration types for the Leave Management System.
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"
    SYSTEM_ADMIN = "system_admin"
    AUDITOR = "auditor"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class LeaveRequestStatus(str, Enum):
    """Leave request workflow states."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


class WorkflowStepStatus(str, Enum):
    """Individual workflow step states."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"
    ESCALATED = "escalated"
    DELEGATED = "delegated"


class AccrualFrequency(str, Enum):
    """Leave accrual frequency types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    ONE_TIME = "one_time"


class LeaveUnit(str, Enum):
    """Unit of leave measurement."""
    DAYS = "days"
    HOURS = "hours"


class CarryForwardType(str, Enum):
    """Types of carry-forward rules."""
    NONE = "none"
    UNLIMITED = "unlimited"
    CAPPED = "capped"
    PERCENTAGE = "percentage"


class EligibilityType(str, Enum):
    """Types of eligibility rules."""
    IMMEDIATE = "immediate"
    AFTER_PROBATION = "after_probation"
    AFTER_TENURE = "after_tenure"
    CUSTOM = "custom"


class AuditAction(str, Enum):
    """Types of auditable actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    APPROVAL = "approval"
    REJECTION = "rejection"
    DELEGATION = "delegation"
    ESCALATION = "escalation"
    ACCRUAL = "accrual"
    ADJUSTMENT = "adjustment"
    ENCASHMENT = "encashment"
    CARRY_FORWARD = "carry_forward"
    EXPIRY = "expiry"
    LOGIN = "login"
    LOGOUT = "logout"


class NotificationType(str, Enum):
    """Types of notifications."""
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    PUSH = "push"


class DelegationType(str, Enum):
    """Types of approval delegation."""
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    SPECIFIC_REQUEST = "specific_request"
