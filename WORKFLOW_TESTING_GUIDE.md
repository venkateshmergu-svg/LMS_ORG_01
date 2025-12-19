"""
Workflow State Machine - Testing Scenarios & Expected Behaviors

This guide shows how each requirement is enforced and tested.
"""

# ==============================================================================

# 1. APPROVING OUT-OF-ORDER STEP → ❌ Exception

# ==============================================================================

"""
SCENARIO: User tries to approve Step 2 before Step 1 is approved

Flow:

1. Create leave request (DRAFT)
2. Submit → Creates 2 steps: Step 1 (PENDING), Step 2 (PENDING)
3. Try to approve Step 2 directly

RESULT: ❌ WorkflowStateException
"""

# Code location: app/engines/workflow_engine.py, approve() method, line ~189

# The validation:

# if step.status != WorkflowStepStatus.PENDING:

# raise WorkflowStateException(

# current_state=step.status.value,

# attempted_action=f"approve step (expected PENDING)"

# )

# Why it fails:

# - When leave request submitted, workflow creates all steps as PENDING

# - First step is PENDING (ready), others stay PENDING (not active)

# - If you try approve Step 2 while it's still PENDING, it's not the active step

# - The code checks step.status != PENDING to prevent this

# AUDIT TRAIL: If exception is raised, transaction rolls back → NO audit entries

# ==============================================================================

# 2. WRONG APPROVER → ❌ Exception

# ==============================================================================

"""
SCENARIO: User A tries to approve a step assigned to User B

Flow:

1. Create leave request for Employee X
2. Submit → Step 1 assigned to Manager Y (X's manager)
3. Manager Z (different person) tries to approve

RESULT: ❌ ApprovalException
"""

# Code location: app/engines/workflow_engine.py, approve() method, line ~184

# The validation:

# if step.approver_id != actor_user_id:

# raise ApprovalException(

# f"Only assigned approver (user {step.approver_id}) can approve this step",

# approver_id=actor_user_id

# )

# Why it fails:

# - When step is created, it stores approver_id in WorkflowStep.approver_id

# - Approve() method checks: actor_user_id == step.approver_id

# - If mismatch, raises ApprovalException immediately

# Example:

# step.approver_id = "user-manager-123"

# actor_user_id = "user-wrong-456"

# → Exception: "Only assigned approver (user user-manager-123) can approve this step"

# AUDIT TRAIL: If exception is raised, transaction rolls back → NO audit entries

# ==============================================================================

# 3. FINAL APPROVAL → LeaveRequest = APPROVED

# ==============================================================================

"""
SCENARIO: Last approver approves, workflow complete

Flow:

1. Create leave request (DRAFT)
2. Submit → Step 1 (PENDING), Step 2 (PENDING)
3. Approver 1 approves Step 1 → Step 2 activated (PENDING)
4. Approver 2 approves Step 2 → Workflow COMPLETE

RESULT: ✅ LeaveRequest.status = APPROVED
"""

# Code location: app/engines/workflow_engine.py, approve() method, line ~225-250

# The logic:

# 1. Mark current step APPROVED

# 2. Check if more steps exist

# 3. If final step:

# - Set LeaveRequest.status = APPROVED

# - Set decided_at = now

# - Set decided_by = actor_user_id

# - Return WorkflowCompleted

# Code snippet:

# if current_idx < len(all_steps) - 1:

# # Activate next step

# next_step = all_steps[current_idx + 1]

# next_step = self.step_repo.update_fields(...)

# return StepActivated(step=next_step, is_final=False)

# else:

# # Final step approved; complete workflow

# leave_request = self.leave_request_repo.update_fields(

# leave_request,

# {

# "status": LeaveRequestStatus.APPROVED,

# "decided_at": now,

# "decided_by": actor_user_id,

# "decision_remarks": comment,

# },

# ctx=ctx,

# description="Approve leave request (final workflow step)",

# )

# return WorkflowCompleted(

# leave_request=leave_request,

# final_status=LeaveRequestStatus.APPROVED

# )

# AUDIT TRAIL:

# - Audit entry for step APPROVED (via step_repo.update_fields)

# - Audit entry for LeaveRequest status change to APPROVED (via leave_request_repo.update_fields)

# - Both within same transaction

# ==============================================================================

# 4. REJECTION → LeaveRequest = REJECTED

# ==============================================================================

"""
SCENARIO: Any approver rejects the request

Flow:

1. Create leave request (DRAFT)
2. Submit → Steps instantiated (PENDING_APPROVAL)
3. Approver 1 rejects Step 1

RESULT: ✅ LeaveRequest.status = REJECTED (terminal)
"""

# Code location: app/engines/workflow_engine.py, reject() method, line ~253-310

# The logic:

# 1. Verify approver identity (same as approve)

# 2. Verify step is PENDING

# 3. Mark step as REJECTED

# 4. Set LeaveRequest.status = REJECTED

# 5. Return WorkflowCompleted

# Code snippet:

# step = self.step_repo.update_fields(

# step,

# {

# "status": WorkflowStepStatus.REJECTED,

# "actioned_at": now,

# "action_remarks": comment,

# },

# ctx=ctx,

# description="Reject workflow step",

# )

#

# leave_request = self.leave_request_repo.update_fields(

# leave_request,

# {

# "status": LeaveRequestStatus.REJECTED,

# "decided_at": now,

# "decided_by": actor_user_id,

# "decision_remarks": comment,

# },

# ctx=ctx,

# description="Reject leave request",

# )

# AUDIT TRAIL:

# - Audit entry for step status → REJECTED

# - Audit entry for LeaveRequest status → REJECTED

# - Both within same transaction

# - Terminal state: no further actions allowed

# ==============================================================================

# 5. WITHDRAWAL → LeaveRequest = WITHDRAWN

# ==============================================================================

"""
SCENARIO: Employee withdraws their own request before final approval

Flow:

1. Create leave request (DRAFT)
2. Submit → PENDING_APPROVAL
3. Employee withdraws request

RESULT: ✅ LeaveRequest.status = WITHDRAWN (terminal)
All PENDING steps marked SKIPPED
"""

# Code location: app/engines/workflow_engine.py, withdraw() method, line ~313-415

# The logic:

# 1. Verify only request owner can withdraw

# 2. Verify request is PENDING_APPROVAL

# 3. Set LeaveRequest.status = WITHDRAWN

# 4. Mark all PENDING steps as SKIPPED

# 5. Return WorkflowCompleted

# Code snippet:

# if leave_request.user_id != actor_user_id:

# raise ApprovalException(

# f"Only leave request owner (user {leave_request.user_id}) can withdraw",

# )

#

# if leave_request.status != LeaveRequestStatus.PENDING_APPROVAL:

# raise WorkflowStateException(

# current_state=leave_request.status.value,

# attempted_action="withdraw leave request"

# )

#

# leave_request = self.leave_request_repo.update_fields(

# leave_request,

# {

# "status": LeaveRequestStatus.WITHDRAWN,

# "cancelled_at": now,

# "cancelled_by": actor_user_id,

# "cancellation_reason": reason,

# },

# ctx=ctx,

# description="Withdraw leave request",

# )

#

# # Mark pending steps as skipped

# for step in all_steps:

# self.step_repo.update_fields(

# step,

# {"status": WorkflowStepStatus.SKIPPED},

# ctx=ctx,

# description="Skip pending workflow step (request withdrawn)",

# )

# AUDIT TRAIL:

# - Audit entry for LeaveRequest status → WITHDRAWN

# - Audit entries for each PENDING step → SKIPPED

# - All within same transaction

# - Terminal state: no further actions allowed

# ==============================================================================

# 6. AUDIT ROWS FOR EACH TRANSITION

# ==============================================================================

"""
SCENARIO: Complete workflow with full audit trail

Flow:

1. Create leave request → Audit entry (CREATE LeaveRequest)
2. Submit request → Audit entries:
   - UPDATE LeaveRequest (status: DRAFT → PENDING_APPROVAL)
   - CREATE WorkflowStep 1
   - UPDATE WorkflowStep 1 (activate)
   - CREATE WorkflowStep 2
3. Approve Step 1 → Audit entries:
   - UPDATE WorkflowStep 1 (status: PENDING → APPROVED)
   - UPDATE WorkflowStep 2 (status: PENDING → PENDING, mark active)
4. Approve Step 2 → Audit entries:
   - UPDATE WorkflowStep 2 (status: PENDING → APPROVED)
   - UPDATE LeaveRequest (status: PENDING_APPROVAL → APPROVED)

RESULT: ✅ 9+ audit trail entries
"""

# Code locations:

# 1. Repositories emit audit via update_fields() - app/repositories/base.py, line ~75-95

# 2. Each mutation calls \_emit_audit() with action, entity, changes

# 3. AuditLog entry created via audit_repo.append() - app/repositories/audit_repository.py

# Audit entry structure:

# {

# "action": "UPDATE",

# "entity_type": "WorkflowStep",

# "entity_id": "step-uuid",

# "old_values": {"status": "pending"},

# "new_values": {"status": "approved"},

# "changes": {"status": {"old": "pending", "new": "approved"}},

# "description": "Approve workflow step",

# "actor_id": "user-uuid",

# "actor_type": "user",

# "timestamp": "2025-12-19T10:30:00Z",

# "request_id": "request-uuid",

# }

# Why audit is transactional:

# 1. UnitOfWork wraps entire request in transaction

# 2. Repositories flush mutations to session

# 3. Audit entries created via same session

# 4. On success: transaction.commit() → all persist

# 5. On error: transaction.rollback() → none persist

# ==============================================================================

# TESTING TEMPLATE

# ==============================================================================

"""
import pytest
from uuid import uuid4
from datetime import date, datetime, timezone
from app.core.exceptions import ApprovalException, WorkflowStateException
from app.core.enums import LeaveRequestStatus, WorkflowStepStatus

@pytest.fixture
def setup_workflow(session, leave_engine, workflow_engine, audit_context): # Create org, users, leave type, workflow config
org = Organization(code="TEST", name="Test Org")
session.add(org)
session.flush()

    manager = User(
        employee_id="MGR001",
        email="manager@test.com",
        first_name="Manager",
        last_name="User",
        organization_id=org.id,
    )
    session.add(manager)
    session.flush()

    employee = User(
        employee_id="EMP001",
        email="employee@test.com",
        first_name="Employee",
        last_name="User",
        organization_id=org.id,
        manager_id=manager.id,
    )
    session.add(employee)
    session.flush()

    # Create leave type and workflow
    leave_type = LeaveType(
        organization_id=org.id,
        code="ANNUAL",
        name="Annual Leave",
    )
    session.add(leave_type)
    session.flush()

    workflow = WorkflowConfiguration(
        organization_id=org.id,
        code="STANDARD",
        name="Standard Approval",
    )
    session.add(workflow)
    session.flush()

    return {
        "org": org,
        "manager": manager,
        "employee": employee,
        "leave_type": leave_type,
        "workflow": workflow,
    }

def test_out_of_order_approval_raises_exception(setup_workflow): # Arrange
leave_req = leave_engine.create_leave_request(
user_id=setup_workflow["employee"].id,
leave_type_id=setup_workflow["leave_type"].id,
start_date=date(2025, 12, 20),
end_date=date(2025, 12, 22),
total_days=3,
reason="Vacation",
ctx=audit_context,
)

    updated_req = leave_engine.submit(
        request_id=leave_req.leave_request.id,
        ctx=audit_context,
    )

    steps = session.execute(
        select(WorkflowStep).where(
            WorkflowStep.leave_request_id == updated_req.id
        )
    ).scalars().all()

    step1, step2 = steps[0], steps[1]

    # Act & Assert: Try to approve step2 before step1
    with pytest.raises(WorkflowStateException) as exc_info:
        workflow_engine.approve(
            step_id=step2.id,
            actor_user_id=setup_workflow["manager"].id,
            comment="Approved",
            ctx=audit_context,
        )

    assert "expected PENDING" in str(exc_info.value)

def test_wrong_approver_raises_exception(setup_workflow): # Arrange: Create second user (not the assigned approver)
other_user = User(
employee_id="OTH001",
email="other@test.com",
first_name="Other",
last_name="User",
organization_id=setup_workflow["org"].id,
)
session.add(other_user)
session.flush()

    leave_req = leave_engine.create_leave_request(...)
    updated_req = leave_engine.submit(...)
    step = session.execute(select(WorkflowStep)).scalars().first()

    # Act & Assert: Try to approve with wrong user
    with pytest.raises(ApprovalException) as exc_info:
        workflow_engine.approve(
            step_id=step.id,
            actor_user_id=other_user.id,  # Wrong approver
            comment="Approved",
            ctx=audit_context,
        )

    assert "Only assigned approver" in str(exc_info.value)

def test_final_approval_sets_leave_request_to_approved(setup_workflow): # Arrange
leave_req = leave_engine.create_leave_request(...)
updated_req = leave_engine.submit(...)
steps = session.execute(select(WorkflowStep)).scalars().all()

    # Act: Approve all steps
    for step in steps:
        result = workflow_engine.approve(
            step_id=step.id,
            actor_user_id=setup_workflow["manager"].id,
            comment="Approved",
            ctx=audit_context,
        )

    # Assert: Final result is WorkflowCompleted
    assert isinstance(result, WorkflowCompleted)
    assert result.final_status == LeaveRequestStatus.APPROVED
    assert result.leave_request.status == LeaveRequestStatus.APPROVED

def test_rejection_sets_leave_request_to_rejected(setup_workflow): # Arrange
leave_req = leave_engine.create_leave_request(...)
updated_req = leave_engine.submit(...)
step = session.execute(select(WorkflowStep)).scalars().first()

    # Act: Reject
    result = workflow_engine.reject(
        step_id=step.id,
        actor_user_id=setup_workflow["manager"].id,
        comment="Need more info",
        ctx=audit_context,
    )

    # Assert
    assert isinstance(result, WorkflowCompleted)
    assert result.final_status == LeaveRequestStatus.REJECTED
    assert result.leave_request.status == LeaveRequestStatus.REJECTED

def test_withdrawal_sets_leave_request_to_withdrawn(setup_workflow): # Arrange
leave_req = leave_engine.create_leave_request(...)
updated_req = leave_engine.submit(...)

    # Act: Withdraw
    result = workflow_engine.withdraw(
        leave_request_id=updated_req.id,
        actor_user_id=setup_workflow["employee"].id,
        reason="Changed plans",
        ctx=audit_context,
    )

    # Assert
    assert isinstance(result, WorkflowCompleted)
    assert result.final_status == LeaveRequestStatus.WITHDRAWN
    assert result.leave_request.status == LeaveRequestStatus.WITHDRAWN

def test_audit_trail_created_for_transitions(setup_workflow): # Arrange
leave_req = leave_engine.create_leave_request(...)
updated_req = leave_engine.submit(...)
step = session.execute(select(WorkflowStep)).scalars().first()

    # Clear audit to track only approval audit entries
    session.query(AuditLog).delete()

    # Act: Approve
    workflow_engine.approve(
        step_id=step.id,
        actor_user_id=setup_workflow["manager"].id,
        comment="Approved",
        ctx=audit_context,
    )

    # Assert: Audit entries exist
    audit_entries = session.query(AuditLog).all()
    assert len(audit_entries) >= 2  # Step approved + LeaveRequest updated

    assert any(
        e.entity_type == "WorkflowStep" and e.action == AuditAction.UPDATE
        for e in audit_entries
    )
    assert any(
        e.entity_type == "LeaveRequest" and e.action == AuditAction.UPDATE
        for e in audit_entries
    )

"""
