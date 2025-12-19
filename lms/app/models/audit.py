"""
Audit log model - append-only for complete audit trail.
"""
import uuid
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.sql import func

from ..core.database import Base
from ..core.enums import AuditAction


class AuditLog(Base):
    """
    Audit Log model - immutable append-only audit trail.
    No updates or deletes allowed on this table.
    """
    __tablename__ = 'audit_logs'
    
    # UUID primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Timestamp (immutable)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Actor information
    actor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)  # NULL for system actions
    actor_type = Column(String(50), nullable=False)  # 'user', 'system', 'scheduler'
    actor_ip = Column(INET, nullable=True)
    actor_user_agent = Column(String(500), nullable=True)
    
    # Action details
    action: Any = Column(SQLEnum(AuditAction), nullable=False, index=True)
    
    # Entity being audited
    entity_type = Column(String(100), nullable=False, index=True)  # 'leave_request', 'user', etc.
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Organization context
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=True)
    
    # Change details
    old_values = Column(JSONB, nullable=True)  # Previous state
    new_values = Column(JSONB, nullable=True)  # New state
    changes = Column(JSONB, nullable=True)  # Diff of changed fields
    
    # Additional context
    description = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, default=dict)  # Additional contextual data
    
    # Request context
    request_id = Column(String(100), nullable=True)  # Correlation ID
    session_id = Column(String(100), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_actor_timestamp', 'actor_id', 'timestamp'),
        Index('ix_audit_org_timestamp', 'organization_id', 'timestamp'),
        Index('ix_audit_action_entity', 'action', 'entity_type'),
    )


class AuditLogArchive(Base):
    """
    Audit Log Archive model - for archived audit logs (retention management).
    Same structure as AuditLog but for archived data.
    """
    __tablename__ = 'audit_logs_archive'
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    actor_type = Column(String(50), nullable=False)
    actor_ip = Column(INET, nullable=True)
    actor_user_agent = Column(String(500), nullable=True)
    
    action: Any = Column(SQLEnum(AuditAction), nullable=False)
    
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    changes = Column(JSONB, nullable=True)
    
    description = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, default=dict)
    
    request_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
