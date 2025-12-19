"""Integration tests for leave balance accounting.

Tests the complete balance lifecycle through workflow actions:
- Submit reserves balance
- Approve consumes balance
- Reject/Withdraw releases balance
- Audit trail is complete
"""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from lms.app.core.exceptions import InsufficientBalanceException
from lms.app.engines.balance_engine import BalanceEngine
from lms.app.repositories import AuditContext


class FakeSession:
    """Minimal fake session for testing balance engine in isolation."""

    def __init__(self):
        self.is_active = True


class FakeLeaveType:
    """Fake leave type without SQLAlchemy columns."""

    def __init__(self):
        self.code = "ANNUAL"


class FakeBalance:
    """Fake balance object without SQLAlchemy columns."""

    def __init__(self, initial_balance: float = 10.0):
        self.id = uuid4()
        self.user_id = uuid4()
        self.leave_type_id = uuid4()
        self.policy_id = uuid4()
        self.opening_balance = initial_balance
        self.accrued = 0.0
        self.used = 0.0
        self.pending = 0.0
        self.adjusted = 0.0
        self.carried_forward = 0.0
        self.encashed = 0.0
        self.expired = 0.0
        self.leave_type = FakeLeaveType()

    @property
    def available_balance(self) -> float:
        """Calculate available balance."""
        return float(
            self.opening_balance
            + self.accrued
            + self.carried_forward
            + self.adjusted
            - self.used
            - self.pending
            - self.encashed
            - self.expired
        )


class FakeLeaveRequest:
    """Fake leave request without SQLAlchemy columns."""

    def __init__(self, total_days: float = 3.0, request_number: str = "LR-001"):
        self.id = uuid4()
        self.user_id = uuid4()
        self.leave_type_id = uuid4()
        self.request_number = request_number
        self.start_date = date(2024, 1, 15)
        self.end_date = date(2024, 1, 17)
        self.total_days = total_days


class FakeBalanceRepo:
    """Fake balance repo that simulates balance transitions."""

    def __init__(self, initial_balance: float = 10.0):
        self.balance = FakeBalance(initial_balance)
        self.updates: list[dict] = []

    def get_current_balance(self, user_id, leave_type_id, on_date):
        return self.balance

    def update_fields(self, balance, fields, ctx, description):
        self.updates.append(
            {
                "fields": fields,
                "description": description,
            }
        )
        # Apply updates to our balance object
        for key, value in fields.items():
            setattr(self.balance, key, value)
        return self.balance


def test_balance_on_submit_reserves_days():
    """Test that submitting a leave request reserves days."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=10.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    # Create a fake leave request
    req = FakeLeaveRequest(total_days=3.0, request_number="LR-001")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Submit: should reserve 3 days
    engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore

    # Verify PENDING was incremented and one update was recorded
    assert balance_repo.balance.pending == 3.0
    assert len(balance_repo.updates) == 1
    assert balance_repo.updates[0]["fields"]["pending"] == 3.0
    assert "Reserve" in balance_repo.updates[0]["description"]


def test_balance_on_submit_insufficient_balance():
    """Test that submitting with insufficient balance raises error."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=2.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    req = FakeLeaveRequest(total_days=5.0, request_number="LR-002")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Should raise InsufficientBalanceException
    with pytest.raises(InsufficientBalanceException) as exc_info:
        engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore

    assert "ANNUAL" in str(exc_info.value)
    assert exc_info.value.details["available"] == 2.0
    assert exc_info.value.details["requested"] == 5.0


def test_balance_on_approve_consumes_pending():
    """Test that approving a leave request moves PENDING → USED."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=10.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    req = FakeLeaveRequest(total_days=3.0, request_number="LR-003")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Submit first
    engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore
    assert balance_repo.balance.pending == 3.0
    assert balance_repo.balance.used == 0.0

    # Approve
    engine.on_approve(leave_request=req, ctx=ctx)  # type: ignore

    # Verify PENDING was decremented and USED was incremented
    assert balance_repo.balance.pending == 0.0
    assert balance_repo.balance.used == 3.0
    assert len(balance_repo.updates) == 2
    assert "Approve" in balance_repo.updates[1]["description"]


def test_balance_on_reject_releases_pending():
    """Test that rejecting a leave request releases PENDING → AVAILABLE."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=10.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    req = FakeLeaveRequest(total_days=3.0, request_number="LR-004")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Submit first
    engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore
    assert balance_repo.balance.pending == 3.0

    # Reject
    engine.on_reject(leave_request=req, ctx=ctx)  # type: ignore

    # Verify PENDING was decremented (released)
    assert balance_repo.balance.pending == 0.0
    assert len(balance_repo.updates) == 2
    assert "Reject" in balance_repo.updates[1]["description"]


def test_balance_on_withdraw_releases_pending():
    """Test that withdrawing a leave request releases PENDING → AVAILABLE."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=10.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    req = FakeLeaveRequest(total_days=3.0, request_number="LR-005")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Submit first
    engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore
    assert balance_repo.balance.pending == 3.0

    # Withdraw
    engine.on_withdraw(leave_request=req, ctx=ctx)  # type: ignore

    # Verify PENDING was decremented (released)
    assert balance_repo.balance.pending == 0.0
    assert len(balance_repo.updates) == 2
    assert "Withdraw" in balance_repo.updates[1]["description"]


def test_balance_transitions_audit_trail():
    """Test that audit trail is recorded for each transition."""
    session = FakeSession()
    balance_repo = FakeBalanceRepo(initial_balance=10.0)

    engine: BalanceEngine = BalanceEngine(  # type: ignore[assignment]
        session,  # type: ignore[arg-type]
        balance_repo=balance_repo,  # type: ignore[arg-type]
        audit_repo=None,  # type: ignore[arg-type]
    )

    req = FakeLeaveRequest(total_days=2.0, request_number="LR-006")
    ctx = AuditContext(actor_id=uuid4(), actor_type="user")

    # Submit, approve, verify audit trail
    engine.on_submit(leave_request=req, ctx=ctx)  # type: ignore
    engine.on_approve(leave_request=req, ctx=ctx)  # type: ignore

    # Should have 2 updates recorded
    assert len(balance_repo.updates) == 2
    assert "LR-006" in balance_repo.updates[0]["description"]
    assert "LR-006" in balance_repo.updates[1]["description"]
