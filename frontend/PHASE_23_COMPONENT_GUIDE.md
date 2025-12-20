# PHASE_23_COMPONENT_GUIDE.md

## Quick Reference: Phase 23 Components

All production components implemented in Phase 23 with full usage examples.

---

## 1. LeaveForm Component

**Location:** `src/features/leave/components/LeaveForm.tsx`  
**Purpose:** Form for employees to apply for leave with validation and balance checking

### Basic Usage
```tsx
import { LeaveForm } from '@/features/leave/components/LeaveForm';

function MyPage() {
  const handleSuccess = () => {
    // Redirect or show toast
  };

  return <LeaveForm onSuccess={handleSuccess} />;
}
```

### Props
```typescript
interface LeaveFormProps {
  onSuccess?: () => void;  // Called after successful submission
}
```

### Features
- ✅ Date validation (not in past, end >= start)
- ✅ Reason validation (10-500 characters)
- ✅ Real-time balance checking
- ✅ Insufficient balance warning
- ✅ Loading state during submission
- ✅ Error display and retry

### Form Data Submitted
```typescript
{
  leave_type: string;      // Annual Leave, Sick Leave, Personal Leave
  start_date: string;      // ISO date string
  end_date: string;        // ISO date string
  reason: string;          // 10-500 chars
}
```

### Expected Response
```typescript
{
  id: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  // ... other fields
}
```

---

## 2. BalanceCard Component

**Location:** `src/features/balance/components/BalanceCard.tsx`  
**Purpose:** Display leave balance with visualization

### Compact Variant (for dashboards)
```tsx
import { BalanceCard } from '@/features/balance/components/BalanceCard';

function MyDashboard() {
  return (
    <BalanceCard 
      variant="compact" 
      onRefresh={() => console.log('Refreshing...')}
    />
  );
}
```

### Full Variant (for detail pages)
```tsx
function MyPage() {
  return (
    <BalanceCard 
      variant="full"
      onRefresh={() => console.log('Refreshing...')}
    />
  );
}
```

### Props
```typescript
interface BalanceCardProps {
  variant?: 'compact' | 'full';  // Default: 'full'
  onRefresh?: () => void;         // Called when user clicks refresh
}
```

### Compact Display
- Small card with progress bar
- Available days in large text
- Used/Pending breakdown
- Minimal space (perfect for sidebar)

### Full Display
- Welcome header
- Color-coded progress bar
- 3-column stat grid (available/pending/used)
- Smart status alerts
- Manual refresh button

### Data Source
Uses `useLeaveBalance()` hook internally:
```typescript
{
  available: number;  // Days ready to use
  used: number;       // Days already used
  pending: number;    // Days awaiting approval
}
```

---

## 3. ApprovalQueue Component

**Location:** `src/features/approvals/components/ApprovalQueue.tsx`  
**Purpose:** Display pending leave approvals for managers

### Basic Usage
```tsx
import { ApprovalQueue } from '@/features/approvals/components/ApprovalQueue';

function ApprovalsPage() {
  return (
    <div>
      <h1>Pending Approvals</h1>
      <ApprovalQueue pageSize={10} />
    </div>
  );
}
```

### Props
```typescript
interface ApprovalQueuesProps {
  pageSize?: number;  // Items per page (default: 10)
}
```

### Features
- ✅ Paginated table of pending requests
- ✅ Employee info, dates, days count
- ✅ Action buttons (Approve/Reject)
- ✅ Modal for detailed review
- ✅ Success/error notifications
- ✅ Role-based access control (managers only)
- ✅ Query auto-refresh after actions

### Table Columns
| Column | Content |
|--------|---------|
| Employee | Name + ID |
| Leave Type | Type badge |
| Dates | Start date → End date |
| Days | Number of days |
| Submitted | Date + Time |
| Actions | Approve/Reject buttons |

### Pagination
- Shows current page and total count
- Previous/Next buttons
- Disabled at boundaries
- Respects page size

### Data Flow
1. Fetches pending approvals via `useApprovalsQuery()`
2. User clicks Approve/Reject
3. Modal opens with request details
4. User enters approval/rejection comments
5. Mutation called (`useApproveRequest()` / `useRejectRequest()`)
6. Query invalidated, table refreshes
7. Success message shown

---

## 4. ApprovalDetailModal Component

**Location:** `src/features/approvals/components/ApprovalDetailModal.tsx`  
**Purpose:** Modal for approving/rejecting a leave request

### Used By
Automatically used by `ApprovalQueue` - don't import directly

### Manual Usage (if needed)
```tsx
import { ApprovalDetailModal } from '@/features/approvals/components/ApprovalDetailModal';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState(null);

  return (
    <ApprovalDetailModal
      isOpen={isOpen}
      approval={selectedApproval}
      onApprove={(comments) => {
        // Call approve API
      }}
      onReject={(comments) => {
        // Call reject API
      }}
      isLoading={false}
      onClose={() => setIsOpen(false)}
    />
  );
}
```

### Props
```typescript
interface ApprovalDetailModalProps {
  isOpen: boolean;
  approval: {
    id: string;
    employeeName: string;
    startDate: string;
    endDate: string;
    days: number;
    reason: string;
  };
  onApprove: (comments?: string) => void;
  onReject: (comments: string) => void;
  isLoading: boolean;
  onClose: () => void;
}
```

### Two-Step Workflow
1. **First:** User chooses Approve or Reject
2. **Then:** Form appears for comments
   - Approve: Comments optional
   - Reject: Comments required (10+ chars)

### Features
- ✅ Request summary display
- ✅ Approval/rejection forms
- ✅ Comments validation
- ✅ Character count
- ✅ Loading states
- ✅ Cancel option to change action

---

## 5. OAuth Integration

**Location:** `src/lib/oauth.ts` + `src/app/auth/CallbackPage.tsx`

### Login Flow
```tsx
// In LoginPage.tsx
import { getAuthorizationUrl } from '@/lib/oauth';

function LoginPage() {
  const handleLogin = () => {
    const authUrl = getAuthorizationUrl();
    window.location.href = authUrl;
  };

  return <button onClick={handleLogin}>Login with OAuth</button>;
}
```

### Callback Handler
```tsx
// CallbackPage handles: /auth/callback?code=XXX&state=YYY
// Automatically:
// 1. Extracts code from URL
// 2. Exchanges for tokens
// 3. Stores in AuthProvider
// 4. Redirects to dashboard
```

### Configuration
Set in `.env.development` or `.env.production`:
```env
VITE_OAUTH_CLIENT_ID=your_client_id
VITE_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback
VITE_OAUTH_AUTHORIZATION_URL=https://provider.com/oauth/authorize
VITE_API_BASE_URL=http://localhost:8000
```

### Token Exchange
```typescript
// Automatically handles:
// POST /api/v1/auth/token
// {
//   code: string;
//   code_verifier: string;  // PKCE
// }
// 
// Response:
// {
//   access_token: string;
//   refresh_token: string;
//   expires_in: number;
// }
```

---

## 6. Related Hooks (Used Internally)

### useLeaveBalance()
```typescript
const { data: balance, isLoading, refetch } = useLeaveBalance();
// balance: { available, used, pending }
```

### useLeaveRequests()
```typescript
const { data: requests, isLoading } = useLeaveRequests({
  limit?: number;
  status?: 'all' | 'pending' | 'approved' | 'rejected';
  page?: number;
});
// requests: { items: [...], total, page, pageSize }
```

### useCreateLeaveRequest()
```typescript
const { mutate, isPending, error } = useCreateLeaveRequest();
mutate({
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
});
```

### useApprovalsQuery()
```typescript
const { data, isLoading } = useApprovalsQuery({
  page?: number;
  pageSize?: number;
  status?: string;
});
```

### useApproveRequest()
```typescript
const { mutate, isPending } = useApproveRequest();
mutate({ id: string; comments?: string });
```

### useRejectRequest()
```typescript
const { mutate, isPending } = useRejectRequest();
mutate({ id: string; comments: string });
```

---

## Integration Examples

### Example 1: Complete Leave Application Page
```tsx
import { LeaveForm } from '@/features/leave/components/LeaveForm';
import { BalanceCard } from '@/features/balance/components/BalanceCard';

export function LeaveApplicationPage() {
  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <h1>Apply for Leave</h1>
        <LeaveForm onSuccess={() => {
          // Show success toast
          navigate('/leave/history');
        }} />
      </div>
      <div>
        <BalanceCard variant="full" />
      </div>
    </div>
  );
}
```

### Example 2: Dashboard with All Features
```tsx
import { BalanceCard } from '@/features/balance/components/BalanceCard';
import { useLeaveBalance, useLeaveRequests } from '@/features/leave/hooks/useLeaveRequests';

export function DashboardPage() {
  const { data: balance } = useLeaveBalance();
  const { data: requests } = useLeaveRequests({ limit: 5 });

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <div className="grid grid-cols-4 gap-4">
          <StatCard title="Available" value={balance?.available} />
          <StatCard title="Used" value={balance?.used} />
          <StatCard title="Pending" value={balance?.pending} />
        </div>
        
        <RecentRequests requests={requests?.items} />
      </div>
      <div>
        <BalanceCard variant="full" />
      </div>
    </div>
  );
}
```

### Example 3: Manager Approvals Page
```tsx
import { ApprovalQueue } from '@/features/approvals/components/ApprovalQueue';
import { RoleGate } from '@/auth/RoleGate';

export function ApprovalsPage() {
  return (
    <RoleGate requiredRoles={['manager']}>
      <h1>Pending Approvals</h1>
      <ApprovalQueue pageSize={15} />
    </RoleGate>
  );
}
```

---

## Styling

All components use Tailwind CSS utility classes and custom components from `src/globals.css`:

### Card Component
```html
<div class="card">
  Content here
</div>
```

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-error">Error</button>
<button class="btn btn-sm">Small</button>
```

### Badges
```html
<span class="badge badge-success">Approved</span>
<span class="badge badge-error">Rejected</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-info">Info</span>
```

### Input Fields
```html
<input class="input" type="text" />
<textarea class="input" rows="4"></textarea>
<select class="input">
  <option>Option</option>
</select>
```

### Colors
- **Primary:** Blue (#2563eb)
- **Success:** Green (#10b981)
- **Error:** Red (#ef4444)
- **Warning:** Amber (#f59e0b)
- **Info:** Cyan (#06b6d4)

---

## Dark Mode

All components automatically support dark mode via Tailwind:
```
dark:bg-gray-800
dark:text-gray-300
dark:border-gray-700
```

Toggle dark mode with `<html class="dark">` in index.html

---

## Error Handling

All components handle errors gracefully:

### Error Messages
```typescript
// mapAPIError() converts HTTP errors to user messages:
400 → "Validation error"
401 → "Your session expired, please login"
403 → "You don't have permission"
404 → "Resource not found"
409 → "Conflict (e.g., balance insufficient)"
500 → "Server error, please try again"
```

### Retry Logic
- Forms show error message with retry button
- Mutations can be re-run
- Queries auto-retry with exponential backoff

### User Feedback
- Success toasts appear for positive actions
- Error alerts show for failures
- Loading spinners indicate pending operations

---

## Testing Components

### Unit Test Example (LeaveForm)
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LeaveForm } from '@/features/leave/components/LeaveForm';

describe('LeaveForm', () => {
  it('should validate required fields', async () => {
    render(<LeaveForm />);
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/required/i)).toBeInTheDocument();
  });
});
```

### Integration Test Example
```typescript
it('should create leave request and refresh queries', async () => {
  const mockOnSuccess = jest.fn();
  render(<LeaveForm onSuccess={mockOnSuccess} />);
  
  // Fill form...
  // Submit...
  // Verify API was called
  // Verify queries were invalidated
  // Verify onSuccess was called
});
```

---

## Performance Tips

1. **Don't recreate callbacks in render:**
   ```typescript
   // ❌ Bad
   <LeaveForm onSuccess={() => navigate('/')} />
   
   // ✅ Good
   const handleSuccess = useCallback(() => {
     navigate('/');
   }, [navigate]);
   <LeaveForm onSuccess={handleSuccess} />
   ```

2. **Use React Query's caching:**
   - Balance is cached for 5 minutes
   - Requests are cached and auto-refreshed
   - Mutations auto-invalidate related queries

3. **Lazy load heavy components:**
   - Use React.lazy() for Approval modals if needed
   - Vite automatically code-splits routes

---

## Accessibility Checklist

- ✅ All forms have associated labels
- ✅ Error messages linked to inputs via aria-invalid
- ✅ Buttons have clear text labels
- ✅ Loading states announced (aria-busy)
- ✅ Color not only indicator (text + icons)
- ✅ Keyboard navigation works (Tab, Enter, Escape)
- ✅ Form validation shows errors inline
- ✅ Images have alt text
- ✅ Contrast ratios meet WCAG AA
- ✅ Focus visible indicator present

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| BalanceCard not updating | Call `refetch()` manually or wait 5 min for cache invalidation |
| Form not submitting | Check console for validation errors, ensure balance is sufficient |
| Modal not closing | Ensure `onClose` callback is triggered |
| Role-based content not hiding | Verify roles in AuthProvider match backend |
| Dark mode not working | Add `class="dark"` to `<html>` element |

---

## Future Enhancements

Ready for these additions:
- [ ] Email notifications on approval/rejection
- [ ] SMS reminders for pending requests
- [ ] Calendar integration (visual timeline)
- [ ] Bulk actions (approve multiple requests)
- [ ] Export to CSV/PDF
- [ ] Request history export
- [ ] Team analytics dashboard
- [ ] Availability heatmap

---

## Resources

- React: https://react.dev
- React Hook Form: https://react-hook-form.com
- React Query: https://tanstack.com/query
- Tailwind CSS: https://tailwindcss.com
- TypeScript: https://www.typescriptlang.org
