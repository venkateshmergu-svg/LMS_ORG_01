"""
Notification models.
"""
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..core.enums import NotificationType
from .base import BaseModel


class NotificationTemplate(BaseModel):
    """
    Notification Template model - configurable notification templates.
    """
    __tablename__ = 'notification_templates'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=True)  # NULL for system templates
    
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template type
    notification_type: Any = Column(SQLEnum(NotificationType), nullable=False)
    
    # Event trigger
    event_type = Column(String(100), nullable=False)  # e.g., 'leave_request_submitted', 'leave_approved'
    
    # Template content
    subject_template = Column(String(500), nullable=True)  # For email
    body_template = Column(Text, nullable=False)  # Jinja2/Mustache template
    
    # Channel-specific settings
    settings = Column(JSONB, default=dict)
    
    is_active = Column(Boolean, default=True)


class Notification(BaseModel):
    """
    Notification model - notification instances sent to users.
    """
    __tablename__ = 'notifications'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('notification_templates.id'), nullable=True)
    
    notification_type: Any = Column(SQLEnum(NotificationType), nullable=False)
    
    # Content
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    
    # Related entity
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Delivery status
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # For email/SMS
    recipient_address = Column(String(255), nullable=True)
    
    # Delivery metadata
    delivery_status = Column(String(50), default='pending')  # pending, sent, delivered, failed
    delivery_error = Column(Text, nullable=True)
    
    # Additional data
    extra_metadata = Column("metadata", JSONB, default=dict)
