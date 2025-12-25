"""
Seed script for test data.

Creates:
- 2 Managers (Mike and Mary)
- 10 Employees reporting to each manager (20 total)
- Leave balances for all users
- Sample leave requests
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from typing import cast
from uuid import UUID, uuid4

# Add project root to path
sys.path.insert(0, ".")

from sqlalchemy import select
from sqlalchemy.orm import Session

from lms.app.core.database import SessionLocal
from lms.app.core.enums import (
    AccrualFrequency,
    LeaveRequestStatus,
    UserStatus,
)
from lms.app.models.leave import (
    LeaveBalance,
    LeavePolicy,
    LeaveType,
)
from lms.app.models.user import Organization, User
from lms.app.models.workflow import LeaveRequest, LeaveRequestDate


def get_or_create_org(db: Session) -> Organization:
    """Get or create the default organization."""
    org = (
        db.execute(select(Organization).where(Organization.code == "ORG1"))
        .scalars()
        .first()
    )
    if org is None:
        org = Organization(code="ORG1", name="Acme Corporation")
        db.add(org)
        db.flush()
    return org


def get_or_create_leave_type(db: Session, org_id: UUID) -> LeaveType:
    """Get or create annual leave type."""
    leave_type = (
        db.execute(
            select(LeaveType).where(
                LeaveType.organization_id == org_id,
                LeaveType.code == "ANNUAL",
            )
        )
        .scalars()
        .first()
    )

    if leave_type is None:
        leave_type = LeaveType(
            organization_id=org_id,
            code="ANNUAL",
            name="Annual Leave",
            description="Paid annual leave",
            is_active=True,
            is_paid=True,
            requires_reason=True,
            display_order=1,
        )
        db.add(leave_type)
        db.flush()
    return leave_type


def get_or_create_policy(db: Session, org_id: UUID, leave_type_id: UUID) -> LeavePolicy:
    """Get or create leave policy."""
    policy = (
        db.execute(
            select(LeavePolicy).where(
                LeavePolicy.organization_id == org_id,
                LeavePolicy.leave_type_id == leave_type_id,
                LeavePolicy.is_active.is_(True),
            )
        )
        .scalars()
        .first()
    )

    if policy is None:
        policy = LeavePolicy(
            organization_id=org_id,
            leave_type_id=leave_type_id,
            code="ANNUAL_DEFAULT",
            name="Annual Leave Policy",
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to=None,
            accrual_frequency=AccrualFrequency.MONTHLY,
            accrual_amount=1.67,
            is_active=True,
        )
        db.add(policy)
        db.flush()
    return policy


def create_user(
    db: Session,
    org_id: UUID,
    employee_id: str,
    email: str,
    first_name: str,
    last_name: str,
    manager_id: UUID | None = None,
    job_title: str = "Employee",
) -> User:
    """Create a user if not exists."""
    if (
        existing := db.execute(select(User).where(User.email == email))
        .scalars()
        .first()
    ):
        print(f"  User {email} already exists")
        return existing

    user = User(
        employee_id=employee_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        organization_id=org_id,
        manager_id=manager_id,
        job_title=job_title,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.flush()
    print(f"  Created user: {first_name} {last_name} ({email})")
    return user


def create_leave_balance(
    db: Session,
    user_id: UUID,
    leave_type_id: UUID,
    policy_id: UUID,
    opening_balance: float = 20.0,
) -> LeaveBalance:
    """Create leave balance for user."""
    year = datetime.now(timezone.utc).year
    period_start = datetime(year, 1, 1, tzinfo=timezone.utc)
    period_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    if existing := (
        db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == user_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.period_start == period_start,
            )
        )
        .scalars()
        .first()
    ):
        return existing

    balance = LeaveBalance(
        user_id=user_id,
        leave_type_id=leave_type_id,
        policy_id=policy_id,
        period_start=period_start,
        period_end=period_end,
        opening_balance=opening_balance,
        accrued=0.0,
        used=0.0,
        pending=0.0,
        adjusted=0.0,
        carried_forward=0.0,
    )
    db.add(balance)
    db.flush()
    return balance


def create_leave_request(
    db: Session,
    user: User,
    leave_type_id: UUID,
    policy_id: UUID,
    start_date: datetime,
    end_date: datetime,
    reason: str,
) -> LeaveRequest:
    """Create a leave request."""
    total_days = (end_date - start_date).days + 1

    request = LeaveRequest(
        request_number=f"LR-{uuid4().hex[:8].upper()}",
        user_id=user.id,
        leave_type_id=leave_type_id,
        policy_id=policy_id,
        start_date=start_date,
        end_date=end_date,
        total_days=float(total_days),
        reason=reason,
        status=LeaveRequestStatus.PENDING_APPROVAL,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(request)
    db.flush()

    # Create leave request dates
    current = start_date
    while current <= end_date:
        req_date = LeaveRequestDate(
            leave_request_id=request.id,
            leave_date=current,
            day_value=1.0,
            is_holiday=False,
            is_weekend=current.weekday() >= 5,
        )
        db.add(req_date)
        current = current + timedelta(days=1)

    db.flush()
    print(
        f"  Created leave request for {user.first_name}: {start_date.date()} to {end_date.date()}"
    )
    return request


def seed_data():
    """Main seeding function."""
    print("\n" + "=" * 60)
    print("SEEDING TEST DATA")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Get or create organization
        print("\n[1/5] Setting up organization...")
        org = get_or_create_org(db)
        org_id = cast(UUID, org.id)
        print(f"  Organization: {org.name} (ID: {org_id})")

        # Get or create leave type and policy
        print("\n[2/5] Setting up leave type and policy...")
        leave_type = get_or_create_leave_type(db, org_id)
        leave_type_id = cast(UUID, leave_type.id)
        policy = get_or_create_policy(db, org_id, leave_type_id)
        policy_id = cast(UUID, policy.id)
        print(f"  Leave Type: {leave_type.name}")
        print(f"  Policy: {policy.name}")

        # Create managers
        print("\n[3/5] Creating managers...")
        manager1 = create_user(
            db,
            org_id,
            employee_id="MGR001",
            email="mike.manager@example.com",
            first_name="Mike",
            last_name="Manager",
            job_title="Engineering Manager",
        )

        manager2 = create_user(
            db,
            org_id,
            employee_id="MGR002",
            email="mary.manager@example.com",
            first_name="Mary",
            last_name="Director",
            job_title="Product Director",
        )

        # Create leave balances for managers
        create_leave_balance(
            db, cast(UUID, manager1.id), leave_type_id, policy_id, 25.0
        )
        create_leave_balance(
            db, cast(UUID, manager2.id), leave_type_id, policy_id, 25.0
        )

        # Create employees for Manager 1 (Mike)
        print("\n[4/5] Creating employees for Mike Manager...")
        team1_names = [
            ("Alice", "Anderson"),
            ("Bob", "Brown"),
            ("Carol", "Clark"),
            ("David", "Davis"),
            ("Emma", "Evans"),
            ("Frank", "Foster"),
            ("Grace", "Green"),
            ("Henry", "Hill"),
            ("Ivy", "Ingram"),
            ("Jack", "Johnson"),
        ]

        team1_employees = []
        for i, (first, last) in enumerate(team1_names, 1):
            emp = create_user(
                db,
                org_id,
                employee_id=f"EMP1{i:02d}",
                email=f"{first.lower()}.{last.lower()}@example.com",
                first_name=first,
                last_name=last,
                manager_id=cast(UUID, manager1.id),
                job_title="Software Engineer",
            )
            create_leave_balance(db, cast(UUID, emp.id), leave_type_id, policy_id, 20.0)
            team1_employees.append(emp)

        # Create employees for Manager 2 (Mary)
        print("\n[5/5] Creating employees for Mary Director...")
        team2_names = [
            ("Kevin", "King"),
            ("Linda", "Lewis"),
            ("Michael", "Miller"),
            ("Nancy", "Nelson"),
            ("Oscar", "Owen"),
            ("Patricia", "Parker"),
            ("Quinn", "Quinn"),
            ("Rachel", "Roberts"),
            ("Steve", "Smith"),
            ("Tina", "Taylor"),
        ]

        team2_employees = []
        for i, (first, last) in enumerate(team2_names, 1):
            emp = create_user(
                db,
                org_id,
                employee_id=f"EMP2{i:02d}",
                email=f"{first.lower()}.{last.lower()}@example.com",
                first_name=first,
                last_name=last,
                manager_id=cast(UUID, manager2.id),
                job_title="Product Analyst",
            )
            create_leave_balance(db, cast(UUID, emp.id), leave_type_id, policy_id, 20.0)
            team2_employees.append(emp)

        # Create sample leave requests
        print("\n[BONUS] Creating sample leave requests...")

        # Leave requests for Team 1
        if team1_employees:
            create_leave_request(
                db,
                team1_employees[0],
                leave_type_id,
                policy_id,
                datetime(2025, 12, 26, tzinfo=timezone.utc),
                datetime(2025, 12, 27, tzinfo=timezone.utc),
                "Holiday vacation",
            )
            create_leave_request(
                db,
                team1_employees[1],
                leave_type_id,
                policy_id,
                datetime(2025, 12, 30, tzinfo=timezone.utc),
                datetime(2025, 12, 31, tzinfo=timezone.utc),
                "New Year celebration",
            )
            create_leave_request(
                db,
                team1_employees[2],
                leave_type_id,
                policy_id,
                datetime(2026, 1, 2, tzinfo=timezone.utc),
                datetime(2026, 1, 3, tzinfo=timezone.utc),
                "Personal time",
            )

        # Leave requests for Team 2
        if team2_employees:
            create_leave_request(
                db,
                team2_employees[0],
                leave_type_id,
                policy_id,
                datetime(2025, 12, 28, tzinfo=timezone.utc),
                datetime(2025, 12, 29, tzinfo=timezone.utc),
                "Family event",
            )
            create_leave_request(
                db,
                team2_employees[1],
                leave_type_id,
                policy_id,
                datetime(2026, 1, 6, tzinfo=timezone.utc),
                datetime(2026, 1, 8, tzinfo=timezone.utc),
                "Medical appointment",
            )

        db.commit()

        print("\n" + "=" * 60)
        print("SEED DATA SUMMARY")
        print("=" * 60)
        print(f"  Organization: {org.name}")
        print("  Managers: 2 (Mike Manager, Mary Director)")
        print("  Employees: 20 (10 per manager)")
        print("  Leave Requests: 5 (pending approval)")
        print("\n  Manager 1 (Mike) email: mike.manager@example.com")
        print("  Manager 2 (Mary) email: mary.manager@example.com")
        print("\n  To login as a manager, use: /auth/callback?code=dev:manager")
        print("  To login as an employee, use: /auth/callback?code=dev:employee")
        print("=" * 60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
