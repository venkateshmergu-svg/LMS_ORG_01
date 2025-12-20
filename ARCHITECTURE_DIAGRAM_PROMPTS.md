# LMS Architecture Diagram Prompts

This document contains detailed prompts for generating logical and physical architecture diagrams using tools like Mermaid, draw.io, or other diagram generators.

---

## 1. LOGICAL ARCHITECTURE DIAGRAM (Component Overview)

### Prompt

Copy and use the following prompt:

```
Create a component architecture diagram for a Leave Management System with the following layers and components:

PRESENTATION LAYER (top):
- FastAPI Application (main.py)
- HTTP Endpoints:
  - Leave Requests Controller (POST, GET, PUT operations)
  - Users Controller (User CRUD)
  - Audit Controller (Audit log queries)

API/MIDDLEWARE LAYER (below Presentation):
- Dependency Injection Factory (deps.py)
- JWT Token Validation
- RBAC Middleware (role-based access control)
- Audit Context Provider

BUSINESS LOGIC LAYER (Core Engines):
- Leave Engine (orchestrates leave request lifecycle)
- Policy Engine (evaluates policies, eligibility, balance)
- Workflow Engine (state machine for approvals)
- Balance Engine (accounting for leave balances)
- Audit Engine (audit trail queries)
- User Engine (user management)

DATA ACCESS LAYER (Repositories):
- Repository Factory
- User Repositories (User, Organization, Department)
- Leave Repositories (Request, Type, Policy, Balance, Comments)
- Workflow Repositories (Configuration, Steps, Delegation)
- Audit Repository (append-only audit log)
- Calendar & Notification Repositories

DATA MODEL LAYER (ORM):
- SQLAlchemy Base Models
- Domain Entities (User, LeaveRequest, LeavePolicy, WorkflowStep, etc.)

DATABASE LAYER (bottom):
- PostgreSQL Database
- Connection Pool
- Audit Log Table

TRANSACTION MANAGEMENT (cross-cutting):
- Unit of Work Pattern (manages transaction lifecycle)

Show arrows indicating:
- HTTP requests flowing down from clients
- Controllers calling Engines
- Engines calling Repositories
- Repositories calling Database
- Audit events flowing up from mutations
- Dependencies injected at API layer
```

---

## 2. PHYSICAL ARCHITECTURE DIAGRAM

### Prompt

Copy and use the following prompt:

```
Create a deployment/physical architecture diagram for the Leave Management System showing:

EXTERNAL SERVICES (top-left):
- OAuth2/OIDC Provider (Azure AD, Okta)
- External IdP (Identity Provider)

CLIENT APPLICATIONS (top):
- Web Browser
- Mobile App
- Third-party Integrations

LOAD BALANCER (optional - for scale)

APPLICATION SERVERS:
- Uvicorn/FastAPI Server (Port 8000)
  - Runs on: Python 3.12+
  - Framework: FastAPI
  - Contains: API layer, Engines, Repositories

CACHE LAYER:
- Redis (Port 6379)
  - Broker for Celery (DB: 1)
  - Result Backend (DB: 2)
  - Session cache (optional, DB: 0)

ASYNC WORKER POOL:
- Celery Workers (multiple instances)
  - Task: Accrual Processing
  - Task: Notification Delivery

PRIMARY DATABASE:
- PostgreSQL (Port 5432)
  - Tables: Users, LeaveRequests, Policies, WorkflowSteps, AuditLogs
  - Backup: automated snapshots

CONFIGURATION MANAGEMENT:
- .env file (local) or Vault (production)
  - DATABASE_URL
  - SECRET_KEY
  - REDIS_URL
  - CELERY settings
  - OAuth2 credentials

MIGRATION TOOL:
- Alembic (runs at startup or manual)

Show network flows:
- Clients → Load Balancer → API Server
- API Server → PostgreSQL (read/write)
- API Server ← PostgreSQL (query results)
- API Server → Redis (broker connection)
- Celery Workers ← Redis (task queue)
- Celery Workers → PostgreSQL (domain operations)
- API Server → IdP (token validation)
```

---

## 3. DATA FLOW DIAGRAM (Leave Request Submission Flow)

### Prompt

Copy and use the following prompt:

```
Create a detailed data flow diagram for a leave request submission workflow:

ACTOR: Employee User

STEP 1 - INITIATION:
[Employee] --HTTP POST /api/v1/leave-requests/submit--> [FastAPI Endpoint]

STEP 2 - AUTHENTICATION & AUTHORIZATION:
[Endpoint] --validate JWT--> [Security Module]
[Security Module] --decode token--> [JWT Validator]
[JWT Validator] --return AuthenticatedUser--> [Endpoint]
[Endpoint] --check role--> [RBAC Module]
[RBAC Module] --verify EMPLOYEE role--> [Endpoint]

STEP 3 - DEPENDENCY INJECTION:
[Endpoint] <--inject--> [Dependency Factory]
[Dependency Factory] --create--> [Unit of Work]
[Unit of Work] --create session--> [Database Connection Pool]
[Dependency Factory] --create--> [Audit Context]
[Dependency Factory] --create--> [Leave Engine]

STEP 4 - BUSINESS LOGIC ORCHESTRATION:
[Endpoint] --call submit()--> [Leave Engine]
[Leave Engine] --get user--> [User Repository]
[User Repository] --query--> [PostgreSQL]
[Leave Engine] --resolve policy--> [Policy Engine]
[Policy Engine] --get balance--> [Balance Repository]
[Balance Repository] --query--> [PostgreSQL]
[Leave Engine] --validate state--> [Workflow Engine]

STEP 5 - PERSISTENCE & AUDIT:
[Leave Engine] --update status--> [Leave Request Repository]
[Leave Request Repository] --emit audit--> [Audit Repository]
[Audit Repository] --INSERT--> [PostgreSQL: AuditLog Table]
[Leave Request Repository] --INSERT/UPDATE--> [PostgreSQL: LeaveRequest Table]
[Balance Engine] --hold balance--> [Balance Repository]
[Balance Repository] --INSERT--> [PostgreSQL: BalanceTransaction Table]

STEP 6 - TRANSACTION COMMIT:
[Unit of Work] --commit()--> [Database Transaction]
[Database Transaction] --COMMIT--> [PostgreSQL]

STEP 7 - ASYNC TASKS (Fire & Forget):
[Leave Engine] --publish event--> [Redis Task Queue]
[Celery Worker] --consume--> [Redis Task Queue]
[Celery Worker] --send email--> [Notification Service]

STEP 8 - RESPONSE:
[Leave Engine] --return result--> [Endpoint]
[Endpoint] --HTTP 200 + JSON--> [Employee]
[Employee] <--receive confirmation--> [Browser]

Show data structures:
- Request payload contains: leave_type_id, start_date, end_date, reason
- Response contains: request_id, status, confirmation_message
- Audit event contains: actor_id, action, entity_id, timestamp, changes
```

---

## 4. COMP

Copy and use the following promptONENT DEPENDENCY DIAGRAM (Engine Dependencies)

### Prompt:

```
Create a component dependency diagram showing how Engines depend on Repositories:

CENTER: LeaveEngine
├── depends on: UserRepository
├── depends on: LeaveTypeRepository
├── depends on: LeaveRequestRepository
├── depends on: LeaveRequestDateRepository
├── depends on: LeaveRequestCommentRepository
├── depends on: PolicyEngine
│   ├── depends on: LeavePolicyRepository
│   ├── depends on: PolicyAssignmentRepository
│   └── depends on: LeaveBalanceRepository
└── depends on: WorkflowEngine
    ├── depends on: WorkflowConfigurationRepository
    ├── depends on: WorkflowStepRepository
    ├── depends on: DelegationRepository
    ├── depends on: UserRepository
    ├── depends on: LeaveRequestRepository
    └── depends on: AuditRepository

BalanceEngine:
├── depends on: LeaveBalanceRepository
└── depends on: AuditRepository

UserEngine:
└── depends on: UserRepository

AuditEngine:
└── depends on: AuditRepository

All Engines:
├── receive: Session (from Unit of Work)
├── receive: AuditContext (from DI)
└── emit: audit events through repositories

All Repositories:
├── operate on: same Session (transactional)
├── emit audit through: AuditRepository
└── manage: SQLAlchemy ORM models

Show flow:
- Arrows pointing from Engines to Repositories
- Solid lines for hard dependencies
- Colors: Green for Engines, Blue for Repositories, Red for cross-cutting concerns
```

---

## 5. DATA

Copy and use the following promptBASE SCHEMA DIAGRAM (Logical Data Model)

### Prompt:

```
Create an entity-relationship diagram (ERD) showing the Leave Management System database schema:

ENTITIES:

Users Table:
- id (UUID, PK)
- email (String, unique)
- first_name, last_name
- status (active/inactive)
- organization_id (FK → Organization)
- department_id (FK → Department)
- created_at, updated_at, is_deleted

Organization Table:
- id (UUID, PK)
- name
- settings (JSONB)

Department Table:
- id (UUID, PK)
- name
- organization_id (FK)

LeaveRequest Table:
- id (UUID, PK)
- request_number (unique)
- user_id (FK → User)
- leave_type_id (FK → LeaveType)
- policy_id (FK → LeavePolicy)
- status (draft/submitted/approved/rejected/withdrawn)
- start_date, end_date
- total_days
- reason
- created_at, updated_at

LeaveRequestDate Table:
- id (UUID, PK)
- leave_request_id (FK → LeaveRequest)
- leave_date
- day_value (1.0 or 0.5)

LeaveRequestComment Table:
- id (UUID, PK)
- leave_request_id (FK → LeaveRequest)
- user_id (FK → User)
- comment_text
- is_internal (boolean)
- created_at

LeaveType Table:
- id (UUID, PK)
- name (Casual, Sick, etc.)
- description
- organization_id (FK)
- is_active

LeavePolicy Table:
- id (UUID, PK)
- leave_type_id (FK → LeaveType)
- organization_id (FK)
- max_days_per_year
- carry_forward_limit
- carry_forward_expiry_months
- min_advance_notice_days
- is_active
- effective_from

PolicyAssignment Table:
- id (UUID, PK)
- policy_id (FK → LeavePolicy)
- user_id (FK → User, nullable)
- department_id (FK → Department, nullable)
- priority
- effective_from

LeaveBalance Table:
- id (UUID, PK)
- user_id (FK → User)
- leave_type_id (FK → LeaveType)
- available
- held (pending approvals)
- consumed
- carried_forward
- expiring_soon
- as_of_date

BalanceTransaction Table:
- id (UUID, PK)
- leave_balance_id (FK)
- transaction_type (accrual/debit/adjustment)
- amount
- reference_id (leave_request_id)
- created_at

WorkflowConfiguration Table:
- id (UUID, PK)
- name
- organization_id (FK)
- is_active

WorkflowStep Table:
- id (UUID, PK)
- workflow_id (FK → WorkflowConfiguration)
- step_number
- approver_user_id (FK → User, nullable)
- approver_role (MANAGER, HR_ADMIN, etc.)
- status (pending/approved/rejected)
- leave_request_id (FK → LeaveRequest)

Delegation Table:
- id (UUID, PK)
- delegator_id (FK → User)
- delegatee_id (FK → User)
- delegation_type (full/partial)
- start_date, end_date
- created_at

AuditLog Table (append-only):
- id (UUID, PK)
- entity_type (User, LeaveRequest, LeaveBalance, etc.)
- entity_id (UUID)
- action (CREATE, UPDATE, DELETE, APPROVE, REJECT)
- actor_id (FK → User)
- old_values (JSONB)
- new_values (JSONB)
- timestamp (index)
- request_id (correlation)
- organization_id (for multi-tenancy)

HolidayCalendar Table:
- id (UUID, PK)
- name
- organization_id (FK)

Holiday Table:
- id (UUID, PK)
- calendar_id (FK → HolidayCalendar)
- holiday_date
- description

NotificationTemplate Table:
- id (UUID, PK)
- template_name
- subject_template
- body_template
- channels (email, sms, push)

Notification Table:
- id (UUID, PK)
- user_id (FK → User)
- template_id (FK → NotificationTemplate)
- status (pending/sent/failed)
- created_at, sent_at

RELATIONSHIPS:
- One User has many LeaveRequests
- One Organization has many Departments
- One Department has many Users
- One LeaveType has many LeaveRequests
- One LeaveRequest has many LeaveRequestDates
- One LeaveRequest has many LeaveRequestComments
- One LeavePolicy applies to many LeaveRequests
- One LeaveBalance tracks balance per (User, LeaveType)
- One LeaveBalance has many BalanceTransactions
- One WorkflowConfiguration has many WorkflowSteps
- One WorkflowStep has one Approver (User)
- One Delegation covers one delegator and delegatee pair
- All mutations create AuditLog entries
```

---

Copy and use the following prompt

## 6. SEQUENCE DIAGRAM (Leave Request Approval Flow)

### Prompt:

```
Create a sequence diagram showing the complete leave request approval workflow:

ACTORS/SYSTEMS:
- Employee
- Manager (Approver)
- LeaveEngine
- WorkflowEngine
- BalanceEngine
- Repository Layer
- PostgreSQL Database
- Celery Task Queue

SEQUENCE:

1. Employee submits leave request
   Employee ->> LeaveEngine: submit(request_id)

2. LeaveEngine validates and transitions status
   LeaveEngine ->> WorkflowEngine: activate_workflow(request_id)

3. WorkflowEngine creates workflow step for Manager
   WorkflowEngine ->> LeaveRequestRepository: get(request_id)
   LeaveRequestRepository ->> PostgreSQL: SELECT * FROM leave_request
   PostgreSQL -->> LeaveRequestRepository: LeaveRequest object
   LeaveRequestRepository -->> WorkflowEngine: LeaveRequest

4. WorkflowEngine creates and persists approval step
   WorkflowEngine ->> WorkflowStepRepository: create(step)
   WorkflowStepRepository ->> PostgreSQL: INSERT INTO workflow_step
   WorkflowStepRepository ->> AuditRepository: emit_audit(CREATE, step)
   AuditRepository ->> PostgreSQL: INSERT INTO audit_log

5. BalanceEngine holds balance
   LeaveEngine ->> BalanceEngine: on_submit(request)
   BalanceEngine ->> LeaveBalanceRepository: hold_balance(user_id, amount)
   LeaveBalanceRepository ->> PostgreSQL: UPDATE leave_balance
   LeaveBalanceRepository ->> AuditRepository: emit_audit(UPDATE, balance)

6. Transaction commits
   LeaveEngine ->> UnitOfWork: commit()
   UnitOfWork ->> PostgreSQL: COMMIT TRANSACTION

7. Async notification task enqueued
   LeaveEngine ->> Redis: enqueue_task(send_notification)
   Redis -->> CeleryWorker: dequeue task
   CeleryWorker ->> NotificationService: send_email(manager)

8. Manager reviews and approves
   Manager ->> LeaveEngine: approve_step(step_id)

9. LeaveEngine delegates to WorkflowEngine
   LeaveEngine ->> WorkflowEngine: approve(step_id, actor_user_id)

10. WorkflowEngine updates step status
    WorkflowEngine ->> WorkflowStepRepository: update(step, status=APPROVED)
    WorkflowStepRepository ->> PostgreSQL: UPDATE workflow_step
    WorkflowStepRepository ->> AuditRepository: emit_audit(APPROVE, step)

11. Check if workflow complete
    WorkflowEngine ->> WorkflowStepRepository: get_pending_steps(request_id)
    WorkflowStepRepository ->> PostgreSQL: SELECT FROM workflow_step WHERE status=PENDING
    PostgreSQL -->> WorkflowStepRepository: [] (no pending steps)
    WorkflowStepRepository -->> WorkflowEngine: []

12. Mark request as approved
    WorkflowEngine ->> LeaveRequestRepository: update(request, status=APPROVED)
    LeaveRequestRepository ->> PostgreSQL: UPDATE leave_request
    LeaveRequestRepository ->> AuditRepository: emit_audit(APPROVE, request)

13. BalanceEngine debits balance
    LeaveEngine ->> BalanceEngine: on_approve(request)
    BalanceEngine ->> LeaveBalanceRepository: debit_balance(user_id, held_amount)
    LeaveBalanceRepository ->> PostgreSQL: UPDATE leave_balance
    LeaveBalanceRepository ->> BalanceTransactionRepository: record(debit_transaction)
    BalanceTransactionRepository ->> PostgreSQL: INSERT INTO balance_transaction
    BalanceTransactionRepository ->> AuditRepository: emit_audit(CREATE, transaction)

14. All changes committed atomically
    LeaveEngine ->> UnitOfWork: commit()
    UnitOfWork ->> PostgreSQL: COMMIT TRANSACTION

15. Async notification to employee
    LeaveEngine ->> Redis: enqueue_task(send_approval_email)
    Redis -->> CeleryWorker: dequeue task
    CeleryWorker ->> NotificationService: send_email(employee, "Approved")

16. Response sent to manager
    LeaveEngine -->> Manager: LeaveRequest(status=APPROVED)

NOTES:
- All database operations within single UnitOfWork transaction
- Either all changes commit or all rollback
- Audit events created for every mutation
- Async tasks fire after transaction commits
- Manager sees updated status on their dashboard
```

---

Copy and use the following prompt

## 7. AUTHENTICATION & AUTHORIZATION FLOW

### Prompt:

```
Create a sequence diagram for authentication and authorization flow:

ACTORS/SYSTEMS:
- Client (Browser/App)
- FastAPI Endpoint
- OAuth2/OIDC Provider (IdP)
- Security Module
- RBAC Module
- User Repository
- PostgreSQL Database

FLOW:

1. Client sends HTTP request with Authorization header
   Client ->> FastAPI Endpoint: GET /api/v1/leave-requests/123
   Client header: Authorization: Bearer <jwt_token>

2. Endpoint invokes security dependency
   FastAPI Endpoint ->> Security Module: get_authenticated_user(token)

3. Security module extracts token
   Security Module ->> Security Module: extract_token_from_header()

4. Validate token signature and expiry
   Security Module ->> Security Module: decode_token(token)
   Security Module ->> Security Module: verify_signature(hs256_key or jwks)

5. If external IdP configured, fetch JWKS
   Security Module ->> IdP: GET /.well-known/openid-configuration
   IdP -->> Security Module: jwks_uri
   Security Module ->> IdP: GET /jwks.json
   IdP -->> Security Module: public_keys

6. Map token claims to User
   Security Module ->> User Repository: get_or_create_by_email(email_from_token)
   User Repository ->> PostgreSQL: SELECT * FROM user WHERE email = ?
   PostgreSQL -->> User Repository: User object (or NULL)

7. If user doesn't exist, create
   User Repository ->> User Repository: create_user(from_token)
   User Repository ->> PostgreSQL: INSERT INTO user
   User Repository ->> AuditRepository: emit_audit(CREATE, user)

8. Return AuthenticatedUser context
   Security Module -->> FastAPI Endpoint: AuthenticatedUser(user_id, email, roles)

9. Endpoint invokes RBAC dependency
   FastAPI Endpoint ->> RBAC Module: get_rbac_context(auth_user)
   RBAC Module -->> FastAPI Endpoint: RBACContext(user_id, roles, has_role())

10. Endpoint checks role requirement
    FastAPI Endpoint ->> RBAC Module: rbac.has_role(EMPLOYEE, MANAGER)
    RBAC Module ->> RBAC Module: check_role_hierarchy()
    RBAC Module -->> FastAPI Endpoint: true/false

11. If role check fails
    FastAPI Endpoint ->> FastAPI Endpoint: raise HTTPException(403)
    FastAPI Endpoint -->> Client: HTTP 403 Forbidden

12. Endpoint performs ownership check (if needed)
    FastAPI Endpoint ->> LeaveEngine: get_leave_request(request_id)
    LeaveEngine ->> LeaveRequestRepository: get(request_id)
    LeaveRequestRepository ->> PostgreSQL: SELECT * FROM leave_request
    PostgreSQL -->> LeaveRequestRepository: LeaveRequest
    LeaveRequestRepository -->> LeaveEngine: LeaveRequest
    LeaveEngine -->> FastAPI Endpoint: LeaveRequest(user_id=X)

    FastAPI Endpoint ->> FastAPI Endpoint: verify(request.user_id == rbac.user_id)

13. If ownership check fails
    FastAPI Endpoint ->> FastAPI Endpoint: raise HTTPException(403, "Not owner")
    FastAPI Endpoint -->> Client: HTTP 403 Forbidden

14. All checks pass, call engine
    FastAPI Endpoint ->> LeaveEngine: approve_step(step_id, actor_user_id=rbac.user_id)
    (proceeds with normal business logic)

15. Response returned
    LeaveEngine -->> FastAPI Endpoint: result
    FastAPI Endpoint -->> Client: HTTP 200 + JSON

ROLE HIERARCHY:
- EMPLOYEE: Basic leave operations
- MANAGER: Approval of team requests
- HR_ADMIN: Policy configuration
- SYSTEM_ADMIN: User and role management
- AUDITOR: Read-only audit log

FAILURE SCENARIOS:
- Invalid/expired token → HTTP 401 Unauthorized
- Valid token but insufficient role → HTTP 403 Forbidden
- Valid token but resource not owned → HTTP 403 Forbidden
- User inactive → HTTP 403 Forbidden
```

Copy and use the following prompt

---

## 8. TRANSACTION & AUDIT FLOW

### Prompt:

```
Create a diagram showing transaction management and audit trail generation:

SCENARIO: Leave Request Submission (Multiple Changes)

STEP 1: UnitOfWork Created
UnitOfWork.__init__(session)
├── session.begin() NOT called yet
└── state: not_started

STEP 2: Endpoint Executes Multiple Operations
[LeaveEngine] calls [LeaveRequestRepository.add()]
  └─ LeaveRequest table: INSERT new row
  └─ LeaveRequestRepository: emit_audit(CREATE)
     └─ AuditRepository: INSERT audit_log
  └─ state: pending (in transaction)

[BalanceEngine] calls [LeaveBalanceRepository.update()]
  └─ LeaveBalance table: UPDATE row
  └─ BalanceTransactionRepository: INSERT ledger row
  └─ AuditRepository: INSERT audit_log (2 events)
  └─ state: pending

[WorkflowEngine] calls [WorkflowStepRepository.add()]
  └─ WorkflowStep table: INSERT new row
  └─ AuditRepository: INSERT audit_log
  └─ state: pending

CRITICAL INVARIANT:
All above operations share the SAME database session
└─ All changes in single transaction
└─ All share same connection from pool
└─ No intermediate commits

STEP 3: Check for Errors
If ANY error occurs:
  └─ UnitOfWork.__exit__(exception)
     ├─ transaction.rollback()
     ├─ session.close()
     └─ state: rolled_back

  DATABASE RESULT:
  ├─ LeaveRequest: NOT INSERTED
  ├─ LeaveBalance: NOT UPDATED
  ├─ BalanceTransaction: NOT INSERTED
  ├─ WorkflowStep: NOT INSERTED
  └─ AuditLog: ALL ROLLED BACK (atomicity guaranteed)

STEP 4: All Operations Succeed
UnitOfWork.__exit__(no_exception)
├─ transaction.commit()
│  ├─ PostgreSQL: BEGIN TRANSACTION (implicit)
│  ├─ PostgreSQL: INSERT into leave_request
│  ├─ PostgreSQL: UPDATE leave_balance
│  ├─ PostgreSQL: INSERT into balance_transaction
│  ├─ PostgreSQL: INSERT into workflow_step
│  ├─ PostgreSQL: INSERT into audit_log (4 events)
│  └─ PostgreSQL: COMMIT TRANSACTION
├─ session.close()
└─ state: committed

DATABASE FINAL STATE:
├─ leave_request: [id, user_id, status, ...]
├─ leave_balance: [available=X, held=Y, ...]
├─ balance_transaction: [id, amount, type, reference_id, ...]
├─ workflow_step: [id, step_number, approver, status, ...]
└─ audit_log (4 rows):
   ├─ action=CREATE, entity_type=LeaveRequest, entity_id=UUID1, timestamp=T1, actor_id=USER1
   ├─ action=UPDATE, entity_type=LeaveBalance, entity_id=UUID2, old_values={...}, new_values={...}, timestamp=T2
   ├─ action=CREATE, entity_type=BalanceTransaction, entity_id=UUID3, timestamp=T3
   └─ action=CREATE, entity_type=WorkflowStep, entity_id=UUID4, timestamp=T4

AUDIT TRAIL GUARANTEES:
1. **Append-only**: No UPDATE/DELETE on audit_log
2. **Correlation**: All events for one operation share request_id
3. **Immutable**: old_values/new_values captured as JSONB snapshots
4. **Ordered**: timestamp + id ensures chronological order
5. **Actor tracking**: All events attributed to authenticated user
6. **Organization isolation**: Multi-tenancy support via org_id

AFTER COMMIT:
├─ HTTP response sent to client
├─ Async tasks published to Redis
│  └─ Celery worker processes background jobs
├─ Downstream systems notified (via webhooks if configured)
└─ Audit log queryable for compliance/debugging

ROLLBACK SCENARIO (Example - InsufficientBalanceException):
IF balance_check fails DURING on_approve():
├─ BalanceEngine.on_approve() raises InsufficientBalanceException
├─ Exception propagates to endpoint
├─ UnitOfWork context manager catches exception
├─ UnitOfWork.rollback() called
├─ PostgreSQL: ROLLBACK TRANSACTION
├─ Nothing persisted (including partial audit events)
├─ HTTP 400 response sent to client with error message
└─ Retry with different leave type or different dates

PERFORMANCE CONSIDERATIONS:
- Single transaction: ≤ 1000ms typical
- Connection from pool: reused, no TCP overhead
- Audit inserts: minimal overhead (simple append)
- Rollback: faster than commit (no disk I/O for aborted changes)
```

Copy and use the following prompt

---

## 9. MULTI-LAYERED CALL STACK DIAGRAM

### Prompt:

```
Create a detailed call stack diagram showing how a leave request approval flows through all layers:

REQUEST: POST /api/v1/leave-requests/{request_id}/approve
ACTOR: Manager User

LAYER 1 - HTTP & ROUTING:
├─ FastAPI Router
│  └─ Match: POST /api/v1/leave-requests/{request_id}/approve
│  └─ Handler: endpoints.leave_requests.approve_step()

LAYER 2 - DEPENDENCY INJECTION:
├─ resolve: rbac: RBACContext
│  └─ Depends(require_roles(MANAGER))
│  └─ get_authenticated_user()
│     └─ decode JWT token
│     └─ validate signature
│     └─ return AuthenticatedUser
│  └─ get_rbac_context()
│     └─ wrap in RBACContext
│     └─ check role: MANAGER ✓
├─ resolve: engine: LeaveEngine
│  └─ Depends(get_leave_engine)
│  └─ create UnitOfWork
│  └─ create all Repositories
│  └─ create Engines
│  └─ wire all dependencies
├─ resolve: ctx: AuditContext
│  └─ Depends(get_audit_context)
│  └─ extract headers (x_actor_id, x_request_id)
│  └─ include auth_user from jwt

LAYER 3 - ENDPOINT CONTROLLER:
├─ endpoint.approve_step(request_id, step_id, rbac, engine, ctx)
│  └─ get_leave_request(request_id)
│     └─ call engine
│     └─ check ownership: request.user_id != rbac.user_id → error
│     └─ verify request status == SUBMITTED ✓
│  └─ call engine.approve_step(
│        step_id=step_id,
│        actor_user_id=rbac.user_id,
│        comment=None,
│        ctx=ctx
│     )

LAYER 4 - LEAVE ENGINE (Orchestration):
├─ LeaveEngine.approve_step()
│  ├─ 1. Fetch step from DB
│  │  └─ step_repo.get(step_id)
│  │     └─ WorkflowStepRepository.get()
│  │        └─ session.get(WorkflowStep, step_id)
│  │        └─ return WorkflowStep object
│  │
│  ├─ 2. Fetch leave request
│  │  └─ request_repo.get(leave_request_id)
│  │     └─ return LeaveRequest
│  │
│  ├─ 3. Delegate to WorkflowEngine
│  │  └─ workflow_engine.approve(
│  │        step_id=step_id,
│  │        actor_user_id=rbac.user_id,
│  │        comment=None,
│  │        ctx=ctx
│  │     )
│  │
│  ├─ 4. Delegate to BalanceEngine
│  │  └─ balance_engine.on_approve(leave_request, ctx)
│  │
│  ├─ 5. Return result
│  │  └─ return dict with status, message

LAYER 5 - WORKFLOW ENGINE (State Machine):
├─ WorkflowEngine.approve()
│  ├─ 1. Validate step status
│  │  └─ assert step.status == PENDING
│  │
│  ├─ 2. Update step status
│  │  └─ step_repo.update(step, status=APPROVED, ctx=ctx)
│  │     └─ session.merge(step) # attach to session
│  │     └─ session.flush()
│  │     └─ emit_audit(action=APPROVE, entity=step, ctx=ctx)
│  │        └─ audit_repo.create(
│  │             entity_type='WorkflowStep',
│  │             entity_id=step.id,
│  │             action='APPROVE',
│  │             actor_id=rbac.user_id,
│  │             new_values={'status': 'APPROVED'},
│  │             timestamp=now()
│  │          )
│  │           └─ session.add(audit_log_entry)
│  │           └─ return
│  │
│  ├─ 3. Check for remaining pending steps
│  │  └─ pending_steps = step_repo.get_pending_steps(leave_request_id)
│  │     └─ query: WHERE leave_request_id=? AND status='PENDING'
│  │     └─ return []
│  │
│  ├─ 4. If no pending steps, mark request as approved
│  │  └─ request_repo.update(request, status=APPROVED, ctx=ctx)
│  │     └─ session.merge(request)
│  │     └─ session.flush()
│  │     └─ emit_audit(action=APPROVE, entity=request)
│  │        └─ audit_repo.create(...)
│  │
│  └─ 5. Return completion event
│     └─ return WorkflowCompleted(request_id=..., status=APPROVED)

LAYER 6 - BALANCE ENGINE (Accounting):
├─ BalanceEngine.on_approve()
│  ├─ 1. Get current balance
│  │  └─ balance_repo.get_current_balance(user_id, leave_type_id)
│  │     └─ query: LeaveBalance WHERE user_id=? AND leave_type_id=?
│  │     └─ return balance object
│  │
│  ├─ 2. Calculate debit amount
│  │  └─ days_to_debit = leave_request.total_days
│  │
│  ├─ 3. Validate sufficient balance
│  │  └─ if balance.available + balance.held < days_to_debit:
│  │        └─ raise InsufficientBalanceException()
│  │           └─ triggers UnitOfWork.rollback()
│  │           └─ HTTP 400 returned
│  │
│  ├─ 4. Update balance (debit)
│  │  └─ balance.held -= days_to_debit
│  │  └─ balance.consumed += days_to_debit
│  │  └─ balance_repo.update(balance, ctx=ctx)
│  │     └─ session.merge(balance)
│  │     └─ session.flush()
│  │     └─ emit_audit(action=UPDATE, entity=balance)
│  │        └─ audit_repo.create(..., old_values=..., new_values=...)
│  │
│  ├─ 5. Create balance transaction ledger entry
│  │  └─ txn = BalanceTransaction(
│  │        leave_balance_id=balance.id,
│  │        transaction_type='DEBIT',
│  │        amount=days_to_debit,
│  │        reference_id=leave_request.id
│  │     )
│  │  └─ txn_repo.add(txn, ctx=ctx)
│  │     └─ session.add(txn)
│  │     └─ session.flush()
│  │     └─ emit_audit(action=CREATE, entity=txn)
│  │
│  └─ 6. Return (no return value)

LAYER 7 - REPOSITORY LAYER (Data Access):
├─ All repositories share same Session (from UnitOfWork)
├─ All flush() calls write to session (not yet committed)
├─ All emit_audit() calls go through AuditRepository
│  └─ AuditRepository queues audit events in same session
├─ No actual database writes yet

LAYER 8 - TRANSACTION MANAGEMENT:
├─ UnitOfWork context manager (from FastAPI dependency)
├─ Python's with statement exit:
│  └─ if no exception:
│     └─ session.commit()  ← EVERYTHING WRITTEN TO DB ATOMICALLY
│  └─ else:
│     └─ session.rollback()  ← EVERYTHING ROLLED BACK

LAYER 9 - DATABASE:
├─ PostgreSQL receives COMMIT
├─ All pending inserts/updates executed
├─ Single ACID transaction guaranteed
├─ Changes visible to other transactions

LAYER 10 - RESPONSE & SIDE EFFECTS:
├─ endpoint constructs response DTO
├─ publish async tasks (email notification)
├─ return HTTP 200 + JSON to client

SUMMARY OF CHANGES IN DATABASE:
├─ workflow_step: status PENDING → APPROVED
├─ leave_request: status SUBMITTED → APPROVED
├─ leave_balance: held -5, consumed +5
├─ balance_transaction: new DEBIT entry
├─ audit_log: 4 new entries (APPROVE step, UPDATE balance, DEBIT transaction, APPROVE request)
├─ All committed atomically or all rolled back
```

Copy and use the following prompt

---

## 10. ORGANIZATIONAL STRUCTURE & MULTI-TENANCY

### Prompt:

```
Create a diagram showing multi-tenancy and organizational hierarchy:

ROOT: Organization (Company)
├─ id: UUID
├─ name: "Acme Corp"
├─ settings: JSONB (policy defaults, leave types, etc.)
│
├─ DEPARTMENTS (within org):
│  ├─ Engineering
│  ├─ Sales
│  ├─ HR
│  └─ Finance
│
├─ USERS (within org):
│  ├─ Engineering Team:
│  │  ├─ Employee A (EMPLOYEE role)
│  │  ├─ Employee B (EMPLOYEE role)
│  │  └─ Manager X (MANAGER role, reports from A & B)
│  │
│  ├─ Sales Team:
│  │  ├─ Employee C (EMPLOYEE role)
│  │  ├─ Employee D (EMPLOYEE role)
│  │  └─ Manager Y (MANAGER role)
│  │
│  ├─ HR Team:
│  │  └─ HR Admin (HR_ADMIN role)
│  │
│  └─ System:
│     ├─ System Admin (SYSTEM_ADMIN role)
│     └─ Auditor (AUDITOR role)
│
├─ LEAVE TYPES (within org):
│  ├─ Casual Leave
│  ├─ Sick Leave
│  ├─ Annual Leave
│  └─ Unpaid Leave
│
├─ POLICIES (within org):
│  ├─ Policy for Casual Leave
│  │  └─ max_days_per_year: 10
│  │  └─ carry_forward_limit: 5
│  │
│  ├─ Policy for Sick Leave
│  │  └─ max_days_per_year: 15
│  │  └─ no carry forward
│  │
│  └─ Policy for Annual Leave
│     └─ max_days_per_year: 20
│     └─ carry_forward_limit: 5
│
├─ POLICY ASSIGNMENTS (within org):
│  ├─ Casual: Engineering Dept → 12 days/year
│  ├─ Casual: Sales Dept → 10 days/year
│  ├─ Sick: All Employees → 15 days/year
│  └─ Annual: Employee A → 25 days/year (override)
│
├─ WORKFLOWS (within org):
│  ├─ Standard Approval Workflow:
│  │  ├─ Step 1: Manager approval
│  │  ├─ Step 2: HR verification (if > 5 days)
│  │  └─ Step 3: Finance sign-off (for unpaid)
│  │
│  └─ Executive Workflow:
│     ├─ Step 1: Director approval
│     └─ Step 2: CFO approval
│
├─ HOLIDAY CALENDARS (within org):
│  ├─ National Holidays 2025
│  ├─ Regional Holidays (by location)
│  └─ Company-specific closures
│
└─ AUDIT SCOPE (per organization):
   ├─ All leave requests
   ├─ All balance changes
   ├─ All approvals
   ├─ All policy updates
   └─ Queryable by organization_id

ISOLATION GUARANTEE:
- Each organization has completely separate:
  ├─ Users
  ├─ Departments
  ├─ Leave types and policies
  ├─ Workflows
  ├─ Audit logs
  └─ Balance data

- Query pattern:
  SELECT * FROM leave_request
  WHERE organization_id = authenticated_user.organization_id
  (never cross-org queries)

- Audit security:
  ├─ Only org members can see their org's audit logs
  ├─ AUDITOR role scoped to their organization
  └─ Compliance reports per organization
```

---

## Usage Instructions

### For Mermaid Diagrams

Copy the relevant prompt and use with Mermaid CLI or online editor:

- Mermaid Live Editor: https://mermaid.live
- Mermaid CLI: `npx mermaid-cli`
- VS Code Extension: Mermaid Editor

### For Draw.io Diagrams

- Use prompts as specification documents
- Create diagrams manually or use AI plugins
- Export as SVG/PNG for presentations

### For PlantUML Diagrams

- Convert prompts to PlantUML syntax
- Use PlantUML online editor or generate programmatically

### Best Practices

1. **Start with Logical Architecture** (Prompt #1) for business stakeholders
2. **Add Physical Architecture** (Prompt #2) for infrastructure teams
3. **Use Data Flow** (Prompt #3) for detailed process understanding
4. **Reference Sequence Diagrams** (Prompts #6, #7) for troubleshooting
5. **Combine with Database Schema** (Prompt #5) for data discussions
6. **Use Call Stack** (Prompt #9) for technical deep dives
