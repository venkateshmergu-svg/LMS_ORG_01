# PHASE 21 – FRONTEND ARCHITECTURE

**Leave Management System (LMS) - Production Frontend**

**Date:** December 19, 2025  
**Version:** 1.0  
**Status:** Architecture Definition

---

## EXECUTIVE SUMMARY

This document defines the frontend architecture for the LMS, designed as a **thin client** that consumes the complete, authoritative backend APIs. The frontend is responsible for presentation, user experience, and role-based navigation—NOT for business logic, security enforcement, or data calculations.

**Core Principle:** Backend is the single source of truth. Frontend is a view layer with smart caching.

---

## TECH STACK

### Core Framework

- **React 18+** with TypeScript
- **Vite** (development) or **Next.js 14+ App Router** (production)
- **TypeScript 5+** (strict mode enabled)

### State Management

- **TanStack Query v5** (React Query) for server state
- **Zustand** or **Context API** for minimal UI state (theme, sidebar, modals)

### Styling

- **Tailwind CSS 3+** with custom design system tokens
- **Radix UI** or **shadcn/ui** for accessible primitives
- **Lucide Icons** for consistent iconography

### API & Auth

- **Axios** with typed interceptors
- **OAuth2/OIDC Client** (token management abstracted)
- **OpenAPI TypeScript Codegen** for type-safe API contracts

### Development

- **ESLint** + **Prettier** for code quality
- **Vitest** for unit tests
- **Playwright** for E2E tests
- **MSW (Mock Service Worker)** for API mocking

---

## PHASE 21.1 – APPLICATION STRUCTURE

### Folder Structure

```
frontend/
├── public/
│   └── assets/
├── src/
│   ├── app/                      # Routing & layouts (Next.js) OR routes (React Router)
│   │   ├── layout.tsx            # Root layout with providers
│   │   ├── page.tsx              # Dashboard / landing
│   │   ├── (authenticated)/      # Protected routes group
│   │   │   ├── leave/
│   │   │   │   ├── apply/
│   │   │   │   ├── history/
│   │   │   │   └── balance/
│   │   │   ├── approvals/
│   │   │   ├── team/
│   │   │   ├── reports/
│   │   │   └── audit/
│   │   └── (public)/
│   │       └── login/
│   │
│   ├── auth/                     # Authentication layer
│   │   ├── AuthProvider.tsx     # Auth context & token management
│   │   ├── ProtectedRoute.tsx   # Route guards
│   │   ├── useAuth.ts           # Auth hook
│   │   ├── RoleGate.tsx         # Component-level RBAC
│   │   └── tokens.ts            # Token storage abstraction
│   │
│   ├── api/                      # Backend API clients
│   │   ├── client.ts            # Axios instance with interceptors
│   │   ├── types/               # OpenAPI-generated or manual types
│   │   │   ├── leave.types.ts
│   │   │   ├── user.types.ts
│   │   │   ├── workflow.types.ts
│   │   │   └── common.types.ts
│   │   ├── endpoints/
│   │   │   ├── leave.api.ts
│   │   │   ├── approvals.api.ts
│   │   │   ├── balance.api.ts
│   │   │   ├── audit.api.ts
│   │   │   └── integrations.api.ts
│   │   └── errors.ts            # Error mapping utilities
│   │
│   ├── features/                 # Domain-driven feature modules
│   │   ├── leave/
│   │   │   ├── components/      # Leave-specific UI
│   │   │   ├── hooks/           # useLeaveRequests, useApplyLeave
│   │   │   └── types.ts
│   │   ├── approvals/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   ├── balance/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   ├── audit/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   └── admin/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── types.ts
│   │
│   ├── components/               # Shared/reusable UI components
│   │   ├── ui/                  # Base primitives (Button, Input, Card)
│   │   ├── layout/              # Header, Sidebar, Footer
│   │   ├── feedback/            # LoadingSpinner, ErrorBoundary, Toast
│   │   └── data-display/        # Table, Badge, StatusIndicator
│   │
│   ├── hooks/                    # Shared custom hooks
│   │   ├── useQueryStates.ts    # Unified loading/error states
│   │   ├── useDebounce.ts
│   │   └── usePermissions.ts
│   │
│   ├── layouts/                  # Page-level layout templates
│   │   ├── DashboardLayout.tsx
│   │   ├── MinimalLayout.tsx
│   │   └── PrintLayout.tsx
│   │
│   ├── lib/                      # Third-party configurations
│   │   ├── react-query.ts       # QueryClient setup
│   │   ├── axios.ts             # Axios defaults
│   │   └── date-fns.ts          # Date utilities
│   │
│   ├── utils/                    # Pure utility functions
│   │   ├── format.ts            # Date, number formatting
│   │   ├── validation.ts        # Client-side validation helpers
│   │   └── constants.ts         # App-wide constants
│   │
│   └── types/                    # Global TypeScript types
│       ├── global.d.ts
│       ├── env.d.ts
│       └── api.d.ts
│
├── .env.development
├── .env.production
├── tsconfig.json
├── vite.config.ts / next.config.js
└── tailwind.config.ts
```

### Layer Responsibilities

| Layer           | Responsibility                           | Examples                               |
| --------------- | ---------------------------------------- | -------------------------------------- |
| **app/**        | Routing, layouts, page composition       | Route definitions, auth wrappers       |
| **auth/**       | Token lifecycle, auth state, role checks | Login flow, token refresh, RBAC gates  |
| **api/**        | HTTP communication with backend          | Axios client, endpoint wrappers, types |
| **features/**   | Domain-specific logic & UI               | Leave application form, approval queue |
| **components/** | Reusable, domain-agnostic UI             | Buttons, tables, modals                |
| **hooks/**      | Cross-cutting React hooks                | Query state management, permissions    |
| **layouts/**    | Page structure templates                 | Sidebar + content, minimal header      |
| **utils/**      | Pure functions (no React)                | Date formatting, string helpers        |
| **types/**      | Shared TypeScript definitions            | Enums, global types                    |

---

## PHASE 21.2 – API CONTRACT STRATEGY

### Type Generation Strategy

**Recommended Approach:** **OpenAPI-Generated Types** (single source of truth)

```bash
# Generate TypeScript types from backend OpenAPI spec
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types/generated.ts
```

**Alternative:** Manual type curation (only if OpenAPI unavailable)

### API Client Architecture

**File:** `src/api/client.ts`

```typescript
import axios, { AxiosInstance, AxiosError } from "axios";
import { getAccessToken, refreshAccessToken } from "@/auth/tokens";

export const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Attach JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### Endpoint Wrappers

**File:** `src/api/endpoints/leave.api.ts`

```typescript
import { apiClient } from "../client";
import type {
  LeaveRequest,
  LeaveRequestCreate,
  LeaveBalance,
  PaginatedResponse,
} from "../types/generated";

export const leaveAPI = {
  // GET /api/v1/leave/requests
  getMyRequests: async (params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<LeaveRequest>> => {
    const { data } = await apiClient.get("/api/v1/leave/requests", { params });
    return data;
  },

  // POST /api/v1/leave/requests
  createRequest: async (payload: LeaveRequestCreate): Promise<LeaveRequest> => {
    const { data } = await apiClient.post("/api/v1/leave/requests", payload);
    return data;
  },

  // GET /api/v1/leave/balance
  getBalance: async (): Promise<LeaveBalance> => {
    const { data } = await apiClient.get("/api/v1/leave/balance");
    return data;
  },

  // DELETE /api/v1/leave/requests/{id}
  withdrawRequest: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/leave/requests/${id}`);
  },
};
```

### Error Mapping

**File:** `src/api/errors.ts`

```typescript
import { AxiosError } from "axios";

export interface APIError {
  code: string;
  message: string;
  field?: string;
}

export function mapAPIError(error: unknown): APIError {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    if (status === 400) {
      return {
        code: "VALIDATION_ERROR",
        message: detail || "Invalid request data",
        field: error.response?.data?.field,
      };
    }

    if (status === 403) {
      return {
        code: "FORBIDDEN",
        message: "You do not have permission to perform this action",
      };
    }

    if (status === 404) {
      return {
        code: "NOT_FOUND",
        message: detail || "Resource not found",
      };
    }

    if (status === 409) {
      return {
        code: "CONFLICT",
        message: detail || "This action conflicts with existing data",
      };
    }

    if (status && status >= 500) {
      return {
        code: "SERVER_ERROR",
        message: "An unexpected error occurred. Please try again later.",
      };
    }
  }

  return {
    code: "UNKNOWN_ERROR",
    message: "An unexpected error occurred",
  };
}
```

### Rules

✅ **DO:**

- Use generated types from OpenAPI
- Wrap all API calls in typed functions
- Handle all HTTP status codes explicitly
- Return typed responses, never `any`
- Include request/response interceptors

❌ **DON'T:**

- Guess API response shapes
- Perform calculations on API data (e.g., balance math)
- Retry failed requests indefinitely
- Ignore 403/401 errors
- Store business rules in frontend

---

## PHASE 21.3 – AUTH & RBAC IN UI

### Authentication Strategy

**Assumption:** Backend issues JWT via OAuth2/OIDC. Frontend receives token from auth callback.

### Token Storage

**File:** `src/auth/tokens.ts`

```typescript
// PRODUCTION: Use secure, httpOnly cookies OR in-memory storage
// AVOID localStorage for JWTs (XSS risk)

let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  // Optional: store refresh token in httpOnly cookie via backend
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
}

export async function refreshAccessToken(): Promise<string> {
  // Call backend refresh endpoint
  const response = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) throw new Error("Token refresh failed");

  const data = await response.json();
  accessToken = data.access_token;
  return accessToken;
}
```

### Auth Context

**File:** `src/auth/AuthProvider.tsx`

```typescript
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { setTokens, clearTokens } from "./tokens";

interface User {
  id: string;
  email: string;
  full_name: string;
  roles: string[]; // e.g., ["EMPLOYEE", "MANAGER"]
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // On mount, validate existing token and fetch user
    const initAuth = async () => {
      try {
        const response = await fetch("/api/v1/auth/me", {
          headers: { Authorization: `Bearer ${getAccessToken()}` },
        });
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        }
      } catch (error) {
        console.error("Auth init failed", error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (accessToken: string, refreshToken: string) => {
    setTokens(accessToken, refreshToken);

    // Fetch user profile
    const response = await fetch("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const userData = await response.json();
    setUser(userData);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    window.location.href = "/login";
  };

  const hasRole = (role: string) => {
    return user?.roles.includes(role) ?? false;
  };

  const hasAnyRole = (roles: string[]) => {
    return roles.some((role) => user?.roles.includes(role)) ?? false;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasRole,
        hasAnyRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
```

### Route Protection

**File:** `src/auth/ProtectedRoute.tsx`

```typescript
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRoles?: string[];
}

export function ProtectedRoute({
  children,
  requiredRoles,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasAnyRole } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>; // Or proper loading skeleton
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRoles && !hasAnyRole(requiredRoles)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
```

### Component-Level RBAC

**File:** `src/auth/RoleGate.tsx`

```typescript
import { ReactNode } from "react";
import { useAuth } from "./AuthProvider";

interface RoleGateProps {
  children: ReactNode;
  requiredRoles: string[];
  fallback?: ReactNode;
}

export function RoleGate({
  children,
  requiredRoles,
  fallback = null,
}: RoleGateProps) {
  const { hasAnyRole } = useAuth();

  if (!hasAnyRole(requiredRoles)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
```

**Usage Example:**

```typescript
<RoleGate requiredRoles={["HR_ADMIN", "MANAGER"]}>
  <Button onClick={handleApprove}>Approve Request</Button>
</RoleGate>
```

### UI RBAC Rules

| Aspect         | UI Behavior                        | Backend Authority                    |
| -------------- | ---------------------------------- | ------------------------------------ |
| **Navigation** | Hide menu items user cannot access | Endpoints return 403 if unauthorized |
| **Buttons**    | Disable/hide actions not permitted | API rejects unauthorized actions     |
| **Routes**     | Redirect to 403 page               | Backend denies access                |
| **Data**       | Don't fetch data user can't see    | Backend filters data by role         |

**Critical:** UI RBAC is for UX only. Backend always enforces security.

---

## PHASE 21.4 – ROLE-BASED UX FLOWS

### EMPLOYEE Role

**Primary Flows:**

1. **Apply for Leave**

   - Navigate to "Apply Leave"
   - Select leave type, dates, reason
   - View available balance (read from API)
   - Submit → Backend validates via policy engine
   - See confirmation + workflow status

2. **View Leave Balance**

   - Dashboard shows current balances
   - Click "Balance Details" → full breakdown (accrual, used, pending)
   - All calculations from backend

3. **View Leave History**

   - Table of all past requests (approved, rejected, withdrawn)
   - Filter by date range, status
   - Paginated results from API

4. **Withdraw Pending Request**
   - Click "Withdraw" on pending request
   - Confirm dialog
   - DELETE /api/v1/leave/requests/{id}
   - Refresh list via query invalidation

**UI Components:**

- `LeaveApplicationForm`
- `BalanceSummaryCard`
- `LeaveHistoryTable`
- `WithdrawRequestButton`

---

### MANAGER Role

**Primary Flows:**

1. **View Pending Approvals**

   - Dashboard shows approval queue
   - Sorted by submission date
   - Shows employee name, leave type, dates, balance impact

2. **Approve/Reject Request**

   - Click on request → detail modal
   - View employee balance, history, policy constraints
   - Add comments (required for rejection)
   - POST /api/v1/approvals/{id}/approve or /reject
   - Backend handles workflow progression

3. **View Team Calendar**

   - Calendar view of team's approved leave
   - Filter by team member, leave type
   - Identify coverage gaps

4. **View Team Reports**
   - Leave utilization metrics
   - Export to CSV (backend generates)

**UI Components:**

- `ApprovalQueue`
- `ApprovalDetailModal`
- `TeamCalendar`
- `TeamLeaveReport`

**Additional Access:**

- MANAGER also has EMPLOYEE permissions (can apply for own leave)

---

### HR_ADMIN Role

**Primary Flows:**

1. **View All Requests (System-Wide)**

   - Advanced filters: employee, department, date range, status
   - Export to Excel (backend generates)

2. **Trigger HRIS Sync**

   - Navigate to "Integrations"
   - Click "Sync HRIS" → POST /api/v1/integrations/hris/sync
   - View sync status (polling or SSE)
   - Display errors if sync fails

3. **Trigger Payroll Export**

   - Select pay period
   - Click "Generate Payroll Export"
   - Download CSV from backend

4. **View System Audit Logs**

   - Filter by user, action type, date
   - Read-only table

5. **Manage Leave Policies** (Future)
   - CRUD operations on leave types, accrual rules
   - Not implemented in Phase 21

**UI Components:**

- `SystemWideLeaveTable`
- `IntegrationPanel`
- `PayrollExportForm`
- `AuditLogViewer`

---

### AUDITOR Role

**Primary Flows:**

1. **View Audit Logs**

   - Read-only access to all audit events
   - Filter by entity type, user, timestamp
   - Export logs for compliance

2. **View Leave History (Read-Only)**
   - Cannot approve/reject
   - Can see all requests and decisions

**UI Components:**

- `AuditLogViewer` (same as HR_ADMIN, but no write actions)
- `ReadOnlyLeaveHistory`

---

### SYSTEM_ADMIN Role

**Primary Flows:**

1. **Manage Users**

   - Create/edit users
   - Assign roles
   - Deactivate accounts

2. **View System Health**
   - API metrics (from backend observability)
   - Error rates, latency

**UI Components:**

- `UserManagementTable`
- `SystemHealthDashboard`

---

## PHASE 21.5 – STATE MANAGEMENT

### State Architecture

**Two State Domains:**

1. **Server State** (managed by TanStack Query)

   - Leave requests, balances, approvals, audit logs
   - Cached, synchronized with backend
   - Invalidated on mutations

2. **UI State** (managed by Zustand or Context)
   - Sidebar open/closed
   - Theme (light/dark)
   - Active modals
   - Form draft state (if needed)

### TanStack Query Setup

**File:** `src/lib/react-query.ts`

```typescript
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 0,
    },
  },
});
```

### Query Hooks Pattern

**File:** `src/features/leave/hooks/useLeaveRequests.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leaveAPI } from "@/api/endpoints/leave.api";
import { mapAPIError } from "@/api/errors";

const QUERY_KEYS = {
  leaveRequests: ["leave", "requests"] as const,
  leaveBalance: ["leave", "balance"] as const,
};

export function useLeaveRequests(params?: { status?: string }) {
  return useQuery({
    queryKey: [...QUERY_KEYS.leaveRequests, params],
    queryFn: () => leaveAPI.getMyRequests(params),
  });
}

export function useLeaveBalance() {
  return useQuery({
    queryKey: QUERY_KEYS.leaveBalance,
    queryFn: () => leaveAPI.getBalance(),
  });
}

export function useCreateLeaveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: leaveAPI.createRequest,
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveRequests });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveBalance });
    },
    onError: (error) => {
      const mappedError = mapAPIError(error);
      console.error("Failed to create leave request:", mappedError);
    },
  });
}

export function useWithdrawLeaveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => leaveAPI.withdrawRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveRequests });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveBalance });
    },
  });
}
```

### Optimistic Updates (Limited Use)

**Only for non-critical UI actions** (e.g., marking notification as read).

**NOT for:**

- Leave balance calculations
- Approval decisions
- Financial data

**Example (Safe):**

```typescript
export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => notificationAPI.markRead(id),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["notifications"] });

      // Snapshot previous value
      const previous = queryClient.getQueryData(["notifications"]);

      // Optimistically update
      queryClient.setQueryData(["notifications"], (old: any) => ({
        ...old,
        items: old.items.map((n: any) =>
          n.id === id ? { ...n, read: true } : n
        ),
      }));

      return { previous };
    },
    onError: (err, id, context) => {
      // Rollback on error
      queryClient.setQueryData(["notifications"], context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
```

### Query Invalidation Strategy

| Event                   | Invalidate Queries                                            |
| ----------------------- | ------------------------------------------------------------- |
| Leave request created   | `leave.requests`, `leave.balance`                             |
| Leave request withdrawn | `leave.requests`, `leave.balance`                             |
| Leave approved/rejected | `approvals`, `leave.requests`, `leave.balance` (for employee) |
| HRIS sync completed     | `leave.balance`, `users`                                      |

---

## PHASE 21.6 – ERROR & LOADING STRATEGY

### Loading States

**Three Loading Patterns:**

1. **Initial Load** (first time fetching)

   ```tsx
   if (query.isLoading) return <SkeletonTable />;
   ```

2. **Background Refetch** (refetching with stale data)

   ```tsx
   {
     query.isFetching && <RefreshIndicator />;
   }
   ```

3. **Mutation in Progress**
   ```tsx
   <Button disabled={mutation.isPending}>
     {mutation.isPending ? "Submitting..." : "Submit"}
   </Button>
   ```

### Error States

**Unified Error Component:**

**File:** `src/components/feedback/ErrorState.tsx`

```typescript
import { APIError } from "@/api/errors";

interface ErrorStateProps {
  error: APIError;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const messages = {
    VALIDATION_ERROR: "Please check your input and try again.",
    FORBIDDEN: "You do not have permission for this action.",
    NOT_FOUND: "The requested resource was not found.",
    CONFLICT: "This action conflicts with existing data.",
    SERVER_ERROR: "An unexpected error occurred. Our team has been notified.",
    UNKNOWN_ERROR: "Something went wrong. Please try again.",
  };

  return (
    <div className="error-state">
      <AlertCircle className="error-icon" />
      <h3>{error.code.replace("_", " ")}</h3>
      <p>{messages[error.code] || error.message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          Try Again
        </Button>
      )}
    </div>
  );
}
```

### Empty States

**File:** `src/components/feedback/EmptyState.tsx`

```typescript
interface EmptyStateProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: ReactNode;
}

export function EmptyState({
  title,
  description,
  action,
  icon,
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      {icon}
      <h3>{title}</h3>
      <p>{description}</p>
      {action && <Button onClick={action.onClick}>{action.label}</Button>}
    </div>
  );
}
```

**Usage:**

```tsx
const { data, isLoading, error, refetch } = useLeaveRequests();

if (isLoading) return <SkeletonTable />;
if (error) return <ErrorState error={mapAPIError(error)} onRetry={refetch} />;
if (!data || data.items.length === 0) {
  return (
    <EmptyState
      title="No Leave Requests"
      description="You haven't submitted any leave requests yet."
      action={{
        label: "Apply for Leave",
        onClick: () => navigate("/leave/apply"),
      }}
    />
  );
}

return <LeaveTable data={data.items} />;
```

### Retry Strategy

**Automatic Retries:**

- GET requests: 1 retry (configured in QueryClient)
- POST/PUT/DELETE: 0 retries (avoid duplicate mutations)

**Manual Retry:**

- Expose `refetch` function in error state
- Let user decide when to retry

**Circuit Breaker (Future):**

- If backend is down (multiple 5xx), show global banner
- Pause automatic refetches

---

## WHAT NOT TO DO ❌

### ❌ Do NOT Duplicate Business Logic

**BAD:**

```typescript
// Frontend calculates balance
const availableBalance = totalBalance - usedBalance - pendingBalance;
```

**GOOD:**

```typescript
// Backend provides balance
const { availableBalance } = await leaveAPI.getBalance();
```

---

### ❌ Do NOT Enforce Security Only in UI

**BAD:**

```typescript
// Only UI check
if (user.role === "EMPLOYEE") {
  return <div>Access Denied</div>;
}
// No backend validation
```

**GOOD:**

```typescript
// UI check for UX
if (!hasRole("MANAGER")) {
  return <div>Access Denied</div>;
}
// Backend ALSO checks role on API call
const data = await approvalAPI.approve(id); // 403 if not authorized
```

---

### ❌ Do NOT Calculate Derived Data Client-Side

**BAD:**

```typescript
// Frontend calculates workflow status
const status =
  request.approved_by_manager && request.approved_by_hr
    ? "APPROVED"
    : "PENDING";
```

**GOOD:**

```typescript
// Backend provides status
const { status } = request; // Backend determines via workflow engine
```

---

### ❌ Do NOT Tightly Couple to Backend Internals

**BAD:**

```typescript
// Hardcoding backend table names
const query = `SELECT * FROM leave_requests WHERE user_id = ${userId}`;
```

**GOOD:**

```typescript
// Use backend-provided API
const requests = await leaveAPI.getMyRequests();
```

---

### ❌ Do NOT Store Sensitive Data in localStorage

**BAD:**

```typescript
localStorage.setItem("jwt", accessToken); // XSS vulnerable
```

**GOOD:**

```typescript
// In-memory storage OR httpOnly cookie
let accessToken: string | null = null;
```

---

## IMPLEMENTATION PHASES

### Phase 21.1: Scaffold & Setup

- [ ] Initialize Vite/Next.js project with TypeScript
- [ ] Configure Tailwind CSS
- [ ] Install TanStack Query, Axios, React Router
- [ ] Set up ESLint, Prettier
- [ ] Create folder structure

### Phase 21.2: Auth & API Layer

- [ ] Implement `AuthProvider` and token management
- [ ] Create Axios client with interceptors
- [ ] Generate TypeScript types from OpenAPI
- [ ] Build endpoint wrappers (`leave.api.ts`, etc.)
- [ ] Test API calls with mock backend

### Phase 21.3: Core Components

- [ ] Build UI component library (Button, Input, Card, Table)
- [ ] Create loading/error/empty state components
- [ ] Implement layout components (Sidebar, Header)
- [ ] Set up routing with protected routes

### Phase 21.4: Feature Modules

- [ ] **Employee:** Leave application form, balance view, history
- [ ] **Manager:** Approval queue, team calendar
- [ ] **HR Admin:** System reports, integration triggers
- [ ] **Auditor:** Audit log viewer

### Phase 21.5: Polish & Optimization

- [ ] Add skeleton loaders
- [ ] Implement toast notifications
- [ ] Add form validation (client-side only, not business rules)
- [ ] Optimize query caching
- [ ] Add E2E tests with Playwright

### Phase 21.6: Deployment Prep

- [ ] Environment variable configuration
- [ ] Build optimization (code splitting, lazy loading)
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)

---

## TESTING STRATEGY

### Unit Tests (Vitest)

- Pure utility functions
- Component rendering (React Testing Library)
- Hook behavior (without API calls)

### Integration Tests (MSW)

- API client with mocked responses
- Query hooks with mocked backend
- Form submission flows

### E2E Tests (Playwright)

- Critical user journeys:
  - Login → Apply Leave → Withdraw
  - Login as Manager → Approve Request
  - Login as HR → Trigger HRIS Sync
- Test against real backend (staging environment)

---

## DEPLOYMENT ARCHITECTURE

### Development

```
Frontend (Vite dev server) → http://localhost:5173
Backend (FastAPI) → http://localhost:8000
```

### Production (Recommended)

```
Nginx/Caddy
├── /api/* → Backend (FastAPI)
└── /* → Frontend (Static SPA)
```

**OR Next.js SSR:**

```
Next.js Server → Calls Backend API server-side
```

### Environment Variables

**`.env.development`**

```
VITE_API_BASE_URL=http://localhost:8000
VITE_OAUTH_CLIENT_ID=your-client-id
VITE_OAUTH_AUTHORITY=https://your-idp.com
```

**`.env.production`**

```
VITE_API_BASE_URL=https://api.lms.company.com
VITE_OAUTH_CLIENT_ID=prod-client-id
VITE_OAUTH_AUTHORITY=https://idp.company.com
```

---

## PERFORMANCE CHECKLIST

- [ ] Code splitting (lazy load routes)
- [ ] Image optimization (use Next/Image or similar)
- [ ] TanStack Query caching (staleTime, cacheTime)
- [ ] Debounce search inputs
- [ ] Virtualize long lists (react-window)
- [ ] Compress assets (gzip/brotli)
- [ ] Use React.memo for expensive components
- [ ] Avoid unnecessary re-renders (useMemo, useCallback)

---

## ACCESSIBILITY (a11y) CHECKLIST

- [ ] Semantic HTML (header, main, nav, footer)
- [ ] ARIA labels for interactive elements
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus management (modals, drawers)
- [ ] Color contrast (WCAG AA minimum)
- [ ] Screen reader testing (NVDA, JAWS)
- [ ] Skip navigation links

---

## NEXT STEPS (Phase 22)

1. **Scaffold Frontend Project**

   - Initialize repo with chosen framework (Vite recommended)
   - Set up TailwindCSS with design tokens
   - Configure TanStack Query

2. **Implement Auth Flow**

   - Integrate with OAuth2/OIDC provider
   - Build login/logout flows
   - Test token refresh

3. **Build Employee Flow**

   - Leave application form
   - Balance display
   - Leave history table

4. **Build Manager Flow**

   - Approval queue
   - Approve/reject actions

5. **Deploy to Staging**
   - Dockerize frontend
   - Deploy alongside backend
   - E2E testing

---

## CONCLUSION

This architecture ensures:

✅ **Separation of Concerns:** Backend owns logic, frontend owns presentation  
✅ **Type Safety:** OpenAPI-generated types prevent contract drift  
✅ **Security:** Backend enforces RBAC, frontend provides UX only  
✅ **Maintainability:** Clear folder structure, domain-driven features  
✅ **Scalability:** TanStack Query handles caching, easy to add new features  
✅ **Developer Experience:** Clear patterns, easy onboarding, great tooling

**The frontend is now ready to be scaffolded in Phase 22.**

---

**Document Version:** 1.0  
**Last Updated:** December 19, 2025  
**Prepared By:** GitHub Copilot (Architecture Design)
