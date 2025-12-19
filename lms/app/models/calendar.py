"""
Holiday calendar model.
"""
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class HolidayCalendar(BaseModel):
    """
    Holiday Calendar model - defines holidays for an organization.
    """
    __tablename__ = 'holiday_calendars'
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    year = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', 'year', name='uq_holiday_calendar_org_code_year'),
    )


class Holiday(BaseModel):
    """
    Holiday model - individual holidays.
    """
    __tablename__ = 'holidays'
    
    calendar_id = Column(UUID(as_uuid=True), ForeignKey('holiday_calendars.id'), nullable=False)
    
    date = Column(Date, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    is_optional = Column(Boolean, default=False)  # Optional/restricted holiday
    is_half_day = Column(Boolean, default=False)
    
    # For location-specific holidays
    locations = Column(String(500), nullable=True)  # Comma-separated location codes
    
    __table_args__ = (
        UniqueConstraint('calendar_id', 'date', name='uq_holiday_calendar_date'),
    )
