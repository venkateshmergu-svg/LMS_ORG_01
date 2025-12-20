# PHASE 23 – FEATURE IMPLEMENTATION & OAUTH2 INTEGRATION

**Leave Management System (LMS) - Feature Development**

**Date:** December 19, 2025  
**Version:** 1.0  
**Status:** Planning & Implementation

---

## OVERVIEW

Phase 23 focuses on implementing core features using the scaffolded architecture from Phase 22. All patterns are established, types are safe, and the foundation is solid. This phase is about rapid feature delivery.

**Core Principles:**
- Backend is the source of truth
- Frontend consumes APIs only
- No business logic in UI
- Type-safe API contracts
- Role-based UX

---

## PRIORITIES (High → Low)

### 🔴 TIER 1 (Critical Path)

1. **OAuth2 Login Flow** — Must be first (gates all features)
2. **Leave Application Form** — Core employee feature
3. **Manager Approval UI** — Core manager feature
4. **Balance Display** — Context for all leave operations

### 🟡 TIER 2 (High Value)

5. **Audit Log Viewer** — HR/Auditor feature
6. **Team Calendar** — Manager feature
7. **HR Admin Dashboard** — Admin feature

### 🟢 TIER 3 (Polish)

8. **Export/Download** — Reports feature
9. **Search & Filters** — Discovery feature
10. **Mobile Optimization** — Responsive design

---

## TIER 1: CRITICAL PATH

### 1. OAuth2 Login Flow

**File:** `src/app/login/LoginPage.tsx`

**What to implement:**
- Redirect to OAuth2 authorization endpoint
- Handle callback with auth code
- Exchange code for access_token + refresh_token
- Store tokens in memory via AuthProvider
- Redirect to dashboard on success
- Display errors on failure

**Backend Contract:**
```
POST /api/v1/auth/token
Body: {
  "grant_type": "authorization_code",
  "code": "...",
  "client_id": "...",
  "redirect_uri": "..."
}
Response: {
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Implementation Steps:**
1. Add OAuth configuration constants
2. Create `redirectToOAuth()` function
3. Create callback handler
4. Implement token exchange
5. Update AuthProvider login
6. Test with backend

---

### 2. Leave Application Form

**File:** `src/app/leave/LeaveApplicationPage.tsx`

**What to implement:**
- Leave type selector (from API)
- Start & end date pickers
- Reason textarea
- Client-side validation
- Balance checking before submit
- Success/error feedback
- useCreateLeaveRequest() mutation

**Form Flow:**
```
1. User selects leave type
2. Fetch available balance for type
3. Validate dates (not in past, valid range)
4. Show available days & impact
5. User submits
6. Mutation calls API
7. On success: Clear form, show toast, redirect
8. On error: Show error message, allow retry
```

**Implementation Steps:**
1. Create form component with React Hook Form
2. Add date picker UI
3. Implement balance check UI
4. Add validation rules
5. Connect useCreateLeaveRequest() hook
6. Handle success/error states
7. Add loading spinner during submission

---

### 3. Manager Approval UI

**File:** `src/features/approvals/components/ApprovalQueue.tsx`

**What to implement:**
- Table of pending approvals
- Click row to see details
- Detail modal with employee info, leave details, balance impact
- Approve button with optional comments
- Reject button (comments required)
- Success/error feedback

**Backend Contract:**
```
GET /api/v1/approvals/pending
Response: {
  "items": [
    {
      "id": "...",
      "leave_request_id": "...",
      "employee_name": "...",
      "leave_type": "ANNUAL",
      "start_date": "2025-01-15",
      "end_date": "2025-01-17",
      "days_requested": 3,
      "status": "PENDING"
    }
  ]
}

POST /api/v1/approvals/{id}/approve
Body: { "comments": "..." }

POST /api/v1/approvals/{id}/reject
Body: { "comments": "..." }
```

**Implementation Steps:**
1. Create `useApprovalsQuery()` hook
2. Build approval table component
3. Create detail modal component
4. Add approve/reject forms
5. Connect mutations
6. Handle state changes
7. Add real-time updates (polling or SSE)

---

### 4. Balance Display Widget

**File:** `src/features/balance/components/BalanceCard.tsx`

**What to implement:**
- Current available balance
- Used balance
- Pending balance
- Visual progress bar
- Last updated timestamp
- Refresh button

**Backend Contract:**
```
GET /api/v1/leave/balance
Response: {
  "employee_id": "...",
  "leave_type": "ANNUAL",
  "total_balance": 20,
  "used": 5,
  "pending": 2,
  "available": 13,
  "last_updated": "2025-12-19T10:00:00"
}
```

**Implementation Steps:**
1. Create `useLeaveBalance()` hook (already done)
2. Build card component with data display
3. Add progress bar visualization
4. Add refresh button
5. Handle loading/error states
6. Add tooltip with breakdown

---

## TIER 2: HIGH VALUE

### 5. Audit Log Viewer

**File:** `src/features/audit/components/AuditLogTable.tsx`

**Features:**
- Searchable table of audit logs
- Filter by entity type, action, user, date range
- Sort by timestamp
- Export to CSV
- Real-time tail mode (optional)

### 6. Team Calendar

**File:** `src/features/approvals/components/TeamCalendar.tsx`

**Features:**
- Calendar view of team's approved leave
- Color-coded by leave type
- Click day to see details
- Filter by team member
- View availability

### 7. HR Admin Dashboard

**File:** `src/app/admin/HRAdminPage.tsx`

**Features:**
- Leave utilization metrics
- Reports & analytics
- HRIS sync trigger
- Payroll export generator
- System health check

---

## IMPLEMENTATION TIMELINE

**Week 1 (Phase 23A) — Tier 1:**
- Day 1: OAuth2 setup & testing
- Day 2-3: Leave form with validation
- Day 4-5: Manager approval UI
- Day 6-7: Balance widget & refinements

**Week 2 (Phase 23B) — Tier 2:**
- Day 1-2: Audit log viewer
- Day 3-4: Team calendar
- Day 5-6: HR admin dashboard
- Day 7: Polish & testing

**Week 3 (Phase 23C) — Testing & Deployment:**
- Day 1-2: Unit tests (Vitest)
- Day 3-4: E2E tests (Playwright)
- Day 5-6: Performance & security audit
- Day 7: Deployment prep

---

## DETAILED IMPLEMENTATION GUIDE

### Step 1: OAuth2 Integration

Create OAuth configuration:

**File:** `src/lib/oauth.ts`

```typescript
export const oauthConfig = {
  clientId: import.meta.env.VITE_OAUTH_CLIENT_ID,
  authority: import.meta.env.VITE_OAUTH_AUTHORITY,
  redirectUri: `${window.location.origin}/auth/callback`,
  scopes: ['openid', 'profile', 'email'],
};

export function getAuthorizationUrl() {
  const params = new URLSearchParams({
    client_id: oauthConfig.clientId,
    redirect_uri: oauthConfig.redirectUri,
    response_type: 'code',
    scope: oauthConfig.scopes.join(' '),
    state: generateRandomState(),
  });
  return `${oauthConfig.authority}/authorize?${params}`;
}

export function generateRandomState() {
  return Math.random().toString(36).substring(7);
}
```

Create callback handler:

**File:** `src/app/auth/CallbackPage.tsx`

```typescript
export function CallbackPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const error = params.get('error');

        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }

        if (!code) {
          throw new Error('No authorization code received');
        }

        // Exchange code for tokens
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grant_type: 'authorization_code',
            code,
            client_id: import.meta.env.VITE_OAUTH_CLIENT_ID,
            redirect_uri: `${window.location.origin}/auth/callback`,
          }),
        });

        if (!response.ok) {
          throw new Error('Token exchange failed');
        }

        const data = await response.json();
        await login(data.access_token, data.refresh_token);
        navigate('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication failed');
      }
    };

    handleCallback();
  }, [login, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card">
          <h1 className="text-2xl font-bold text-error mb-4">Authentication Failed</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => (window.location.href = '/login')}
            className="btn btn-primary"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin mb-4">⏳</div>
        <p>Completing sign in...</p>
      </div>
    </div>
  );
}
```

Update LoginPage:

**File:** `src/app/login/LoginPage.tsx` (update)

```typescript
import { useNavigate } from 'react-router-dom';
import { getAuthorizationUrl } from '@/lib/oauth';

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleOAuthLogin = () => {
    window.location.href = getAuthorizationUrl();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-md w-full card shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">LMS</h1>
          <p className="text-gray-600 dark:text-gray-300">Leave Management System</p>
        </div>

        <button
          onClick={handleOAuthLogin}
          className="w-full btn btn-primary text-lg py-3"
        >
          Sign in with OAuth2
        </button>

        <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
          Securely sign in with your organization account
        </p>
      </div>
    </div>
  );
}
```

Update App routes:

**File:** `src/app/App.tsx` (add route)

```typescript
import { CallbackPage } from '@/app/auth/CallbackPage';

<Route path="/auth/callback" element={<CallbackPage />} />
```

---

### Step 2: Leave Application Form

Create leave form component:

**File:** `src/features/leave/components/LeaveForm.tsx`

```typescript
import { useForm, Controller } from 'react-hook-form';
import { useCreateLeaveRequest } from '@/features/leave/hooks/useLeaveRequests';
import { useLeaveBalance } from '@/features/leave/hooks/useLeaveRequests';
import { differenceInDays } from 'date-fns';

interface LeaveFormData {
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
}

export function LeaveForm({ onSuccess }: { onSuccess?: () => void }) {
  const { control, handleSubmit, watch, formState: { errors } } = useForm<LeaveFormData>({
    defaultValues: {
      leave_type: 'ANNUAL',
      start_date: '',
      end_date: '',
      reason: '',
    },
  });

  const { data: balance } = useLeaveBalance();
  const { mutate, isPending, error } = useCreateLeaveRequest();

  const startDate = watch('start_date');
  const endDate = watch('end_date');

  const daysRequested = startDate && endDate ? differenceInDays(new Date(endDate), new Date(startDate)) + 1 : 0;
  const availableDays = balance?.available || 0;

  const onSubmit = (data: LeaveFormData) => {
    mutate(data, {
      onSuccess: () => {
        onSuccess?.();
      },
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">Leave Type</label>
        <Controller
          name="leave_type"
          control={control}
          rules={{ required: 'Leave type is required' }}
          render={({ field }) => (
            <select {...field} className="input">
              <option value="ANNUAL">Annual Leave</option>
              <option value="SICK">Sick Leave</option>
              <option value="PERSONAL">Personal Leave</option>
            </select>
          )}
        />
        {errors.leave_type && <p className="text-error text-sm mt-1">{errors.leave_type.message}</p>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Start Date</label>
          <Controller
            name="start_date"
            control={control}
            rules={{
              required: 'Start date is required',
              validate: (value) => new Date(value) >= new Date() || 'Cannot apply for past dates',
            }}
            render={({ field }) => <input {...field} type="date" className="input" />}
          />
          {errors.start_date && <p className="text-error text-sm mt-1">{errors.start_date.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">End Date</label>
          <Controller
            name="end_date"
            control={control}
            rules={{
              required: 'End date is required',
              validate: (value) => new Date(value) >= new Date(startDate) || 'End date must be after start date',
            }}
            render={({ field }) => <input {...field} type="date" className="input" />}
          />
          {errors.end_date && <p className="text-error text-sm mt-1">{errors.end_date.message}</p>}
        </div>
      </div>

      {daysRequested > 0 && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Days requested: <span className="font-bold">{daysRequested}</span>
          </p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
            Available balance: <span className={availableDays >= daysRequested ? 'font-bold text-success' : 'font-bold text-error'}>
              {availableDays}
            </span>
          </p>
          {availableDays < daysRequested && (
            <p className="text-sm text-error mt-2">
              ⚠️ Insufficient balance. You need {daysRequested - availableDays} more days.
            </p>
          )}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-2">Reason</label>
        <Controller
          name="reason"
          control={control}
          rules={{ required: 'Please provide a reason' }}
          render={({ field }) => (
            <textarea {...field} rows={4} className="input" placeholder="Why are you taking leave?" />
          )}
        />
        {errors.reason && <p className="text-error text-sm mt-1">{errors.reason.message}</p>}
      </div>

      {error && <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded text-error text-sm">{error.message}</div>}

      <button type="submit" disabled={isPending || availableDays < daysRequested} className="w-full btn btn-primary">
        {isPending ? 'Submitting...' : 'Submit Application'}
      </button>
    </form>
  );
}
```

---

### Step 3: Manager Approval UI

Create approval components:

**File:** `src/features/approvals/components/ApprovalQueue.tsx`

```typescript
import { useApprovalsQuery } from '@/features/approvals/hooks/useApprovalsQuery';
import { ApprovalDetailModal } from './ApprovalDetailModal';
import { useState } from 'react';

export function ApprovalQueue() {
  const { data, isLoading, error } = useApprovalsQuery();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  if (isLoading) return <div>Loading approvals...</div>;
  if (error) return <div className="text-error">Failed to load approvals</div>;

  const selectedApproval = data?.items.find((item) => item.id === selectedId);

  return (
    <>
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="text-left py-3 px-4">Employee</th>
              <th className="text-left py-3 px-4">Leave Type</th>
              <th className="text-left py-3 px-4">From</th>
              <th className="text-left py-3 px-4">To</th>
              <th className="text-left py-3 px-4">Days</th>
              <th className="text-left py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.items && data.items.length > 0 ? (
              data.items.map((approval) => (
                <tr
                  key={approval.id}
                  className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  onClick={() => setSelectedId(approval.id)}
                >
                  <td className="py-3 px-4">{approval.employee_name}</td>
                  <td className="py-3 px-4">{approval.leave_type}</td>
                  <td className="py-3 px-4">{approval.start_date}</td>
                  <td className="py-3 px-4">{approval.end_date}</td>
                  <td className="py-3 px-4">{approval.days_requested}</td>
                  <td className="py-3 px-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedId(approval.id);
                      }}
                      className="btn btn-primary text-sm"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="py-8 text-center text-gray-500">
                  No pending approvals
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedApproval && (
        <ApprovalDetailModal
          approval={selectedApproval}
          onClose={() => setSelectedId(null)}
        />
      )}
    </>
  );
}
```

---

## TESTING STRATEGY

### Unit Tests (Vitest)

```bash
npm run test
```

Test files:
- `src/features/leave/__tests__/LeaveForm.test.tsx`
- `src/features/approvals/__tests__/ApprovalQueue.test.tsx`
- `src/lib/__tests__/oauth.test.ts`

### E2E Tests (Playwright)

```bash
npm run test:e2e
```

Test scenarios:
1. User login via OAuth → redirects to dashboard
2. User applies for leave → form validation → submission → success toast
3. Manager reviews pending approval → approve/reject → status changes
4. Balance updates after approval

---

## BACKEND INTEGRATION CHECKLIST

Before starting feature implementation, verify backend has:

- [ ] `POST /api/v1/auth/token` — OAuth token exchange
- [ ] `GET /api/v1/auth/me` — User profile
- [ ] `POST /api/v1/leave/requests` — Create leave request
- [ ] `GET /api/v1/leave/requests` — List leave requests
- [ ] `GET /api/v1/leave/balance` — Get balance
- [ ] `GET /api/v1/approvals/pending` — List pending approvals
- [ ] `POST /api/v1/approvals/{id}/approve` — Approve request
- [ ] `POST /api/v1/approvals/{id}/reject` — Reject request
- [ ] `GET /api/v1/audit/logs` — List audit logs

Run backend OpenAPI endpoint to verify:

```bash
curl http://localhost:8000/openapi.json
```

---

## SUCCESS CRITERIA

✅ **Phase 23 Complete When:**

1. **OAuth2 Flow**
   - Login redirects to OAuth provider
   - Callback handler exchanges code for tokens
   - Tokens stored in memory
   - Dashboard accessible after login
   - Logout clears tokens & redirects to login

2. **Leave Form**
   - Form validates dates (no past dates, end > start)
   - Balance check shows availability
   - Form submission calls API
   - Success toast on submission
   - Form clears on success
   - Error messages on failure

3. **Manager Approvals**
   - Pending approvals table loads
   - Click row to view details
   - Modal shows employee & leave info
   - Approve/reject buttons work
   - Comments field required for rejection
   - Success notification after action

4. **Balance Display**
   - Card shows available/used/pending
   - Progress bar visual
   - Refresh button works
   - Updates after leave requests

5. **All Errors Handled**
   - API errors show user-friendly messages
   - Loading states visible
   - Empty states displayed
   - Retry buttons functional

---

## DEPLOYMENT

After Phase 23 completion:

```bash
npm run build
npm run preview
```

Deploy to staging for testing with real users.

---

## NEXT PHASES

- **Phase 24:** Testing & Performance
- **Phase 25:** Mobile Optimization
- **Phase 26:** Advanced Features (calendar, reports, etc.)

---

**Status:** Ready to implement  
**Start Date:** December 19, 2025  
**Estimated Duration:** 2-3 weeks
