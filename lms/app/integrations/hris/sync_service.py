"""HRIS sync orchestrator (inbound).

Maps HRIS departments and employees into LMS `Organization`, `Department`, and `User` models
via repositories. Emits audit logs for creations/updates/soft-disables.

Constraints:
- Idempotent (upsert behavior)
- Retry-safe (no partial commits; endpoint/UoW handles transaction)
- No direct DB access outside repositories
- Engines do not import this module
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ...core.enums import UserStatus
from ...models.user import Department, Organization, User
from ...repositories import (
    AuditContext,
    AuditRepository,
    DepartmentRepository,
    OrganizationRepository,
    UserRepository,
)
from .adapter import HRISAdapter, HRISDepartment, HRISEmployee


class HRISSyncService:
    def __init__(self, session: Session):
        self.session = session
        self.audit_repo = AuditRepository(session)
        self.org_repo = OrganizationRepository(session, audit_repo=self.audit_repo)
        self.dept_repo = DepartmentRepository(session, audit_repo=self.audit_repo)
        self.user_repo = UserRepository(session, audit_repo=self.audit_repo)

    def _ensure_org(self, org_code: str, ctx: AuditContext) -> Optional[Organization]:
        org = self.org_repo.get_by_code(org_code)
        # Organizations are typically pre-provisioned; do not auto-create here.
        return org

    def _upsert_department(
        self, org: Organization, dep: HRISDepartment, ctx: AuditContext
    ) -> Department:
        from uuid import UUID

        org_id = org.id if isinstance(org.id, UUID) else UUID(str(org.id))
        existing = self.dept_repo.get_by_code(org_id, dep.department_code)
        if existing is None:
            entity = Department(
                organization_id=org.id,
                code=dep.department_code,
                name=dep.name,
                is_active=dep.is_active,
            )
            return self.dept_repo.add(
                entity, ctx=ctx, description="HRIS import: create department"
            )
        # Update if any changes
        fields: dict[str, object] = {}
        if existing.name != dep.name:
            fields["name"] = dep.name
        if existing.is_active != dep.is_active:
            fields["is_active"] = dep.is_active
        if fields:
            return self.dept_repo.update_fields(
                existing, fields, ctx=ctx, description="HRIS import: update department"
            )
        return existing

    def _upsert_employee(
        self, org: Organization, emp: HRISEmployee, ctx: AuditContext
    ) -> User:
        existing = self.user_repo.get_by_employee_id(emp.employee_id)

        # Resolve manager by employee_id (if provided)
        manager_id: Optional[object] = None
        if emp.manager_employee_id:
            manager = self.user_repo.get_by_employee_id(emp.manager_employee_id)
            manager_id = getattr(manager, "id", None)

        # Resolve department by code
        department_id: Optional[object] = None
        if emp.department_code:
            from uuid import UUID

            org_id = org.id if isinstance(org.id, UUID) else UUID(str(org.id))
            dept = self.dept_repo.get_by_code(org_id, emp.department_code)
            department_id = getattr(dept, "id", None)

        # Create new user
        if existing is None:
            entity = User(
                employee_id=emp.employee_id,
                email=emp.email,
                first_name=emp.first_name,
                last_name=emp.last_name,
                organization_id=org.id,
                department_id=department_id,
                manager_id=manager_id,
                job_title=emp.job_title,
                employment_type=emp.employment_type,
                hire_date=emp.hire_date,
                termination_date=emp.termination_date,
                status=(
                    UserStatus.TERMINATED if emp.termination_date else UserStatus.ACTIVE
                ),
            )
            return self.user_repo.create_user(entity, ctx=ctx)

        # Update existing fields if changed
        fields: dict[str, object] = {}
        if existing.email != emp.email:
            fields["email"] = emp.email
        if existing.first_name != emp.first_name:
            fields["first_name"] = emp.first_name
        if existing.last_name != emp.last_name:
            fields["last_name"] = emp.last_name
        if existing.department_id != department_id:
            fields["department_id"] = department_id
        if existing.manager_id != manager_id:
            fields["manager_id"] = manager_id
        if existing.job_title != emp.job_title:
            fields["job_title"] = emp.job_title
        if existing.employment_type != emp.employment_type:
            fields["employment_type"] = emp.employment_type
        if existing.hire_date != emp.hire_date:
            fields["hire_date"] = emp.hire_date
        if existing.termination_date != emp.termination_date:
            fields["termination_date"] = emp.termination_date
        # Soft-disable terminated users
        expected_status = (
            UserStatus.TERMINATED if emp.termination_date else UserStatus.ACTIVE
        )
        if existing.status != expected_status:
            fields["status"] = expected_status

        if fields:
            return self.user_repo.update_fields(
                existing, fields, ctx=ctx, description="HRIS import: update user"
            )
        return existing

    def sync(self, adapter: HRISAdapter, ctx: AuditContext) -> dict:
        """Run full sync: departments then employees.

        Returns a summary with counts for auditing/reporting.
        """
        departments = adapter.fetch_departments()
        employees = adapter.fetch_employees()

        created_dept = updated_dept = 0
        created_users = updated_users = 0
        skipped_orgs: set[str] = set()

        # Upsert departments grouped by org
        for dep in departments:
            org = self._ensure_org(dep.organization_code, ctx)
            if org is None:
                skipped_orgs.add(dep.organization_code)
                continue
            from uuid import UUID

            org_id = org.id if isinstance(org.id, UUID) else UUID(str(org.id))
            prev = self.dept_repo.get_by_code(org_id, dep.department_code)
            after = self._upsert_department(org, dep, ctx)
            if prev is None:
                created_dept += 1
            elif (after.name != prev.name) or (after.is_active != prev.is_active):
                updated_dept += 1

        # Upsert employees
        for emp in employees:
            org = self._ensure_org(emp.organization_code, ctx)
            if org is None:
                skipped_orgs.add(emp.organization_code)
                continue
            prev_user = self.user_repo.get_by_employee_id(emp.employee_id)
            after_user = self._upsert_employee(org, emp, ctx)
            if prev_user is None:
                created_users += 1
            elif after_user is not None and after_user.id == prev_user.id:
                # Heuristic: if any field changed, count as updated (already audited by repo)
                if (
                    (after_user.email != prev_user.email)
                    or (after_user.first_name != prev_user.first_name)
                    or (after_user.last_name != prev_user.last_name)
                    or (after_user.department_id != prev_user.department_id)
                    or (after_user.manager_id != prev_user.manager_id)
                    or (after_user.job_title != prev_user.job_title)
                    or (after_user.employment_type != prev_user.employment_type)
                    or (after_user.hire_date != prev_user.hire_date)
                    or (after_user.termination_date != prev_user.termination_date)
                    or (after_user.status != prev_user.status)
                ):
                    updated_users += 1

        return {
            "departments_created": created_dept,
            "departments_updated": updated_dept,
            "users_created": created_users,
            "users_updated": updated_users,
            "skipped_organizations": sorted(skipped_orgs),
        }
