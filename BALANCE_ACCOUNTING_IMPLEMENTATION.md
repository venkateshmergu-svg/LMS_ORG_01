# Leave Balance Accounting Implementation

## Summary

Implemented correct leave balance accounting that enforces strict invariants and auditable state transitions tied to the workflow lifecycle.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ LeaveEngine (Orchestrates leave requests)               │
├─────────────────────────────────────────────────────────┤
│  • create_leave_request()                               │
│  • submit() ──→ BalanceEngine.on_submit()              │
│  • approve_step() ──→ BalanceEngine.on_approve()       │
│  • reject_step() ──→ BalanceEngine.on_reject()         │
│  • withdraw_request() ──→ BalanceEngine.on_withdraw()  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ BalanceEngine (Leave balance state machine)              │
├─────────────────────────────────────────────────────────┤
│  • on_submit() - Reserve balance (AVAILABLE → PENDING)  │
│  • on_approve() - Consume balance (PENDING → USED)      │
│  • on_reject() - Release balance (PENDING → AVAILABLE)  │
│  • on_withdraw() - Release balance (PENDING → AVAILABLE)│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ LeaveBalanceRepository (Database access)                │
│  • get_current_balance()                                │
│  • update_fields() [emits audit events]                 │
└─────────────────────────────────────────────────────────┘
```

## Balance State Machine

### States

- **AVAILABLE** = opening_balance + accrued + carried_forward + adjusted - used - pending - encashed - expired
- **PENDING** = Days reserved for submitted but unapproved requests
- **USED** = Days consumed by approved requests

### Transitions

```
SUBMIT (Draft → Pending Approval)
├─ Validate: AVAILABLE >= total_days
├─ Action: pending += total_days
└─ Audit: "Reserve {days} days for leave request LR-XXX"

APPROVE (Final Step)
├─ Precondition: pending >= total_days (guaranteed by submit)
├─ Action: pending -= total_days; used += total_days
└─ Audit: "Approve leave request LR-XXX: move {days} from PENDING to USED"

REJECT (Any Step)
├─ Precondition: pending >= total_days
├─ Action: pending -= total_days (release to available)
└─ Audit: "Reject leave request LR-XXX: release {days} from PENDING"

WITHDRAW (Before Approval)
├─ Precondition: pending >= total_days
├─ Action: pending -= total_days (release to available)
└─ Audit: "Withdraw leave request LR-XXX: release {days} from PENDING"
```

## Invariants (STRICT)

1. **AVAILABLE cannot go negative** - Enforced by on_submit() validation
2. **PENDING cannot exceed AVAILABLE + PENDING** - Tracked by model calculation
3. **USED only increases on approval** - No direct mutations to used field
4. **No balance mutation without audit** - All changes via repository emit audit events
5. **Atomic transitions** - All state changes committed together with audit trail via UnitOfWork

## Files Created/Modified

### New Files

- [lms/app/engines/balance_engine.py](lms/app/engines/balance_engine.py) - Balance state machine
- [tests/test_balance_engine.py](tests/test_balance_engine.py) - Unit tests (6 tests, all passing)

### Modified Files

- [lms/app/engines/**init**.py](lms/app/engines/__init__.py) - Exported BalanceEngine
- [lms/app/engines/leave_engine.py](lms/app/engines/leave_engine.py) - Integrated balance calls
- [lms/app/api/deps.py](lms/app/api/deps.py) - Injected BalanceEngine dependency

## Test Coverage

```
test_balance_on_submit_reserves_days()
  ✓ Submitting a leave request reserves days from AVAILABLE to PENDING

test_balance_on_submit_insufficient_balance()
  ✓ Raises InsufficientBalanceException when balance < requested days

test_balance_on_approve_consumes_pending()
  ✓ Approving a leave request moves days from PENDING to USED

test_balance_on_reject_releases_pending()
  ✓ Rejecting a leave request releases days from PENDING

test_balance_on_withdraw_releases_pending()
  ✓ Withdrawing a leave request releases days from PENDING

test_balance_transitions_audit_trail()
  ✓ Each transition is recorded with descriptive audit events
```

## Example Lifecycle

```
User has: AVAILABLE = 10 days

1. SUBMIT request for 3 days
   ├─ Check: AVAILABLE (10) >= 3 ✓
   ├─ Update: AVAILABLE = 10, PENDING = 3, USED = 0
   └─ Audit: "Reserve 3 days for LR-001"

2. APPROVE (1st/final step)
   ├─ Check: PENDING (3) >= 3 ✓
   ├─ Update: AVAILABLE = 10, PENDING = 0, USED = 3
   └─ Audit: "Approve LR-001: move 3 days PENDING → USED"

Result: User can still request AVAILABLE = 7 more days
        Actual leave consumed = USED = 3 days

---

Alternative: REJECT instead of APPROVE

2. REJECT (any step)
   ├─ Update: AVAILABLE = 10, PENDING = 0, USED = 0
   └─ Audit: "Reject LR-001: release 3 days from PENDING"

Result: Days are restored, user can resubmit
```

## Design Principles

1. **No direct DB access** - BalanceEngine uses only repositories
2. **No transaction control** - Committed/rolled back by UnitOfWork
3. **Domain exceptions only** - InsufficientBalanceException, not HTTP errors
4. **Audit-first** - All mutations emit audit events via repository
5. **Separation of concerns** - Balance logic decoupled from workflow logic
6. **Testable** - Engine tested independently with fake repos

## Future Extensions (Out of Scope for Phase 14)

- Accrual jobs (monthly/quarterly schedules)
- Carry-forward rules (expiry windows, limits)
- LOP (Loss of Pay) after balance exhaustion
- Payroll integration
- Auto-approval workflows
- Notifications on approval/rejection

## Success Criteria (Met)

✓ Applying leave reduces AVAILABLE only after approval  
✓ Pending requests reserve balance correctly  
✓ Rejected/withdrawn requests restore balance  
✓ All balance changes are atomic with workflow  
✓ Complete audit trail for all transitions  
✓ Strict invariants enforced  
✓ Production-quality code with tests
