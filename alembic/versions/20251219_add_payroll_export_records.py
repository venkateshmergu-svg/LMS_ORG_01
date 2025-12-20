"""Add payroll_export_records table for outbound idempotency tracking.

Revision ID: 20251219_add_payroll_export_records
Revises: None
Create Date: 2025-12-19
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251219_add_payroll_export_records"
down_revision: str | None = None
branch_labels: list[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "payroll_export_records",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        # BaseModel mixins
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Integration-specific fields
        sa.Column("leave_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("leave_type_code", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("adapter_name", sa.String(length=100), nullable=False),
        sa.Column("export_key", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'SENT'"),
            nullable=False,
        ),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "leave_request_id",
            "start_date",
            "end_date",
            "adapter_name",
            name="uq_payroll_export_window",
        ),
    )

    # Helpful indexes
    op.create_index(
        "ix_payroll_export_records_export_key",
        "payroll_export_records",
        ["export_key"],
        unique=True,
    )
    op.create_index(
        "ix_payroll_export_records_employee_id",
        "payroll_export_records",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        "ix_payroll_export_records_leave_request_id",
        "payroll_export_records",
        ["leave_request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payroll_export_records_leave_request_id",
        table_name="payroll_export_records",
    )
    op.drop_index(
        "ix_payroll_export_records_employee_id", table_name="payroll_export_records"
    )
    op.drop_index(
        "ix_payroll_export_records_export_key", table_name="payroll_export_records"
    )
    op.drop_table("payroll_export_records")
