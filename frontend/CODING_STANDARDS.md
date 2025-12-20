# Coding Standards & Conventions – Phase 26.2

**Status:** Reference | **Scope:** All Frontend Code | **Effective:** Phase 26

---

## Table of Contents
1. [File & Folder Naming](#file--folder-naming)
2. [Component Structure](#component-structure)
3. [Hook Usage Rules](#hook-usage-rules)
4. [Utility vs Component Responsibility](#utility-vs-component-responsibility)
5. [Styling Conventions](#styling-conventions)
6. [Anti-Patterns & What to Avoid](#anti-patterns--what-to-avoid)
7. [Examples: Good vs Bad](#examples-good-vs-bad)

---

## File & Folder Naming

### General Rules
- **PascalCase** for React components (`.tsx` files)
- **camelCase** for utilities, hooks, services, and constants (`.ts` files)
- **kebab-case** for CSS files (`.css`)
- Descriptive names (not abbreviations)
- Plural folder names for collections, singular for utilities

### File Naming Examples

#### ✅ GOOD
```
src/
  components/
    ApprovalCard.tsx          # React component
    ApprovalModal.tsx         # React component
  hooks/
    useApprovalQuery.ts       # Custom hook
    useDebounce.ts            # Utility hook
  utils/
    formatters.ts             # Utility functions
    validators.ts             # Validation logic
  services/
    apiClient.ts              # API service
  types/
    generated.ts              # Generated types
  styles/
    globals.css               # Global styles
```

#### ❌ BAD
```
src/
  components/
    approval_card.tsx         # Should be PascalCase
    AC.tsx                    # Abbreviations unclear
  hooks/
    use_approval.ts           # Should be camelCase
  utils/
    formatters.js             # Frontend should be TypeScript
  helpers/                    # Too vague; use utils, hooks, or services
    helper.ts                 # No descriptive name
```

### Folder Structure Rules
- **Grouped by feature:** `src/features/approvals/`, `src/features/leave/`
- **Grouped by type:** `src/components/`, `src/hooks/`, `src/utils/`
- **Max 3 levels deep** (avoid deep nesting)

**Example Structure:**
```
src/
  features/
    approvals/
      components/            # Feature-specific components
        ApprovalCard.tsx
        ApprovalModal.tsx
      hooks/                 # Feature-specific hooks
        useApprovalQuery.ts
      utils/                 # Feature-specific utilities
        calculateDuration.ts
      types/                 # Feature-specific types
        approval.types.ts
  components/                # Shared components
    common/                  # Fully reusable (Button, Card, Modal)
    layout/                  # Layout components (Header, Sidebar)
    data-display/           # Data display (Table, List, Chart)
  hooks/                     # Shared hooks
  utils/                     # Shared utilities
  styles/                    # Global styles
  types/                     # Global types
```

---

## Component Structure

### React Component Template (TSX)

```typescript
// ========================================
// 1. IMPORTS
// ========================================
import React, { useState, useCallback } from 'react';
import type { FC } from 'react';

// Internal imports: API, hooks, utils, types
import { useApprovalQuery } from '@/hooks/useApprovalQuery';
import { ApprovalCard } from '@/components/ApprovalCard';
import type { IApproval } from '@/types';

// ========================================
// 2. TYPES & INTERFACES (If not in separate file)
// ========================================
interface ApprovalListProps {
  userId: string;
  onApprove?: (approval: IApproval) => void;
}

// ========================================
// 3. COMPONENT DEFINITION
// ========================================
/**
 * ApprovalList - Display all pending approvals for a user
 * 
 * @param {ApprovalListProps} props - Component props
 * @returns {JSX.Element} Rendered approval list
 */
export const ApprovalList: FC<ApprovalListProps> = ({ 
  userId, 
  onApprove 
}) => {
  // ========================================
  // 4. STATE MANAGEMENT
  // ========================================
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // ========================================
  // 5. QUERIES & MUTATIONS
  // ========================================
  const { data: approvals, isLoading, error } = useApprovalQuery(userId);

  // ========================================
  // 6. CALLBACKS (Use useCallback)
  // ========================================
  const handleSelect = useCallback((id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  // ========================================
  // 7. RENDER GUARDS (Loading, Error, Empty)
  // ========================================
  if (isLoading) {
    return (
      <div role="status" aria-label="Loading approvals">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="bg-red-50 p-4">
        <p>Unable to load approvals</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!approvals || approvals.length === 0) {
    return (
      <div className="text-center text-gray-500">
        <p>No approvals to review</p>
      </div>
    );
  }

  // ========================================
  // 8. MAIN RENDER
  // ========================================
  return (
    <div className="space-y-4">
      <header className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Approvals ({approvals.length})</h2>
        <button 
          onClick={() => setSelectedIds(new Set())}
          disabled={selectedIds.size === 0}
        >
          Clear Selection
        </button>
      </header>

      <ul className="space-y-2">
        {approvals.map(approval => (
          <ApprovalCard
            key={approval.id}
            approval={approval}
            isSelected={selectedIds.has(approval.id)}
            onSelect={handleSelect}
            onApprove={onApprove}
          />
        ))}
      </ul>
    </div>
  );
};

// ========================================
// 9. EXPORTS
// ========================================
export default ApprovalList;
```

### Component Structure Rules

1. **Imports First** - Group imports: React, external libs, internal imports
2. **Types Next** - Define interfaces/types near the component
3. **Component Definition** - JSDoc comment for exported components
4. **State Management** - useState calls grouped together
5. **Queries/Mutations** - Hook calls for data fetching
6. **Callbacks** - useCallback for stable function references
7. **Render Guards** - Loading, error, empty states BEFORE main render
8. **Main Render** - The component's primary JSX
9. **Exports** - Named export + default export

### Props Pattern

```typescript
// ✅ GOOD: Explicit interface for props
interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  onClick: () => void;
}

export const Button: FC<ButtonProps> = ({ 
  label, 
  variant = 'primary', 
  disabled = false, 
  onClick 
}) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {label}
    </button>
  );
};

// ❌ BAD: Props object without type
export const Button = (props: any) => {
  return <button {...props}>{props.label}</button>;
};

// ❌ BAD: Prop drilling (pass data through many levels)
// Instead: Use context or composition
<Parent user={user} > 
  <Child user={user} >
    <GrandChild user={user} /> {/* Avoid this */}
  </Child>
</Parent>
```

---

## Hook Usage Rules

### ✅ DO

#### Use Hooks for Data Fetching
```typescript
// ✅ GOOD: Custom hook encapsulates query logic
const useApprovalList = (userId: string) => {
  return useQuery(['approvals', userId], () => 
    apiClient.getApprovals(userId)
  );
};

// Usage in component:
const { data, isLoading, error } = useApprovalList(userId);
```

#### Use Hooks for Shared State
```typescript
// ✅ GOOD: Custom hook for shared logic
const useFormState = (initialValues: Record<string, any>) => {
  const [values, setValues] = useState(initialValues);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);

  return { values, touched, handleChange, setTouched };
};
```

#### Use useCallback for Stable Function References
```typescript
// ✅ GOOD: Callback wrapped in useCallback
const handleApprove = useCallback(async (id: string) => {
  await mutation.mutate(id);
}, [mutation]);

// Used in child component:
<ApprovalCard onApprove={handleApprove} />
```

#### Use useMemo for Expensive Computations
```typescript
// ✅ GOOD: Memoized calculation
const filteredAndSorted = useMemo(() => {
  return approvals
    .filter(a => a.status === 'pending')
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}, [approvals]);
```

#### Use useRef for Non-State Values
```typescript
// ✅ GOOD: useRef for DOM focus management
const inputRef = useRef<HTMLInputElement>(null);

const focusInput = () => {
  inputRef.current?.focus();
};

return <input ref={inputRef} />;
```

### ❌ DON'T

#### Don't Nest Hook Calls
```typescript
// ❌ BAD: Hooks inside conditional
if (userId) {
  const { data } = useQuery(/* ... */); // Breaks hook rules
}

// ✅ GOOD: Fetch unconditionally; guard in component
const { data } = useQuery(['approvals', userId], () => 
  userId ? apiClient.getApprovals(userId) : null,
  { enabled: !!userId }
);
```

#### Don't Use Hooks in Loops
```typescript
// ❌ BAD: Hook inside loop
items.forEach(item => {
  useState(item.value); // Invalid
});

// ✅ GOOD: Single hook with item IDs as key
const [values, setValues] = useState<Record<string, any>>({});
```

#### Don't Call Hooks Dynamically
```typescript
// ❌ BAD: Hook call depends on condition
const hook = userId ? useApprovalQuery : useLeaveQuery;
const data = hook(userId);

// ✅ GOOD: Both hooks called unconditionally
const approvals = useApprovalQuery(userId);
const leaves = useLeaveQuery(userId);
// Use only what you need
```

#### Don't Use Index as Key in Lists
```typescript
// ❌ BAD: Index as key can cause re-order bugs
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// ✅ GOOD: Unique identifier as key
{items.map(item => (
  <div key={item.id}>{item.name}</div>
))}
```

---

## Utility vs Component Responsibility

### Utility Functions (Pure, No JSX)
Use for logic that doesn't depend on React state or components.

```typescript
// ✅ GOOD: Pure utility function
export const calculateLeaveBalance = (
  totalDays: number,
  usedDays: number
): number => {
  return Math.max(0, totalDays - usedDays);
};

// Usage:
const balance = calculateLeaveBalance(20, 5); // 15
```

### Component-Level Logic (Uses State/Hooks)
Use for UI state, event handling, or conditional rendering.

```typescript
// ✅ GOOD: Component logic with state
export const LeaveBalance: FC<{ userId: string }> = ({ userId }) => {
  const { data: leaveData } = useLeaveQuery(userId);
  
  // Component uses the utility
  const balance = useMemo(() => 
    calculateLeaveBalance(leaveData.total, leaveData.used),
    [leaveData]
  );

  return <div>Balance: {balance} days</div>;
};
```

### Custom Hooks (Composable Logic)
Use for logic that needs hooks but isn't a component.

```typescript
// ✅ GOOD: Custom hook for composable logic
export const useLeaveBalance = (userId: string) => {
  const { data: leaveData } = useLeaveQuery(userId);
  
  return useMemo(() => 
    calculateLeaveBalance(leaveData.total, leaveData.used),
    [leaveData]
  );
};

// Usage in component:
const balance = useLeaveBalance(userId);
```

### Responsibility Matrix

| Task | Utility | Hook | Component |
|------|---------|------|-----------|
| Pure calculation | ✅ | ✗ | ✗ |
| Format/transform data | ✅ | ✗ | ✗ |
| Fetch data | ✗ | ✅ | ✗ |
| Manage component state | ✗ | ✅ | ✅ |
| Event handling | ✗ | ✗ | ✅ |
| Render JSX | ✗ | ✗ | ✅ |

---

## Styling Conventions

### Tailwind CSS Rules

#### ✅ DO
- Use Tailwind utility classes
- Group related classes logically
- Use `clsx()` or `classnames()` for conditional classes
- Extract repeated class patterns to component-level utilities
- Use Tailwind config for custom spacing/colors
- Follow utility class order (layout, spacing, colors, text, effects)

#### ❌ DON'T
- Don't use inline styles (`style={{ }}`)
- Don't create custom CSS for what Tailwind provides
- Don't use `!important` to override Tailwind
- Don't nest utility classes

### Class Ordering
Follow this order for readability:

```typescript
// ✅ GOOD: Organized class order
<div className="
  // Layout
  flex flex-col gap-4
  // Sizing
  w-full max-w-md
  // Spacing
  p-4 my-2
  // Colors & appearance
  bg-white border border-gray-200 rounded-lg
  // Text
  text-gray-700 font-semibold
  // Interactive
  hover:bg-gray-50 cursor-pointer
  // Responsive
  md:flex-row lg:max-w-lg
">
  Content
</div>
```

### Conditional Classes
```typescript
// ✅ GOOD: Use clsx for conditional classes
import clsx from 'clsx';

<button
  className={clsx(
    'px-4 py-2 rounded font-semibold',
    {
      'bg-blue-600 text-white': variant === 'primary',
      'bg-gray-200 text-gray-800': variant === 'secondary',
      'opacity-50 cursor-not-allowed': disabled,
    }
  )}
>
  Click me
</button>

// ❌ BAD: String concatenation
className={`px-4 py-2 ${disabled ? 'opacity-50' : ''} ${variant === 'primary' ? 'bg-blue' : ''}`}
```

### Extracting Repeated Styles
```typescript
// ❌ BAD: Repeated classes
<div className="flex items-center gap-2 bg-gray-50 p-4 rounded border border-gray-200">
  <span>Info</span>
</div>

// ✅ GOOD: Extracted to utility or component
const alertClasses = 'flex items-center gap-2 bg-gray-50 p-4 rounded border border-gray-200';

<div className={alertClasses}>
  <span>Info</span>
</div>

// Or as a component:
export const Alert: FC<{ children: ReactNode }> = ({ children }) => (
  <div className="flex items-center gap-2 bg-gray-50 p-4 rounded border border-gray-200">
    {children}
  </div>
);
```

### Responsive Design
```typescript
// ✅ GOOD: Mobile-first responsive design
<div className="
  grid grid-cols-1           // Mobile: 1 column
  sm:grid-cols-2             // Small: 2 columns
  lg:grid-cols-3             // Large: 3 columns
  gap-4
  px-4 sm:px-6 lg:px-8       // Responsive padding
">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

---

## Anti-Patterns & What to Avoid

### ❌ Anti-Pattern 1: Prop Drilling
**Problem:** Passing props through many intermediate components

```typescript
// ❌ BAD: Prop drilling
<Layout user={user}>
  <Header user={user}>
    <Nav user={user}>
      <UserMenu user={user} /> {/* Too many levels */}
    </Nav>
  </Header>
</Layout>

// ✅ GOOD: Use context or composition
const UserContext = React.createContext<User | null>(null);

<UserContext.Provider value={user}>
  <Layout>
    <Header>
      <Nav>
        <UserMenu /> {/* useContext(UserContext) inside */}
      </Nav>
    </Header>
  </Layout>
</UserContext.Provider>
```

### ❌ Anti-Pattern 2: God Component
**Problem:** Single component doing too much (state, logic, rendering)

```typescript
// ❌ BAD: God component
export const ApprovalDashboard = () => {
  const [approvals, setApprovals] = useState([]);
  const [filters, setFilters] = useState({});
  const [sortBy, setSortBy] = useState('date');
  const [selectedIds, setSelectedIds] = useState([]);
  // ... 30 more state variables
  
  // ... 200 lines of logic
  // ... 500 lines of JSX rendering everything
};

// ✅ GOOD: Split into smaller components
export const ApprovalDashboard = () => {
  const approvals = useApprovalList();
  
  return (
    <div>
      <ApprovalFilters />
      <ApprovalList approvals={approvals} />
      <ApprovalBulkActions />
    </div>
  );
};
```

### ❌ Anti-Pattern 3: Silent Failures
**Problem:** Errors not shown to user

```typescript
// ❌ BAD: Error swallowed
const { data } = useQuery(['approvals'], () => 
  apiClient.getApprovals()
); // No error handling visible

// ✅ GOOD: Error explicitly handled
const { data, error } = useQuery(['approvals'], () => 
  apiClient.getApprovals()
);

{error && (
  <div role="alert" className="bg-red-50 p-4">
    <p>Failed to load approvals. Try again.</p>
    <button onClick={retry}>Retry</button>
  </div>
)}
```

### ❌ Anti-Pattern 4: Unmemoized Callbacks in Child Props
**Problem:** Causes unnecessary child re-renders

```typescript
// ❌ BAD: New function every render
<Child onApprove={() => mutate(id)} /> // New function object

// ✅ GOOD: Memoized callback
const handleApprove = useCallback(() => mutate(id), [mutate, id]);
<Child onApprove={handleApprove} />
```

### ❌ Anti-Pattern 5: Complex Ternary Rendering
**Problem:** Hard to read and maintain

```typescript
// ❌ BAD: Nested ternaries
return (
  <div>
    {isLoading ? (
      <Spinner />
    ) : error ? (
      <Error />
    ) : data.length === 0 ? (
      <Empty />
    ) : (
      <List data={data} />
    )}
  </div>
);

// ✅ GOOD: Guard clauses (render guards)
if (isLoading) return <Spinner />;
if (error) return <Error />;
if (data.length === 0) return <Empty />;
return <List data={data} />;
```

### ❌ Anti-Pattern 6: Magic Numbers & Strings
**Problem:** Hard to understand intent

```typescript
// ❌ BAD: Magic numbers
if (balance > 5) {
  // Show warning
}

// ✅ GOOD: Named constants
const LOW_BALANCE_THRESHOLD = 5;
if (balance > LOW_BALANCE_THRESHOLD) {
  // Show warning
}
```

### ❌ Anti-Pattern 7: Always Refetch on Component Mount
**Problem:** Unnecessary network requests and server load

```typescript
// ❌ BAD: Refetch every mount
useEffect(() => {
  apiClient.getApprovals().then(setData);
}, []); // No dependencies; refetches on every mount

// ✅ GOOD: Let React Query handle caching
const { data } = useQuery(['approvals'], () => 
  apiClient.getApprovals()
); // Cached; only refetch if stale
```

---

## Examples: Good vs Bad

### Example 1: Form Component

#### ❌ BAD
```typescript
export const ApprovalForm = (props: any) => {
  const [data, setData] = useState({});

  return (
    <div>
      <input 
        onChange={(e) => setData({ ...data, comment: e.target.value })}
      />
      <button onClick={() => props.onSubmit(data)}>Submit</button>
    </div>
  );
};
```

#### ✅ GOOD
```typescript
interface ApprovalFormProps {
  onSubmit: (data: IApprovalSubmission) => Promise<void>;
}

interface FormState {
  comment: string;
  decision: 'approve' | 'reject';
}

export const ApprovalForm: FC<ApprovalFormProps> = ({ onSubmit }) => {
  const [formState, setFormState] = useState<FormState>({
    comment: '',
    decision: 'approve',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(formState);
    } catch (err) {
      setError('Failed to submit approval. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [formState, onSubmit]);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="decision" className="block text-sm font-semibold">
          Decision
        </label>
        <select
          id="decision"
          value={formState.decision}
          onChange={(e) => setFormState(prev => ({
            ...prev,
            decision: e.target.value as 'approve' | 'reject'
          }))}
          className="w-full px-3 py-2 border border-gray-300 rounded"
        >
          <option value="approve">Approve</option>
          <option value="reject">Reject</option>
        </select>
      </div>

      <div>
        <label htmlFor="comment" className="block text-sm font-semibold">
          Comment
        </label>
        <textarea
          id="comment"
          value={formState.comment}
          onChange={(e) => setFormState(prev => ({
            ...prev,
            comment: e.target.value
          }))}
          className="w-full px-3 py-2 border border-gray-300 rounded"
          placeholder="Optional: Add a comment"
          rows={4}
        />
      </div>

      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 p-3 rounded">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};
```

### Example 2: Data List Component

#### ❌ BAD
```typescript
export const ApprovalList = ({ userId }: any) => {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/approvals?userId=${userId}`)
      .then(r => r.json())
      .then(d => setApprovals(d))
      .catch(() => alert('Error!'))
      .finally(() => setLoading(false));
  }, [userId]);

  return (
    <div>
      {loading && <p>Loading...</p>}
      {approvals.map(a => (
        <div key={a.id} style={{ padding: '10px', border: '1px solid black' }}>
          <h3>{a.title}</h3>
          <p>{a.status}</p>
        </div>
      ))}
    </div>
  );
};
```

#### ✅ GOOD
```typescript
interface ApprovalListProps {
  userId: string;
}

export const ApprovalList: FC<ApprovalListProps> = ({ userId }) => {
  const { data: approvals, isLoading, error } = useApprovalQuery(userId);

  if (isLoading) {
    return (
      <div role="status" aria-label="Loading approvals">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div 
        role="alert" 
        className="bg-red-50 border border-red-200 rounded p-4"
      >
        <p className="font-semibold text-red-800">Failed to load approvals</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-2 px-3 py-1 bg-red-800 text-white rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!approvals || approvals.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p className="text-lg">No approvals to review</p>
        <p className="text-sm">Check back later for pending requests</p>
      </div>
    );
  }

  return (
    <ul className="space-y-3">
      {approvals.map(approval => (
        <ApprovalCard 
          key={approval.id} 
          approval={approval}
        />
      ))}
    </ul>
  );
};
```

---

## Summary: Key Takeaways

1. **Naming:** PascalCase (components), camelCase (utilities/hooks)
2. **Structure:** Imports → Types → State → Queries → Callbacks → Guards → Render
3. **Hooks:** Fetch with hooks, memoize callbacks, extract custom hooks
4. **Utils:** Pure functions that don't depend on React
5. **Styling:** Tailwind utilities only; no inline styles
6. **Avoid:** Prop drilling, god components, silent errors, magic numbers
7. **Errors:** Always show user-friendly error messages
8. **Loading:** Always show loading states
9. **Empty:** Always handle empty data gracefully
10. **Types:** Explicit types everywhere; no `any`

---

**Coding Standards Version:** 1.0 | **Status:** Active | **Last Updated:** December 2025
