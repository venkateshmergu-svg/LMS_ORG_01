# LMS FRONTEND WORKSPACE

Complete frontend scaffolding for the Leave Management System.

## Quick Links

### Documentation
- **[Phase 21: Frontend Architecture](../PHASE_21_FRONTEND_ARCHITECTURE.md)** — Design & patterns
- **[Phase 22: Frontend Scaffolding](../PHASE_22_FRONTEND_SCAFFOLDING.md)** — This phase, current status
- **[README.md](./README.md)** — Developer quick start & API reference

### Source Code
- **[src/auth/](./src/auth/)** — Authentication & authorization
- **[src/api/](./src/api/)** — API clients & type contracts
- **[src/features/](./src/features/)** — Domain-specific modules
- **[src/app/](./src/app/)** — Page routing & layouts
- **[src/components/](./src/components/)** — Reusable UI primitives

### Configuration
- `package.json` — Dependencies & npm scripts
- `tsconfig.json` — TypeScript strict mode
- `vite.config.ts` — Dev server & API proxy
- `tailwind.config.js` — Design system
- `.env.development` — Local environment variables
- `.env.production` — Production environment variables

## Getting Started (< 5 minutes)

### Prerequisites
- Node.js 18+ and npm 9+
- Backend running on `http://localhost:8000`

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173 in browser
```

## Architecture at a Glance

```
┌─────────────────────────────────────────┐
│       React 18 + TypeScript             │
│   (src/app/ → src/features/ → src/api/) │
├─────────────────────────────────────────┤
│  • Auth Context (JWT, roles)            │
│  • React Query (server state caching)   │
│  • React Router (protected routes)      │
│  • Tailwind CSS (styling)               │
├─────────────────────────────────────────┤
│  Axios with Auto Token Refresh          │
│  OpenAPI-Generated Types                │
│  Error Mapping & Handling               │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS
               ▼
     ┌────────────────────────┐
     │  FastAPI Backend       │
     │  (Source of Truth)     │
     └────────────────────────┘
```

## What's Ready

| Component | Status | Notes |
|-----------|--------|-------|
| Project structure | ✅ | 25+ folders organized |
| Config files | ✅ | TypeScript, Vite, Tailwind |
| Auth system | ✅ | JWT handling, token refresh, RBAC |
| API client | ✅ | Axios with interceptors |
| Type safety | ✅ | OpenAPI-ready, manual types in place |
| Pages (basic) | ✅ | Dashboard, login, leave app, approvals, audit |
| React Query | ✅ | Setup with sensible defaults |
| Styling | ✅ | Tailwind CSS with custom tokens |
| ESLint/Prettier | ✅ | Code quality configured |

## What's Next (Phase 23)

- [ ] OAuth2 login integration
- [ ] Form validation & submission
- [ ] Manager approval UI
- [ ] Balance display widget
- [ ] Audit log viewer
- [ ] HR admin dashboard
- [ ] E2E tests
- [ ] Docker & deployment

## Scripts

```bash
npm run dev              # Start dev server (HMR enabled)
npm run build           # Production build
npm run preview         # Preview production build
npm run lint            # Check code quality
npm run format          # Auto-format code
npm run type-check      # TypeScript validation
```

## Key Concepts

### 1. Thin Client
No business logic in frontend. Backend enforces rules, balances, workflows.

### 2. Server State Management
TanStack Query caches API data. Backend is source of truth.

### 3. Type Safety
All API types generated from OpenAPI spec. Catch bugs at compile time.

### 4. Security
- Tokens in memory (XSS safe)
- JWT auto-refresh on 401
- Backend enforces RBAC (UI is UX only)

### 5. Developer Experience
Clear patterns, zero boilerplate, fast iteration.

## File Structure

```
frontend/
├── src/
│   ├── app/               # Routes & pages
│   ├── auth/              # OAuth, JWT, RBAC
│   ├── api/               # Axios, types, endpoints
│   ├── features/          # Leave, approvals, balance, audit, admin
│   ├── components/        # UI primitives & layouts
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Config (React Query, etc.)
│   ├── styles/            # Global CSS
│   ├── types/             # TypeScript definitions
│   ├── utils/             # Pure utility functions
│   └── main.tsx           # Entry point
├── public/                # Static assets
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Build config
├── index.html             # HTML template
├── README.md              # Full documentation
└── .env.*                 # Environment variables
```

## API Endpoints Used

**Auth:**
- POST `/api/v1/auth/me` — Current user
- POST `/api/v1/auth/refresh` — Token refresh

**Leave:**
- GET `/api/v1/leave/requests` — My requests
- POST `/api/v1/leave/requests` — Create request
- DELETE `/api/v1/leave/requests/{id}` — Withdraw
- GET `/api/v1/leave/balance` — My balance

**Approvals:**
- GET `/api/v1/approvals/pending` — My approvals
- POST `/api/v1/approvals/{id}/approve` — Approve
- POST `/api/v1/approvals/{id}/reject` — Reject

**Audit:**
- GET `/api/v1/audit/logs` — Audit logs

## Frontend Roles

| Role | Permissions | Routes |
|------|-----------|--------|
| EMPLOYEE | Apply, view own | /leave/apply, /leave/history |
| MANAGER | Employee + approve | /approvals, /team |
| HR_ADMIN | Manager + reports | /reports, /integrations |
| AUDITOR | Read-only logs | /audit |
| SYSTEM_ADMIN | Full access | All |

## Common Tasks

### Add a new API endpoint

```typescript
// 1. src/api/endpoints/feature.api.ts
export const featureAPI = {
  getData: async () => { ... }
};

// 2. src/features/feature/hooks/useFeature.ts
export function useFeature() {
  return useQuery({
    queryKey: ['feature'],
    queryFn: () => featureAPI.getData(),
  });
}

// 3. Use in component
const { data } = useFeature();
```

### Add a new page

```typescript
// 1. Create src/app/feature/FeaturePage.tsx
// 2. Add route to src/app/App.tsx
// 3. Link from navigation
```

### Protect a route

```typescript
<ProtectedRoute requiredRoles={['MANAGER']}>
  <ManagerOnlyPage />
</ProtectedRoute>
```

## Environment Setup

### Development (.env.development)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_OAUTH_CLIENT_ID=dev-client-id
VITE_OAUTH_AUTHORITY=http://localhost:8000
```

### Production (.env.production)
```env
VITE_API_BASE_URL=https://api.company.com
VITE_OAUTH_CLIENT_ID=prod-client-id
VITE_OAUTH_AUTHORITY=https://idp.company.com
```

## Troubleshooting

**Port 5173 taken?**
```bash
npm run dev -- --port 3000
```

**Backend not responding?**
Check `vite.config.ts` proxy target matches backend URL.

**TypeScript errors?**
```bash
npm run type-check
# Regenerate types from backend
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types/generated.ts
```

**Dependencies issues?**
```bash
rm -rf node_modules package-lock.json
npm install
```

## Status

✅ **Phase 22 Complete** — Frontend scaffolding finished
🔳 **Phase 23 Next** — OAuth2 integration & feature implementation

## Resources

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com/)

---

**Created:** December 19, 2025  
**Ready for:** Phase 23 (Feature Implementation)  
**Scalable to:** 50+ features without refactoring
