# LMS Frontend

Production-grade Leave Management System (LMS) frontend built with React 18, TypeScript, Vite, and TanStack Query.

## Overview

This frontend is designed as a **thin client** that consumes the authoritative FastAPI backend. All business logic, security enforcement, and data calculations happen server-side. The frontend is responsible for:

- User interface and experience
- Role-based navigation (UX only)
- Form input and validation (client-side only, not business rules)
- State caching with TanStack Query
- API communication with proper error handling

## Quick Start

### Prerequisites

- **Node.js 18+** and **npm 9+**
- **Backend** running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Server runs at `http://localhost:5173` with HMR enabled.

The Vite config automatically proxies `/api/*` requests to the backend.

### Build

```bash
npm run build
```

Creates optimized production build in `dist/`.

### Type Checking

```bash
npm run type-check
```

### Linting & Formatting

```bash
npm run lint
npm run format
```

## Project Structure

### `src/app/`

Application routing, page layouts, and route definitions.

```
app/
├── App.tsx              # Main router setup
├── dashboard/           # Dashboard pages
├── leave/               # Leave management pages
├── approvals/           # Manager approval flows
├── audit/               # Audit log viewer
└── login/               # Login page
```

### `src/auth/`

Authentication layer with OAuth2/OIDC support.

```
auth/
├── AuthProvider.tsx     # Auth context and state
├── ProtectedRoute.tsx   # Route guards
├── RoleGate.tsx         # Component-level RBAC
└── tokens.ts            # Token storage (in-memory)
```

### `src/api/`

API clients and type contracts.

```
api/
├── client.ts            # Axios instance with interceptors
├── errors.ts            # Error mapping utilities
├── types/
│   └── generated.ts     # OpenAPI-generated types
└── endpoints/
    ├── leave.api.ts     # Leave API wrapper
    └── approvals.api.ts # Approvals API wrapper
```

### `src/features/`

Domain-specific feature modules.

```
features/
├── leave/
│   ├── components/      # Leave UI components
│   ├── hooks/           # useLeaveRequests, etc.
│   └── types.ts
├── approvals/           # Manager approval flows
├── balance/             # Balance display
├── audit/               # Audit log viewing
└── admin/               # HR admin features
```

### `src/components/`

Reusable UI primitives and layouts.

```
components/
├── ui/                  # Button, Input, Card, etc.
├── layout/              # Header, Sidebar, Footer
├── feedback/            # Loading, Error, Empty states
└── data-display/        # Table, Badge, etc.
```

### `src/lib/`

Third-party library configuration.

```
lib/
└── react-query.ts       # QueryClient setup
```

### `src/utils/`

Pure utility functions.

## Architecture Decisions

### 1. **Thin Client Principle**

- ✅ **NO** balance calculations (backend provides `available`, `used`, `pending`)
- ✅ **NO** workflow state determination (backend determines status via workflow engine)
- ✅ **NO** business rule validation (backend enforces via policy engine)
- ✅ **UI RBAC is UX only** (backend enforces authorization on every API call)

### 2. **Token Management**

Tokens are stored **in-memory** (not in localStorage) to prevent XSS attacks:

```typescript
// In src/auth/tokens.ts
let accessToken: string | null = null;

// Tokens are attached to all API requests via interceptor
// If invalid, backend returns 401, frontend refreshes or redirects to login
```

For production with stricter requirements, use **httpOnly cookies** issued by the backend.

### 3. **State Management**

Two-layer approach:

| State | Manager | Example |
|-------|---------|---------|
| **Server State** | TanStack Query | Leave requests, balances, approvals |
| **UI State** | React Context / Zustand | Sidebar open/closed, theme, modal state |

**Rule:** Server data is cached, but backend is always the source of truth.

### 4. **Error Handling**

All HTTP errors are mapped to user-friendly messages:

```typescript
// From src/api/errors.ts
mapAPIError(error) → {
  code: 'VALIDATION_ERROR',
  message: 'Please check your input and try again.',
  field: 'email',
}
```

### 5. **API Types**

Types are **generated from OpenAPI spec** (single source of truth):

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types/generated.ts
```

If OpenAPI unavailable, manually curate types in `src/api/types/generated.ts`.

## OAuth2 / OIDC Integration

**TODO:** Implement OAuth2 flow on the login page.

Example flow:

1. User clicks "Sign in with OAuth"
2. Redirect to `/authorize` endpoint
3. IDP redirects back to `/callback` with auth code
4. Exchange code for `access_token` and `refresh_token`
5. Call `AuthProvider.login(accessToken, refreshToken)`
6. AuthProvider fetches user profile and redirects to dashboard

Recommended library: **react-oauth-flow** or **oidc-client-ts**

## API Endpoints (Backend Contract)

All endpoints assume JWT bearer token in `Authorization` header:

```bash
Authorization: Bearer <access_token>
```

### Authentication

- `POST /api/v1/auth/me` — Get current user profile
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/logout` — Logout

### Leave Management

- `GET /api/v1/leave/requests` — List my leave requests
- `POST /api/v1/leave/requests` — Create leave request
- `DELETE /api/v1/leave/requests/{id}` — Withdraw request
- `GET /api/v1/leave/balance` — Get leave balance

### Approvals (Manager)

- `GET /api/v1/approvals/pending` — List pending approvals
- `POST /api/v1/approvals/{id}/approve` — Approve request
- `POST /api/v1/approvals/{id}/reject` — Reject request

### Reports (HR Admin)

- `GET /api/v1/reports/leave-usage` — Leave utilization report
- `POST /api/v1/reports/export` — Export to CSV

### Audit (Auditor / HR Admin)

- `GET /api/v1/audit/logs` — List audit logs

### Integrations (HR Admin)

- `POST /api/v1/integrations/hris/sync` — Trigger HRIS sync
- `POST /api/v1/integrations/payroll/export` — Generate payroll export

## Development Workflow

### 1. Add a New API Endpoint

**File:** `src/api/endpoints/new-feature.api.ts`

```typescript
import { apiClient } from '../client';
import type { MyType } from '../types/generated';

export const newFeatureAPI = {
  getData: async (): Promise<MyType> => {
    const { data } = await apiClient.get('/api/v1/new-feature');
    return data;
  },
};
```

### 2. Create a Query Hook

**File:** `src/features/new-feature/hooks/useNewFeature.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { newFeatureAPI } from '@/api/endpoints/new-feature.api';

export function useNewFeature() {
  return useQuery({
    queryKey: ['new-feature'],
    queryFn: () => newFeatureAPI.getData(),
  });
}
```

### 3. Use in Component

```typescript
import { useNewFeature } from '@/features/new-feature/hooks/useNewFeature';

export function MyComponent() {
  const { data, isLoading, error } = useNewFeature();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{JSON.stringify(data)}</div>;
}
```

## Role-Based Features

### EMPLOYEE

- Apply for leave (POST /api/v1/leave/requests)
- View own balance and history
- Withdraw pending requests

### MANAGER

- All EMPLOYEE permissions
- View pending approvals
- Approve / reject requests
- View team calendar

### HR_ADMIN

- All MANAGER permissions
- View system-wide reports
- Trigger HRIS / Payroll sync
- View audit logs

### AUDITOR

- View audit logs (read-only)
- View leave history (read-only)

### SYSTEM_ADMIN

- Full system access

## Performance Optimization

### 1. Code Splitting

Routes are lazy-loaded by React Router:

```typescript
const DashboardPage = lazy(() => import('./pages/Dashboard'));
```

### 2. Query Caching

TanStack Query caches API responses:

```typescript
{
  staleTime: 1000 * 60 * 5,      // 5 min
  gcTime: 1000 * 60 * 30,        // 30 min
}
```

### 3. Virtualization

For large tables (100+ rows), use `react-window`:

```typescript
import { FixedSizeList } from 'react-window';
```

### 4. Memoization

Prevent unnecessary re-renders:

```typescript
const MyComponent = memo(({ data }) => ...);
```

## Testing

### Unit Tests (Vitest)

```bash
npm run test
```

### E2E Tests (Playwright)

```bash
npm run test:e2e
```

Test critical user journeys against real backend.

## Deployment

### Production Build

```bash
npm run build
```

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

Create `.env.production`:

```env
VITE_API_BASE_URL=https://api.lms.company.com
VITE_OAUTH_CLIENT_ID=prod-client-id
VITE_OAUTH_AUTHORITY=https://idp.company.com
```

## Troubleshooting

### Token Refresh Loop

If stuck in auth loop, check:

1. Backend's `/api/v1/auth/refresh` endpoint returns valid token
2. `RefreshToken` is valid and not expired
3. Network tab shows 200 on refresh request

### CORS Errors

Ensure Vite proxy config matches backend URL:

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000', // Match your backend
    changeOrigin: true,
  },
}
```

### Type Generation Failed

Regenerate types from OpenAPI spec:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types/generated.ts
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│       Browser (React 18 + TS)           │
├─────────────────────────────────────────┤
│  App Component                          │
│  ├─ Router (React Router)               │
│  ├─ AuthProvider (JWT context)          │
│  └─ QueryClientProvider (TanStack)      │
├─────────────────────────────────────────┤
│  Features (leave, approvals, etc.)      │
│  ├─ useLeaveRequests() [React Query]    │
│  ├─ useAuth() [Auth Context]            │
│  └─ Components (UI primitives)          │
├─────────────────────────────────────────┤
│  API Client (Axios)                     │
│  ├─ Request Interceptor (add JWT)       │
│  └─ Response Interceptor (401 refresh)  │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS
               ▼
    ┌──────────────────────────┐
    │   FastAPI Backend        │
    │ (Source of Truth)        │
    │                          │
    │ - Workflow Engine        │
    │ - Balance Accounting     │
    │ - RBAC Enforcement       │
    │ - Audit Logging          │
    └──────────────────────────┘
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow code style: `npm run lint && npm run format`
3. Write tests for new features
4. Submit PR with description

## License

Proprietary - Leave Management System

## Next Steps (Phase 23)

- [ ] Implement OAuth2 login flow
- [ ] Add form validation and submission
- [ ] Build manager approval UI
- [ ] Create HR admin dashboard
- [ ] Add E2E tests
- [ ] Performance profiling
- [ ] Deploy to staging
