# Frontend Navigation Index

**Complete guide to all frontend files, documentation, and phases**

---

## 📚 Documentation (Read These First)

| Document | Purpose | Time |
|----------|---------|------|
| [README.md](README.md) | Getting started, setup, local development | 10 min |
| [PHASE_21_ARCHITECTURE.md](PHASE_21_ARCHITECTURE.md) | Design principles, patterns, tech stack | 20 min |
| [PHASE_22_SCAFFOLDING.md](PHASE_22_SCAFFOLDING.md) | Project structure, folder organization | 15 min |
| [PHASE_23_IMPLEMENTATION_PLAN.md](PHASE_23_IMPLEMENTATION_PLAN.md) | Feature implementation roadmap | 30 min |
| [PHASE_23_COMPLETION_STATUS.md](PHASE_23_COMPLETION_STATUS.md) | What was built in Phase 23 ✅ | 20 min |
| [PHASE_23_COMPONENT_GUIDE.md](PHASE_23_COMPONENT_GUIDE.md) | How to use all Phase 23 components | 20 min |

---

## 🔒 GOVERNANCE & QUALITY GATES (Phase 26)

| Document | Purpose | Audience |
|----------|---------|----------|
| [FRONTEND_GOVERNANCE.md](FRONTEND_GOVERNANCE.md) | Overview of governance framework, principles, enforcement | All developers, reviewers |
| [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) | **MANDATORY** checklist every change must satisfy | Developers, code reviewers |
| [CODING_STANDARDS.md](CODING_STANDARDS.md) | Naming conventions, component structure, patterns, examples | All developers |
| [PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md) | **MANDATORY** checklist for PR reviewers before approval | Code reviewers, tech leads |
| [API_CONTRACT_GOVERNANCE.md](API_CONTRACT_GOVERNANCE.md) | Rules for consuming backend APIs, versioning, breaking changes | Developers, API integrators |
| [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md) | Deployment process, testing, rollback, communication | Release engineers, tech leads |

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── api/                      # API integration layer
│   │   ├── client.ts             # Axios instance with interceptors
│   │   ├── errors.ts             # HTTP error mapping
│   │   ├── endpoints/            # Typed API endpoint wrappers
│   │   │   ├── leave.api.ts
│   │   │   └── approvals.api.ts
│   │   └── types/
│   │       └── generated.ts      # TypeScript types from API
│   │
│   ├── app/                      # Page routes
│   │   ├── App.tsx               # Main router
│   │   ├── login/
│   │   │   └── LoginPage.tsx     # OAuth login with provider
│   │   ├── auth/
│   │   │   └── CallbackPage.tsx  # OAuth callback handler
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx # Main dashboard with stats
│   │   ├── leave/
│   │   │   ├── LeaveApplicationPage.tsx    # Form to apply
│   │   │   └── LeaveHistoryPage.tsx        # List of requests
│   │   ├── approvals/
│   │   │   └── ApprovalsPage.tsx           # Manager approval queue
│   │   ├── calendar/
│   │   │   └── CalendarPage.tsx            # Team calendar
│   │   ├── audit/
│   │   │   └── AuditPage.tsx               # Audit logs
│   │   └── errors/
│   │       ├── UnauthorizedPage.tsx
│   │       └── NotFoundPage.tsx
│   │
│   ├── auth/                     # Authentication layer
│   │   ├── AuthProvider.tsx      # User context & JWT mgmt
│   │   ├── tokens.ts             # Token storage (in-memory)
│   │   ├── ProtectedRoute.tsx    # Route guard component
│   │   └── RoleGate.tsx          # Conditional rendering by role
│   │
│   ├── components/               # Shared UI components
│   │   ├── common/               # Generic reusable components
│   │   │   ├── ErrorAlert.tsx
│   │   │   ├── SuccessAlert.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── Modal.tsx
│   │   ├── layout/               # Page layout components
│   │   │   ├── MainLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   └── inputs/               # Form input components
│   │       ├── TextField.tsx
│   │       ├── SelectField.tsx
│   │       └── DateField.tsx
│   │
│   ├── features/                 # Domain-specific feature modules
│   │   ├── leave/                # Leave management feature
│   │   │   ├── components/
│   │   │   │   ├── LeaveForm.tsx (PHASE 23) ✨
│   │   │   │   ├── LeaveCard.tsx
│   │   │   │   └── LeaveTable.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useLeaveRequests.ts
│   │   │   ├── types.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── approvals/            # Approval management feature
│   │   │   ├── components/
│   │   │   │   ├── ApprovalQueue.tsx (PHASE 23) ✨
│   │   │   │   ├── ApprovalDetailModal.tsx (PHASE 23) ✨
│   │   │   │   └── ApprovalCard.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useApprovalsQuery.ts (PHASE 23) ✨
│   │   │   ├── types.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── balance/              # Balance tracking feature
│   │   │   ├── components/
│   │   │   │   └── BalanceCard.tsx (PHASE 23) ✨
│   │   │   ├── hooks/
│   │   │   │   └── useBalance.ts
│   │   │   ├── types.ts
│   │   │   └── constants.ts
│   │   │
│   │   └── audit/                # Audit logging feature
│   │       ├── components/
│   │       │   └── AuditLog.tsx
│   │       ├── hooks/
│   │       │   └── useAuditLogs.ts
│   │       ├── types.ts
│   │       └── constants.ts
│   │
│   ├── lib/                      # Utility libraries
│   │   ├── oauth.ts (PHASE 23) ✨ # OAuth configuration & methods
│   │   ├── dates.ts              # Date formatting utilities
│   │   ├── validators.ts         # Validation functions
│   │   └── constants.ts          # Global constants
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useQueryParams.ts
│   │   ├── usePagination.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── styles/                   # Global styles
│   │   ├── globals.css           # Tailwind + custom components
│   │   ├── variables.css         # CSS variables
│   │   └── animations.css        # Custom animations
│   │
│   ├── main.tsx                  # React entry point
│   ├── index.html                # HTML template
│   └── vite-env.d.ts             # Vite type definitions
│
├── tests/                        # Test files (mirrors src/)
│   ├── components/
│   ├── features/
│   └── hooks/
│
├── public/                       # Static assets
│   ├── favicon.ico
│   └── logo.svg
│
├── Configuration Files
│   ├── package.json              # Dependencies & scripts
│   ├── tsconfig.json             # TypeScript config (strict mode)
│   ├── vite.config.ts            # Vite bundler config
│   ├── tailwind.config.js        # Tailwind CSS config
│   ├── postcss.config.js         # PostCSS config
│   ├── .eslintrc.json            # ESLint rules
│   ├── .prettierrc.json          # Prettier formatting
│   ├── .env.development          # Dev environment variables
│   ├── .env.production           # Prod environment variables
│   ├── .gitignore                # Git ignore rules
│   └── .nvmrc                    # Node version specification
│
└── Documentation
    ├── README.md                 # Getting started
    ├── PHASE_21_ARCHITECTURE.md  # Design doc
    ├── PHASE_22_SCAFFOLDING.md   # Structure doc
    ├── PHASE_23_IMPLEMENTATION_PLAN.md
    ├── PHASE_23_COMPLETION_STATUS.md (THIS PHASE)
    ├── PHASE_23_COMPONENT_GUIDE.md (THIS PHASE)
    └── FRONTEND_NAVIGATION_INDEX.md (this file)
```

---

## 🧩 Component Map

### Pages (in `src/app/`)

| Page | Route | Purpose | Status |
|------|-------|---------|--------|
| LoginPage | `/login` | OAuth login | ✅ Complete (Phase 23) |
| CallbackPage | `/auth/callback` | OAuth callback handler | ✅ Complete (Phase 23) |
| DashboardPage | `/dashboard` | Main dashboard | ✅ Complete (Phase 23) |
| LeaveApplicationPage | `/leave/application` | Apply for leave | ✅ Complete (Phase 23) |
| LeaveHistoryPage | `/leave/history` | View leave history | ⏳ Partial (template) |
| ApprovalsPage | `/approvals` | Manager approval queue | ✅ Complete (Phase 23) |
| CalendarPage | `/calendar` | Team calendar | ⏳ Partial (template) |
| AuditPage | `/audit` | Audit logs | ⏳ Partial (template) |
| UnauthorizedPage | `/unauthorized` | 403 error page | ✅ Complete |
| NotFoundPage | `/*` | 404 error page | ✅ Complete |

### Features (in `src/features/`)

#### Leave Management
| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| LeaveForm | `leave/components/LeaveForm.tsx` | Apply for leave form | ✅ Phase 23 |
| LeaveCard | `leave/components/LeaveCard.tsx` | Single leave request card | 📋 Template |
| LeaveTable | `leave/components/LeaveTable.tsx` | List of requests | 📋 Template |
| useLeaveRequests | `leave/hooks/useLeaveRequests.ts` | Query hook for requests | ✅ Implemented |
| useLeaveBalance | (part of above) | Query hook for balance | ✅ Implemented |
| useCreateLeaveRequest | (part of above) | Mutation hook | ✅ Implemented |

#### Approvals
| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| ApprovalQueue | `approvals/components/ApprovalQueue.tsx` | Paginated approval table | ✅ Phase 23 |
| ApprovalDetailModal | `approvals/components/ApprovalDetailModal.tsx` | Approval action modal | ✅ Phase 23 |
| ApprovalCard | `approvals/components/ApprovalCard.tsx` | Single approval card | 📋 Template |
| useApprovalsQuery | `approvals/hooks/useApprovalsQuery.ts` | Query + mutation hooks | ✅ Phase 23 |

#### Balance
| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| BalanceCard | `balance/components/BalanceCard.tsx` | Balance display widget | ✅ Phase 23 |
| useLeaveBalance | `leave/hooks/useLeaveRequests.ts` | Balance query hook | ✅ Implemented |

#### Audit
| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| AuditLog | `audit/components/AuditLog.tsx` | Audit log entry | 📋 Template |
| useAuditLogs | `audit/hooks/useAuditLogs.ts` | Audit query hook | ⏳ Pending |

### Shared Components (in `src/components/`)

#### Common (Generic UI)
| Component | File | Purpose |
|-----------|------|---------|
| ErrorAlert | `common/ErrorAlert.tsx` | Error message display |
| SuccessAlert | `common/SuccessAlert.tsx` | Success message display |
| LoadingSpinner | `common/LoadingSpinner.tsx` | Loading indicator |
| Modal | `common/Modal.tsx` | Reusable modal dialog |

#### Layout
| Component | File | Purpose |
|-----------|------|---------|
| MainLayout | `layout/MainLayout.tsx` | Page wrapper |
| Sidebar | `layout/Sidebar.tsx` | Left navigation |
| Header | `layout/Header.tsx` | Top navigation |
| Footer | `layout/Footer.tsx` | Footer content |

#### Inputs
| Component | File | Purpose |
|-----------|------|---------|
| TextField | `inputs/TextField.tsx` | Text input |
| SelectField | `inputs/SelectField.tsx` | Dropdown select |
| DateField | `inputs/DateField.tsx` | Date picker |

---

## 🔗 API Endpoints Reference

All endpoints are typed and wrapped in `src/api/endpoints/`:

### Authentication
```
POST   /api/v1/auth/token        # OAuth token exchange
GET    /api/v1/auth/me           # Get current user
POST   /api/v1/auth/refresh      # Refresh access token
POST   /api/v1/auth/logout       # Logout
```

### Leave Management
```
GET    /api/v1/leave/balance     # Get leave balance
GET    /api/v1/leave/requests    # List my requests
POST   /api/v1/leave/requests    # Create request
DELETE /api/v1/leave/requests/:id # Withdraw request
```

### Approvals
```
GET    /api/v1/approvals         # Get pending approvals (manager)
POST   /api/v1/approvals/:id/approve  # Approve request
POST   /api/v1/approvals/:id/reject   # Reject request
```

### Audit
```
GET    /api/v1/audit/logs        # Get audit logs (admin)
GET    /api/v1/audit/logs/:id    # Get single audit log
```

See `src/api/endpoints/` for full type definitions.

---

## 🔑 Key Files by Purpose

### Authentication
- `src/auth/AuthProvider.tsx` - User state & JWT management
- `src/auth/tokens.ts` - Token storage (in-memory)
- `src/auth/ProtectedRoute.tsx` - Route guard
- `src/auth/RoleGate.tsx` - Role-based conditional rendering
- `src/lib/oauth.ts` - OAuth utilities (Phase 23)
- `src/app/auth/CallbackPage.tsx` - OAuth callback (Phase 23)

### API Integration
- `src/api/client.ts` - Axios instance with interceptors
- `src/api/errors.ts` - HTTP error mapping
- `src/api/endpoints/leave.api.ts` - Leave endpoints
- `src/api/endpoints/approvals.api.ts` - Approval endpoints
- `src/api/types/generated.ts` - TypeScript type definitions

### Forms & Validation
- `src/features/leave/components/LeaveForm.tsx` - Leave form (Phase 23)
- `src/lib/validators.ts` - Custom validation functions

### Data Management (React Query)
- `src/features/leave/hooks/useLeaveRequests.ts` - Leave queries
- `src/features/approvals/hooks/useApprovalsQuery.ts` - Approval queries (Phase 23)

### UI Components
- `src/components/common/` - Generic UI components
- `src/components/layout/` - Layout components
- `src/components/inputs/` - Form input components
- `src/globals.css` - Component classes (.card, .btn, .badge, etc.)

### Styling
- `src/globals.css` - Tailwind utilities + custom components
- `src/styles/variables.css` - CSS variables
- `tailwind.config.js` - Tailwind theme customization
- `.eslintrc.json` - Code style rules

---

## 🚀 Getting Started

### 1. Setup
```bash
cd frontend
npm install
```

### 2. Environment Variables
```bash
cp .env.development .env.local
# Edit with your OAuth provider credentials
```

### 3. Local Development
```bash
npm run dev
# Opens http://localhost:5173
```

### 4. Build for Production
```bash
npm run build
npm run preview  # Test build locally
```

---

## 📖 Documentation Sections

### For Users
- README.md - Getting started
- PHASE_23_COMPONENT_GUIDE.md - How to use components

### For Developers
- PHASE_21_ARCHITECTURE.md - Design patterns
- PHASE_22_SCAFFOLDING.md - Project structure
- PHASE_23_IMPLEMENTATION_PLAN.md - Feature roadmap
- PHASE_23_COMPLETION_STATUS.md - What's built

### API Contract
- `src/api/endpoints/` - Typed endpoint wrappers
- `src/api/types/generated.ts` - Complete type definitions

---

## ✅ Phase 23 Completion Summary

**What was built:**
1. ✅ OAuth2 authentication (oauth.ts + CallbackPage.tsx)
2. ✅ Leave application form with validation (LeaveForm.tsx)
3. ✅ Manager approval queue with modal (ApprovalQueue.tsx + ApprovalDetailModal.tsx)
4. ✅ Balance display widget (BalanceCard.tsx)
5. ✅ Updated pages to use real components
6. ✅ Approval mutation hooks (useApprovalsQuery.ts)
7. ✅ Full TypeScript typing throughout

**Files created:** 10  
**Files updated:** 7  
**Lines of code:** 2,500+

---

## 🔄 Common Workflows

### Add a New Page
1. Create component in `src/app/{feature}/`
2. Add route in `src/app/App.tsx`
3. Add navigation link in `Sidebar.tsx`
4. Wrap in `ProtectedRoute` if needed

### Add a New Feature
1. Create folder in `src/features/{feature}/`
2. Create `components/`, `hooks/`, `types.ts`
3. Create custom hook using React Query
4. Import in components

### Make API Call
1. Create endpoint wrapper in `src/api/endpoints/`
2. Create React Query hook using it
3. Use hook in component
4. API client handles JWT automatically

### Style a Component
1. Use Tailwind utility classes
2. Use custom classes from `.card`, `.btn`, `.badge` (globals.css)
3. Use CSS variables for colors (`--primary`, etc.)
4. Test in dark mode

---

## 🐛 Debugging

### React DevTools
```
npm install -D @react-devtools/shell
```

### React Query DevTools
```
npm install -D @tanstack/react-query-devtools
```

### TypeScript Errors
```
npm run type-check  # Check types without building
```

### ESLint Warnings
```
npm run lint        # Check code style
npm run lint:fix    # Auto-fix violations
```

---

## 🎓 Learn More

- [React Documentation](https://react.dev)
- [React Hook Form Guide](https://react-hook-form.com)
- [React Query Documentation](https://tanstack.com/query)
- [Tailwind CSS Docs](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev)

---

## 📞 Support

- Check `PHASE_23_COMPONENT_GUIDE.md` for component usage
- Check error messages in browser console
- Check API responses in Network tab (DevTools)
- Check `src/api/types/generated.ts` for data types

---

**Status:** Phase 23 ✅ COMPLETE  
**Next:** Phase 24 - Tier 2 Features & Testing
