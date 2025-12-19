# Workflow State Machine Implementation

## Overview

A complete approval workflow state machine has been implemented for the Leave Management System, ensuring atomicity and correct state transitions.

## Architecture

### State Machine Layers

1. **Workflow Engine** (`app/engines/workflow_engine.py`) - Core state machine logic
2. **Leave Engine** (`app/engines/leave_engine.py`) - Orchestration and workflow instantiation
3. **Repositories** - Persistence with audit emission
4. **API Layer** (`app/api/v1/endpoints/leave_requests.py`) - Thin controllers

## Key Components

### Workflow States

**LeaveRequest Status Flow:**

```
DRAFT → PENDING_APPROVAL → APPROVED
                        ↓
                      REJECTED
                        ↓
                      WITHDRAWN
```

**WorkflowStep Status Transitions:**

```
PENDING → APPROVED → (next step PENDING or WORKFLOW_COMPLETE)
   ↓
REJECTED (terminal)
   ↓
SKIPPED (on withdrawal)
```

### Core Methods

#### 1. Workflow Instantiation (`submit`)

**Location:** `LeaveEngine.submit()`

**Actions:**

- Verifies leave request is in DRAFT status
- Resolves applicable workflow definition
- Determines approvers (currently: request owner's manager)
- Creates ordered WorkflowStep rows (all PENDING initially)
- Transitions LeaveRequest to PENDING_APPROVAL
- Emits audit events for all state changes

**Atomicity:** All steps occur in single transaction; all or nothing.

#### 2. Approval (`approve`)

**Location:** `WorkflowEngine.approve(step_id, actor_user_id, comment)`

**State Invariants:**

- Only assigned approver can act
- Only PENDING steps can be approved
- Only PENDING_APPROVAL leave requests can have steps approved

**Transitions:**

- Mark current step as APPROVED
- **If more steps exist:** Activate next step (PENDING)
- **If final step:** Complete workflow, set LeaveRequest to APPROVED

**Returns:** Union[StepActivated, WorkflowCompleted]

#### 3. Rejection (`reject`)

**Location:** `WorkflowEngine.reject(step_id, actor_user_id, comment)`

**State Invariants:**

- Only assigned approver can act
- Only PENDING steps can be rejected
- Only PENDING_APPROVAL leave requests can have steps rejected

**Transitions:**

- Mark current step as REJECTED (terminal)
- Set LeaveRequest status to REJECTED (terminal)

**Returns:** WorkflowCompleted with status=REJECTED

#### 4. Withdrawal (`withdraw`)

**Location:** `WorkflowEngine.withdraw(leave_request_id, actor_user_id, reason)`

**State Invariants:**

- Only request owner can withdraw
- Only allowed while PENDING_APPROVAL

**Transitions:**

- Set LeaveRequest status to WITHDRAWN (terminal)
- Mark all PENDING steps as SKIPPED

**Returns:** WorkflowCompleted with status=WITHDRAWN

## Atomicity Guarantees

**Request-Scoped Transaction:**

```
FastAPI Request
  ↓
UnitOfWork.__enter__() → session.begin()
  ↓
Engine orchestrates state changes
  ↓
All repositories share same transactional session
  ↓
Audit emission within transaction
  ↓
Request returns successfully
  ↓
UnitOfWork.__exit__() → transaction.commit()
  ↓
Either ALL changes persist or NONE do
```

**Exception Safety:**

```
Exception in workflow logic
  ↓
UnitOfWork.__exit__(exc_type, exc_val, exc_tb)
  ↓
transaction.rollback()
  ↓
session.close()
  ↓
Exception re-raised
```

## Audit Trail

All state transitions emit audit events:

- LeaveRequest status changes
- WorkflowStep creation and transitions
- Actor information (user_id, timestamp)
- Change descriptions and metadata

Events captured:

- `CREATE` - Workflow steps instantiated
- `UPDATE` - Step approval/rejection, request status changes
- `STATUS_CHANGE` - Explicit status transitions
- `APPROVAL` / `REJECTION` - Workflow outcomes

## API Endpoints

### Submit Leave Request

```
POST /api/v1/leave-requests/{request_id}/submit
```

Response:

```json
{
  "id": "uuid",
  "status": "pending_approval",
  "submitted_at": "2025-12-19T10:30:00Z"
}
```

### Approve Workflow Step

```
POST /api/v1/leave-requests/steps/{step_id}/approve
{
  "actor_user_id": "uuid",
  "comment": "Approved by manager"
}
```

Response:

```json
{
  "leave_request_id": "uuid",
  "status": "pending_approval" | "approved",
  "is_final": false | true
}
```

### Reject Workflow Step

```
POST /api/v1/leave-requests/steps/{step_id}/reject
{
  "actor_user_id": "uuid",
  "comment": "Additional days required"
}
```

Response:

```json
{
  "leave_request_id": "uuid",
  "status": "rejected",
  "is_final": true
}
```

### Withdraw Leave Request

```
POST /api/v1/leave-requests/{request_id}/withdraw
{
  "actor_user_id": "uuid",
  "reason": "Changed plans"
}
```

Response:

```json
{
  "leave_request_id": "uuid",
  "status": "withdrawn",
  "is_final": true
}
```

## Validation & Error Handling

**Domain Exceptions (No HTTP layer concerns):**

- `WorkflowStateException` - Invalid state transition
- `ApprovalException` - Approver identity/permission failure
- `WorkflowNotFoundException` - No applicable workflow

**Examples:**

```python
# Cannot approve non-PENDING step
→ WorkflowStateException("Invalid state transition: cannot approve step (expected PENDING)")

# Wrong approver
→ ApprovalException("Only assigned approver can approve this step")

# Request not in submitable state
→ WorkflowStateException("Invalid state transition: submit (only DRAFT requests can be submitted)")
```

## Future Enhancements

NOT implemented in this phase:

- Escalation timers
- SLA enforcement
- Auto-approval rules
- Balance deduction
- RBAC beyond approver identity
- Delegation to other users
- Notification sending

## Testing Scenarios

### Happy Path: Multi-Step Approval

1. Create leave request (DRAFT)
2. Submit request → Instantiate workflow with 2 approvers (PENDING_APPROVAL)
3. First approver approves → Activate second step
4. Second approver approves → Complete workflow (APPROVED)
5. Verify audit trail has 6 events

### Rejection

1. Create and submit leave request
2. First approver rejects → Workflow terminates (REJECTED)
3. No further actions allowed

### Early Withdrawal

1. Create and submit leave request
2. Request owner withdraws → Terminate workflow (WITHDRAWN)
3. Remaining steps marked SKIPPED

## Key Design Decisions

1. **Approver Resolution External:** Workflow engine is agnostic to approver selection; leave engine determines approvers based on policy/hierarchy
2. **Session Sharing:** All repositories in a request use same transactional session
3. **Audit Emission:** Performed by repositories during mutations, within transaction
4. **No Transaction Logic in Engines:** Engines remain pure domain logic; UnitOfWork handles boundaries
5. **Type-Safe Union Returns:** Approve returns `StepActivated | WorkflowCompleted` to distinguish final vs intermediate transitions
