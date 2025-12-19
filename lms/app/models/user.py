"""
User and organization related models.
"""
from datetime import datetime
from typing import Any, Optional, cast

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..core.enums import UserRole, UserStatus
from .base import BaseModel

# Association table for user roles (many-to-many)
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role', SQLEnum(UserRole), primary_key=True),
    Column('granted_at', DateTime(timezone=True), server_default='now()'),
    Column('granted_by', UUID(as_uuid=True), ForeignKey('users.id'), nullable=True),
)


class Organization(BaseModel):
    """Organization/Company model."""
    __tablename__ = 'organizations'
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    settings = Column(JSONB, default=dict)  # Org-level settings
    fiscal_year_start_month = Column(String(2), default='01')  # MM format
    timezone = Column(String(50), default='UTC')
    is_active = Column(Boolean, default=True)
    
    # Relationships
    departments = relationship("Department", back_populates="organization")
    users = relationship("User", back_populates="organization")
    leave_types = relationship("LeaveType", back_populates="organization")
    leave_policies = relationship("LeavePolicy", back_populates="organization")


class Department(BaseModel):
    """Department model."""
    __tablename__ = 'departments'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="departments")
    parent = relationship("Department", remote_side="Department.id", back_populates="children")
    children = relationship("Department", back_populates="parent")
    users = relationship("User", back_populates="department")


class User(BaseModel):
    """User model representing employees."""
    __tablename__ = 'users'
    
    # Basic info
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Authentication (hashed password for non-SSO)
    password_hash = Column(String(255), nullable=True)
    
    # SSO identifiers
    sso_provider = Column(String(50), nullable=True)
    sso_subject_id = Column(String(255), nullable=True)
    
    # Organization
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    
    # Reporting hierarchy
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Employment details
    job_title = Column(String(255), nullable=True)
    employment_type = Column(String(50), nullable=True)  # full_time, part_time, contract
    hire_date = Column(DateTime(timezone=True), nullable=True)
    probation_end_date = Column(DateTime(timezone=True), nullable=True)
    termination_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status: Any = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Additional attributes for policy evaluation
    attributes = Column(JSONB, default=dict)  # location, grade, etc.
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    department = relationship("Department", back_populates="users")
    manager = relationship("User", remote_side="User.id", back_populates="direct_reports")
    direct_reports = relationship("User", back_populates="manager")
    
    leave_balances = relationship("LeaveBalance", back_populates="user")
    leave_requests = relationship("LeaveRequest", back_populates="user", foreign_keys="LeaveRequest.user_id")
    
    # Delegations
    delegations_given = relationship("Delegation", back_populates="delegator", foreign_keys="Delegation.delegator_id")
    delegations_received = relationship("Delegation", back_populates="delegate", foreign_keys="Delegation.delegate_id")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        return cast(UserStatus, self.status) == UserStatus.ACTIVE
    
    @property
    def is_on_probation(self) -> bool:
        probation_end = cast(Optional[datetime], self.probation_end_date)
        if probation_end is None:
            return False
        return datetime.now(probation_end.tzinfo) < probation_end
