# API Contract Governance – Phase 26.4

**Status:** Mandatory | **Scope:** All Backend API Changes | **Effective:** Phase 26

---

## Overview

This document defines how the frontend consumes backend API changes while maintaining stability, backward compatibility, and audit-ready documentation. The backend remains the authoritative source of all business logic and data validation.

**Key Principle:** Frontend is a client of the backend API. Frontend never leads or assumes backend changes.

---

## Table of Contents
1. [API Contract Principles](#api-contract-principles)
2. [Consuming Backend Changes](#consuming-backend-changes)
3. [Frontend Versioning & Compatibility](#frontend-versioning--compatibility)
4. [Breaking Changes: Process & Rollout](#breaking-changes-process--rollout)
5. [Deprecation Strategy](#deprecation-strategy)
6. [API Response Handling](#api-response-handling)
7. [Contract Governance Checklist](#contract-governance-checklist)
8. [Escalation & Disputes](#escalation--disputes)

---

## API Contract Principles

### Principle 1: Backend is Source of Truth
- **All business logic** lives in the backend
- **All authorization decisions** made by backend (not frontend)
- **All data validation** occurs in backend (frontend validation is UX only)
- **All security rules** enforced by backend

**Frontend Implication:**
```typescript
// ✅ GOOD: Frontend assumes backend is authoritative
const { data: user } = useUserQuery();
// Backend has already verified this user's role, permissions, data access

// ❌ BAD: Frontend attempting to enforce business logic
if (user.role === 'admin') {
  user.salary = 100000; // Never do this; backend decides salary visibility
}
```

### Principle 2: Frontend Follows Backend Contract
- Frontend consumes published API contracts (documented endpoints)
- Frontend never assumes undocumented behavior
- Frontend adapts to backend changes; backend never adapts to frontend
- Breaking changes require coordination and planned rollout

### Principle 3: No Speculative Frontend Changes
- Frontend does NOT implement features before backend API is ready
- Frontend does NOT change UI anticipating backend work
- Frontend waits for backend API to be stable before consuming

**Example:**
```typescript
// ❌ BAD: Building UI for backend work that hasn't shipped
const { data: auditLog } = useQuery(['audit-new-format'], () =>
  // This endpoint doesn't exist yet; backend is "working on it"
  apiClient.get('/api/audit/v2/entries')
);

// ✅ GOOD: Only build UI for documented, stable APIs
const { data: auditLog } = useQuery(['audit'], () =>
  // This endpoint is documented and tested
  apiClient.get('/api/audit/entries')
);
```

### Principle 4: Contract Stability Over Speed
- Prefer stable API contracts over rapid iteration
- Changes to API contracts are breaking changes (treat accordingly)
- Backward compatibility is the default expectation

---

## Consuming Backend Changes

### Step 1: Review API Contract Documentation
Before frontend starts consuming a new or changed API:

1. **Read Backend API Documentation**
   - Endpoint path and HTTP method
   - Required parameters and types
   - Request body schema (if POST/PUT)
   - Response schema and HTTP status codes
   - Error responses and error codes
   - Rate limiting and pagination rules
   - Authentication requirements

2. **Verify API is Stable**
   - Is this endpoint documented and released?
   - Has it been tested by QA?
   - Has the backend team approved it for frontend consumption?
   - Is a contract version specified?

3. **Understand Backward Compatibility**
   - What changes are backward compatible?
   - What changes require coordination?
   - How long will old versions be supported?

**Verification Checklist:**
```typescript
// Before writing code, verify:
// ✅ Endpoint documented in API docs
// ✅ Backend team confirmed endpoint is ready
// ✅ Response schema clear and tested
// ✅ Error handling strategy documented
// ✅ Pagination approach (if list endpoint)
// ✅ Authentication requirements clear
```

### Step 2: Create Type Definitions
Generate or manually create TypeScript types matching the API contract:

```typescript
// ✅ GOOD: Types match backend contract exactly
// File: src/api/types/approval.types.ts

export interface IApprovalRequest {
  id: string;
  userId: string;
  leaveId: string;
  status: 'pending' | 'approved' | 'rejected';
  approvedAt?: string; // ISO 8601 date string
  approvedBy?: string; // User ID
  comment?: string;
}

export interface IApprovalListResponse {
  data: IApprovalRequest[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    hasMore: boolean;
  };
}

// Error response
export interface IApiError {
  code: string; // e.g., 'UNAUTHORIZED', 'NOT_FOUND'
  message: string;
  details?: Record<string, any>;
}
```

### Step 3: Implement API Client Method
Create a reusable API client method:

```typescript
// File: src/api/endpoints/approvals.api.ts

export const approvalsApi = {
  /**
   * Get all approvals for a user
   * 
   * @param userId - User ID
   * @param page - Page number (1-indexed)
   * @param pageSize - Results per page
   * @returns List of approval requests
   */
  getApprovals: async (
    userId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<IApprovalListResponse> => {
    const response = await apiClient.get('/api/v1/approvals', {
      params: { userId, page, pageSize },
    });
    return response.data;
  },

  /**
   * Submit an approval decision
   * 
   * @param approvalId - Approval request ID
   * @param decision - 'approve' or 'reject'
   * @param comment - Optional comment
   * @returns Updated approval request
   */
  submitApproval: async (
    approvalId: string,
    decision: 'approve' | 'reject',
    comment?: string
  ): Promise<IApprovalRequest> => {
    const response = await apiClient.post(
      `/api/v1/approvals/${approvalId}`,
      { decision, comment }
    );
    return response.data;
  },
};
```

### Step 4: Implement React Query Hook
Wrap the API client in a React Query hook:

```typescript
// File: src/hooks/useApprovalQuery.ts

export const useApprovalQuery = (userId: string) => {
  return useQuery(
    ['approvals', userId],
    () => approvalsApi.getApprovals(userId),
    {
      enabled: !!userId,
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      onError: (error) => {
        console.error('Failed to fetch approvals:', error);
      },
    }
  );
};

export const useSubmitApprovalMutation = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ approvalId, decision, comment }: {
      approvalId: string;
      decision: 'approve' | 'reject';
      comment?: string;
    }) => approvalsApi.submitApproval(approvalId, decision, comment),
    {
      onSuccess: () => {
        // Invalidate cache so list refreshes
        queryClient.invalidateQueries(['approvals']);
      },
      onError: (error) => {
        console.error('Failed to submit approval:', error);
      },
    }
  );
};
```

### Step 5: Test Against Real Backend
Before merging, test against actual backend:

1. **Happy Path Test**
   ```bash
   # Test successful API call
   npm run dev
   # Manually test in browser; verify data loads
   ```

2. **Error Path Test**
   ```bash
   # Disable network in DevTools
   # Verify error handling works (user sees error message)
   # Re-enable network and test recovery
   ```

3. **Edge Cases**
   - Empty results
   - Single result
   - Large result set
   - Timeout/slow network

---

## Frontend Versioning & Compatibility

### API Versioning Strategy

The backend API uses versioning: `/api/v1/`, `/api/v2/`, etc.

Frontend must understand:
- **Version Deprecation Timeline:** When old versions stop being supported
- **Feature Flags:** How new features roll out (on backend)
- **Backward Compatibility Window:** How long two versions coexist

### Frontend Contract Version Management

Track which backend API versions your frontend supports:

```typescript
// File: src/api/client.config.ts

export const API_VERSIONS = {
  APPROVALS: 'v1',           // Uses /api/v1/approvals
  LEAVE: 'v1',               // Uses /api/v1/leave
  AUDIT: 'v2',               // Uses /api/v2/audit (upgraded from v1)
} as const;

// Supported backend API versions
export const SUPPORTED_API_VERSIONS = {
  v1: { 
    supported: true, 
    deprecatedOn: '2025-12-31',
    removedOn: '2026-06-30' 
  },
  v2: { 
    supported: true, 
    deprecatedOn: null,
    removedOn: null 
  },
} as const;
```

### Tracking Backward Compatibility

Document in your codebase which backend versions you support:

```typescript
// File: src/api/endpoints/approvals.api.ts

/**
 * Approvals API Client
 * 
 * Supported Backend Versions:
 * - v1: Current (used until 2026-06-30)
 * - v2: Not yet available
 * 
 * Known Incompatibilities:
 * - None
 */
export const approvalsApi = {
  getApprovals: async (userId: string) => {
    // Implementation for v1
  },
};
```

---

## Breaking Changes: Process & Rollout

### Definition: Breaking Change
A backend API change is **breaking** if it:
- Changes response schema (removes fields, changes types)
- Changes HTTP status codes
- Changes error response format
- Removes or relocates endpoints
- Changes parameter requirements
- Changes pagination behavior

### Detecting Breaking Changes

Backend communicates breaking changes to frontend team:

1. **Backend Announces Change** (2+ weeks before)
   - Email to frontend tech lead
   - PR linked for review
   - New API version (e.g., v2)
   - Migration timeline documented

2. **Frontend Reviews Impact**
   - Which components consume this API?
   - What changes needed in frontend?
   - How long to implement?

3. **Frontend Coordinates Implementation**
   - Front and back align on release timeline
   - Frontend uses feature flags if needed
   - Parallel support of old/new API during transition

### Example: Breaking Change in Approvals API

**Scenario:** Backend changes `/api/v1/approvals` response format

**Before (v1):**
```json
{
  "id": "123",
  "userId": "456",
  "status": "pending",
  "createdAt": "2025-01-01T00:00:00Z"
}
```

**After (v2):**
```json
{
  "id": "123",
  "requesterId": "456",  // Field renamed from userId
  "status": "pending_review",  // Value changed
  "createdAt": "2025-01-01T00:00:00Z"
}
```

**Frontend Rollout Plan:**

```typescript
// Step 1: Create adapter for v1 response
// File: src/api/adapters/approvalAdapter.ts

export const adaptApprovalV1toV2 = (v1Approval: IApprovalV1): IApprovalV2 => {
  return {
    id: v1Approval.id,
    requesterId: v1Approval.userId,  // Map old to new
    status: mapStatusV1toV2(v1Approval.status),
    createdAt: v1Approval.createdAt,
  };
};

// Step 2: Update API client to use adapter
export const approvalsApi = {
  getApprovals: async (userId: string) => {
    // Temporarily call v1 endpoint
    const response = await apiClient.get('/api/v1/approvals', {
      params: { userId },
    });
    
    // Adapt response to new format
    return response.data.map(adaptApprovalV1toV2);
  },
};

// Step 3: Roll out in phases
// Phase 1: Adapter in place (v1 endpoint still works)
// Phase 2: Switch to v2 endpoint when backend ready
// Phase 3: Remove adapter after v1 deprecated

// Step 4: When switching to v2 endpoint
export const approvalsApi = {
  getApprovals: async (userId: string) => {
    // Now calling v2 endpoint (no adapter needed)
    const response = await apiClient.get('/api/v2/approvals', {
      params: { userId },
    });
    return response.data;
  },
};
```

### Release Timeline for Breaking Changes

| Timeline | Action |
|----------|--------|
| T-2 weeks | Backend announces breaking change to frontend team |
| T-1 week | Frontend reviews impact; alignment meeting if needed |
| T day | Backend deploys new version alongside old version |
| T+1 day | Frontend switches to new endpoint (tests with new API) |
| T+2 weeks | Verify no issues in production |
| T+1 month | Frontend can remove old API adapter code |
| T+2 months | Backend can deprecate old API version |

---

## Deprecation Strategy

### Deprecation Lifecycle

**Stage 1: Announcement (8 weeks before removal)**
- Backend announces deprecation in documentation
- Frontend is notified of timeline
- No changes required yet; frontend continues using old API

**Stage 2: Parallel Versions (6 weeks before removal)**
- New API version available alongside old version
- Frontend can optionally migrate (not required)
- Both APIs fully supported

**Stage 3: Soft Deprecation (2 weeks before removal)**
- Old API version still works but is slow (lower cache, higher latency)
- Frontend migration encouraged
- Final migration window

**Stage 4: Hard Deprecation (removal)**
- Old API version removed
- Frontend must use new version
- Requests to old endpoint return 410 (Gone)

### Frontend Response to Deprecation

**Timeline for Frontend:**
```
Week 1-4: Review deprecation notice
          Plan migration
          Create types for new API

Week 5-8: Implement new API integration
         Test against new endpoint
         Create PR with migration

Week 9-10: Deploy migration to production
          Monitor for issues
          Keep old code as fallback

Week 11-12: Remove old code
           Clean up adapters/fallbacks
           Deploy cleanup to production
```

---

## API Response Handling

### Standard Response Pattern

All API responses follow this pattern:

```typescript
// Success response (2xx)
{
  "data": { /* Actual data */ },
  "meta": {
    "timestamp": "2025-01-01T00:00:00Z",
    "version": "v1"
  }
}

// Error response (4xx, 5xx)
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "User not found",
    "details": { "userId": "123" }
  }
}
```

### Frontend Error Handling

Always handle all error scenarios:

```typescript
// ✅ GOOD: Comprehensive error handling
export const useApprovalQuery = (userId: string) => {
  return useQuery(
    ['approvals', userId],
    () => approvalsApi.getApprovals(userId),
    {
      onError: (error: AxiosError<IApiError>) => {
        // Network error
        if (!error.response) {
          console.error('Network error or timeout');
          return;
        }

        // HTTP error with response
        const { status, data } = error.response;
        
        switch (status) {
          case 400:
            console.error('Bad request:', data.error.message);
            break;
          case 401:
            console.error('Unauthorized; redirect to login');
            // Trigger login redirect
            break;
          case 403:
            console.error('Forbidden; user lacks permission');
            break;
          case 404:
            console.error('Not found');
            break;
          case 500:
            console.error('Server error; retry');
            break;
          default:
            console.error('Unexpected error:', data.error.message);
        }
      },
    }
  );
};
```

### Status Code Handling

| Status | Meaning | Frontend Action |
|--------|---------|-----------------|
| 200 | OK | Display data |
| 201 | Created | Show success message |
| 400 | Bad Request | Show validation error to user |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show "Access Denied" message |
| 404 | Not Found | Show "Not Found" message |
| 409 | Conflict | Show "Try again; data has changed" |
| 500 | Server Error | Show "Server error; try again later" |
| 503 | Unavailable | Show "Service is down; retry later" |

---

## Contract Governance Checklist

Use this checklist when consuming a new or changed API:

### Before Implementation
- [ ] Backend API endpoint is documented
- [ ] Backend team confirmed endpoint is stable and ready
- [ ] Response schema reviewed and understood
- [ ] Error handling strategy documented
- [ ] Pagination approach (if applicable) verified
- [ ] Authentication requirements clear
- [ ] Rate limiting rules understood
- [ ] Backward compatibility plan (if breaking change) created

### During Implementation
- [ ] TypeScript types created matching API contract exactly
- [ ] API client method created (reusable)
- [ ] React Query hook created
- [ ] Error handling comprehensive (all status codes handled)
- [ ] Happy path tested manually
- [ ] Error paths tested manually
- [ ] Empty data tested
- [ ] Pagination tested (if applicable)

### After Implementation
- [ ] Code reviewed for compliance with API contract
- [ ] Tested against real backend (not mocks)
- [ ] Performance verified (no unnecessary re-requests)
- [ ] Cache strategy appropriate (staleTime, gcTime)
- [ ] Documentation updated (API client docs, types)
- [ ] No TypeScript errors or `any` types
- [ ] No console errors

### PR Description Includes
- [ ] Which API endpoint(s) consumed
- [ ] Link to API documentation
- [ ] What data is displayed and how
- [ ] Error handling summary
- [ ] Test results (happy + error paths)
- [ ] Known limitations (if any)

---

## Escalation & Disputes

### Scenario: Frontend and Backend Disagree on API Contract

**Example:** Backend says "status can be null" but frontend expects "status is always a string"

**Resolution Process:**

1. **Document the Issue**
   - File GitHub issue with details
   - Reference API documentation (backend docs)
   - Show example response data
   - Explain frontend expectation

2. **Resolve (Pick One)**
   - **Backend fixes:** API is wrong; backend corrects response
   - **Frontend adapts:** Frontend handles null status
   - **Agreement:** Both agree on contract; document decision in ADR

3. **Update Documentation**
   - API docs clarified
   - Types updated
   - Frontend code updated
   - Test case added to prevent regression

4. **Record Decision**
   - ADR filed (Architecture Decision Record)
   - Linked in PR and code

---

## Quick Reference: Red Flags

### 🚩 Red Flags - Do NOT Implement
- Backend says "we'll add the API next sprint" → Wait for API
- "We think the response will have X field" → Require documented API
- "Let's assume status codes are 200 for everything" → Require real status codes
- "We don't have documentation; just copy this curl command" → Require official API docs
- Backend says "we might change the schema soon" → Wait for stability
- API responses vary between environments → Require consistency

---

**API Contract Governance Version:** 1.0 | **Status:** Active | **Last Updated:** December 2025
