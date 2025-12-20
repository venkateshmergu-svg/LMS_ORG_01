# Definition of Done (DoD) – Phase 26.1

**Status:** Mandatory | **Scope:** Every Frontend Change | **Effective:** Phase 26

---

## Overview

Every frontend change—bug fix, feature update, refactor, or documentation—must satisfy **ALL** items in this Definition of Done before merge approval. No exceptions without documented exemption.

This DoD is organized into **8 mandatory categories**:
1. Code Quality (TypeScript, linting, no console errors)
2. UI States (loading, empty, error, success)
3. Accessibility (WCAG, keyboard, ARIA)
4. Performance (re-renders, caching)
5. Security & RBAC (authorization, data handling)
6. Documentation (code comments, user-facing docs)
7. Testing (test coverage, evidence)
8. Release Readiness (no blockers, rollback plan)

---

## Category 1: Code Quality

### ✅ TypeScript Strict Mode
- [ ] No `any` types (explicit or implicit)
- [ ] All function parameters have type annotations
- [ ] All function return types are explicit
- [ ] All variables have inferred or explicit types
- [ ] `strictNullChecks` and `strictFunctionTypes` enabled in `tsconfig.json`
- [ ] Run `tsc --noEmit` before commit; zero errors

**Verification:**
```bash
npx tsc --noEmit
```

**Example:**
```typescript
// ❌ BAD
function handleUpdate(data) {
  setUser(data);
}

// ✅ GOOD
function handleUpdate(data: IUserUpdate): void {
  setUser(data);
}
```

### ✅ ESLint & Code Quality
- [ ] Zero ESLint errors
- [ ] Zero ESLint warnings (unless explicitly ignored with documented reason)
- [ ] Run `npm run lint` and fix all issues before commit
- [ ] No `eslint-disable` comments without explanation

**Verification:**
```bash
npm run lint
```

### ✅ No Console Errors or Warnings
- [ ] No `console.error()` in production code (use logging service)
- [ ] No `console.warn()` unless intentional debugging
- [ ] Browser dev console shows no red errors or warnings related to the change
- [ ] Check console in Chrome DevTools (F12) in production build

**Verification:**
```bash
npm run build
# Then open in browser and check dev console
```

### ✅ Code Formatting
- [ ] Code formatted with Prettier (auto-format on save enabled)
- [ ] No inconsistent spacing, indentation, or line length
- [ ] Run `npm run format` to ensure consistency

**Verification:**
```bash
npm run format
```

---

## Category 2: UI States

All interactive components must handle and display these states clearly:

### ✅ Loading State
- [ ] Component shows loading indicator (spinner, skeleton, or shimmer)
- [ ] User knows to wait; actions are disabled
- [ ] Loading text/ARIA label indicates what is loading

**Example:**
```typescript
// ✅ GOOD
{isLoading && (
  <div className="flex items-center gap-2" role="status" aria-label="Loading approvals">
    <Spinner />
    <span>Fetching approvals...</span>
  </div>
)}
```

### ✅ Empty State
- [ ] When query returns no data, component shows a helpful message (not blank)
- [ ] Empty state suggests next action (e.g., "No leaves yet. Create a new request.")
- [ ] Empty state is visually distinct from loading or error

**Example:**
```typescript
// ✅ GOOD
{!isLoading && data.length === 0 && (
  <div className="text-center text-gray-500">
    <p>No approvals to review</p>
    <p className="text-sm">Pending approvals will appear here</p>
  </div>
)}
```

### ✅ Error State
- [ ] Errors display a user-friendly message (not raw API error)
- [ ] Error message suggests recovery action (retry, contact support)
- [ ] Error does not crash the component; graceful fallback provided
- [ ] Network errors handled separately from validation errors

**Example:**
```typescript
// ✅ GOOD
{error && (
  <div className="bg-red-50 border border-red-200 rounded p-4" role="alert">
    <p className="font-semibold text-red-800">Unable to load approvals</p>
    <p className="text-red-700 text-sm">Please try again or contact support</p>
    <button onClick={retry} className="mt-2">Retry</button>
  </div>
)}
```

### ✅ Success State
- [ ] When action succeeds, user gets clear confirmation (toast, snackbar, or message)
- [ ] Success message shows what was accomplished
- [ ] UI updates reflect the successful change immediately (optimistic or confirmed)

**Example:**
```typescript
// ✅ GOOD
{successMessage && (
  <div className="bg-green-50 border border-green-200 rounded p-4" role="status">
    <p className="text-green-800">Approval submitted successfully</p>
  </div>
)}
```

---

## Category 3: Accessibility (WCAG 2.1 AA)

### ✅ Keyboard Navigation
- [ ] All interactive elements (buttons, links, inputs) are keyboard accessible
- [ ] Tab order is logical (left-to-right, top-to-bottom)
- [ ] Focus is visible (outline/highlight clearly shows focused element)
- [ ] Focus trap implemented for modals/dialogs (Tab cycles within modal)
- [ ] Escape key closes modals/dialogs
- [ ] Test: Use keyboard only (no mouse) to interact with component

**Verification:**
```bash
# Tab through component; verify logical order and visible focus
# Press Escape in modals; verify closure
```

### ✅ ARIA Labels & Roles
- [ ] All form inputs have associated `<label>` tags
- [ ] Buttons have descriptive text or `aria-label` (not just icons)
- [ ] Icons without text have `aria-label` (e.g., close button)
- [ ] Semantic HTML used: `<button>`, `<nav>`, `<main>`, `<section>`, etc.
- [ ] Custom components have proper `role` attributes if not semantic HTML
- [ ] Images have `alt` text (or `alt=""` if decorative)

**Example:**
```typescript
// ❌ BAD
<button onClick={close}>✕</button>

// ✅ GOOD
<button 
  onClick={close}
  aria-label="Close dialog"
  className="text-gray-500 hover:text-gray-700"
>
  ✕
</button>
```

### ✅ Focus Management
- [ ] Focus is restored after dialog/modal closes
- [ ] Focus moves to new content after async load
- [ ] No focus traps (except intentional modals)
- [ ] `useRef` + `focus()` used to manage focus programmatically when needed

**Example:**
```typescript
// ✅ GOOD
const closeDialog = () => {
  setOpen(false);
  triggerRef.current?.focus(); // Return focus to triggering button
};
```

### ✅ Color Contrast
- [ ] Text has sufficient contrast ratio (WCAG AA: 4.5:1 for normal text)
- [ ] Do NOT rely on color alone to convey information
- [ ] Use text labels + icons together
- [ ] Test: Use WebAIM Contrast Checker or browser extension

**Example:**
```typescript
// ❌ BAD
<span className="text-red">Required</span> {/* Color only */}

// ✅ GOOD
<span className="text-red-600 font-semibold">
  * Required
</span>
```

### ✅ Error Messages for Forms
- [ ] Validation errors are linked to form fields with `aria-describedby`
- [ ] Error message is read aloud when field loses focus
- [ ] Error is visible in color + icon (not color alone)

**Example:**
```typescript
// ✅ GOOD
<input
  id="email-input"
  type="email"
  aria-describedby={error ? "email-error" : undefined}
/>
{error && (
  <span id="email-error" className="text-red-600 text-sm">
    Invalid email address
  </span>
)}
```

### ✅ Screen Reader Testing
- [ ] Tested with NVDA (Windows) or VoiceOver (Mac)
- [ ] Component structure makes sense when read aloud
- [ ] Form fields, buttons, and interactive elements are announced correctly
- [ ] Dynamic content updates are announced (use `aria-live` if needed)

**Verification:**
```bash
# Windows: Download NVDA (free)
# Mac: Enable VoiceOver (Cmd + F5)
# Test: Tab through and listen to announcements
```

---

## Category 4: Performance

### ✅ No Unnecessary Re-renders
- [ ] Component does not re-render on every parent update
- [ ] Use `React.memo()` for pure components
- [ ] Use `useMemo()` for expensive calculations
- [ ] Use `useCallback()` for callback stability
- [ ] Props are stable (not recreated on every render)

**Example:**
```typescript
// ❌ BAD
function Parent() {
  const handleClick = () => { /* ... */ };
  return <Child onClick={handleClick} />; // New function every render
}

// ✅ GOOD
function Parent() {
  const handleClick = useCallback(() => { /* ... */ }, []);
  return <Child onClick={handleClick} />;
}
```

### ✅ Query Cache & Invalidation
- [ ] React Query (or cache library) is configured properly
- [ ] Cache keys are consistent and predictable
- [ ] Stale time is set appropriately (not too aggressive, not too lenient)
- [ ] Cache is invalidated after mutations (POST, PUT, DELETE)
- [ ] No manual cache busting with forced refetch unless necessary

**Example:**
```typescript
// ✅ GOOD
const mutation = useMutation(updateApproval, {
  onSuccess: () => {
    queryClient.invalidateQueries(['approvals']); // Refresh cache
  }
});
```

### ✅ Network Requests Optimized
- [ ] No duplicate requests for same data
- [ ] Pagination or virtual scrolling used for large lists
- [ ] Images are optimized (compressed, correct format)
- [ ] No polling; use websockets or optimistic updates where applicable

### ✅ Bundle Size Checked
- [ ] New dependencies don't bloat bundle unnecessarily
- [ ] Dynamic imports (`React.lazy`) used for large features
- [ ] No duplicate dependencies in `package.json`

**Verification:**
```bash
npm run build
# Check dist/ folder size; ensure no significant increase
```

### ✅ No Console Spam
- [ ] No repeated `console.log()` or `console.warn()` in loops
- [ ] Debugging logs removed before commit
- [ ] Use React DevTools Profiler to check render frequency

---

## Category 5: Security & RBAC

### ✅ Role-Based Access Control (RBAC)
- [ ] `RoleGate` component used to hide/show role-specific UI
- [ ] No business logic tied to frontend roles
- [ ] Backend is the source of truth for authorization
- [ ] Frontend never grants permissions; only reflects backend decisions

**Example:**
```typescript
// ✅ GOOD
{currentUser.role === 'approver' && (
  <button onClick={approveRequest}>Approve</button>
)}
// Backend validates user is actually an approver

// ❌ BAD
// Never do this:
localStorage.setItem('role', 'admin'); // Client-side privilege escalation!
```

### ✅ No Security Logic in Frontend
- [ ] No passwords, tokens, or secrets hardcoded
- [ ] API calls always go through backend (never direct DB access)
- [ ] Sensitive data (SSN, salary, etc.) not logged or stored in frontend
- [ ] HTTPS enforced for all API calls
- [ ] Tokens stored securely (httpOnly cookies preferred, never localStorage for tokens)

### ✅ Input Validation
- [ ] All user input is validated before sending to backend
- [ ] Validation is defensive (check type, length, format)
- [ ] Backend re-validates (frontend validation is UX only)
- [ ] No XSS vulnerabilities (use React's built-in escaping)

**Example:**
```typescript
// ✅ GOOD
if (!email.includes('@') || email.length > 255) {
  setError('Invalid email');
  return;
}
// Backend re-validates before accepting
```

### ✅ Data Handling
- [ ] Sensitive data not logged in console
- [ ] Error messages don't expose internal system details
- [ ] User data is treated as untrusted
- [ ] CORS headers respected; no workarounds

---

## Category 6: Documentation

### ✅ Code Comments
- [ ] Complex logic has explanatory comments
- [ ] WHY is explained, not WHAT (code explains WHAT)
- [ ] Comments updated if code changes
- [ ] No outdated or misleading comments

**Example:**
```typescript
// ❌ BAD
const x = y * 2; // multiply y by 2

// ✅ GOOD
// Double the user's balance to match fiscal year adjustment
const adjustedBalance = userBalance * 2;
```

### ✅ Component Documentation
- [ ] JSDoc comments for exported components/functions
- [ ] Props documented with types and usage
- [ ] Unusual behavior or gotchas documented

**Example:**
```typescript
/**
 * ApprovalCard - Displays a single approval request
 * 
 * @param {IApproval} approval - The approval object
 * @param {() => void} onApprove - Callback when user approves
 * @param {boolean} isLoading - Loading state
 */
export function ApprovalCard({ approval, onApprove, isLoading }: Props) {
  // ...
}
```

### ✅ Updated User-Facing Documentation
- [ ] If new features/pages added, user guide updated
- [ ] If breaking UX changes made, release notes document impact
- [ ] Navigation index reflects new sections (if applicable)
- [ ] Runbook updated if operational procedures change

---

## Category 7: Testing & Verification

### ✅ Manual Testing Checklist
- [ ] Feature tested in Chrome, Firefox, Safari (desktop)
- [ ] Feature tested on mobile (iOS Safari, Chrome Android)
- [ ] All UI states tested (loading, empty, error, success)
- [ ] Happy path tested
- [ ] Error paths tested
- [ ] Edge cases tested (empty input, max input, special characters)

### ✅ Regression Testing
- [ ] No unintended changes to existing pages
- [ ] Navigation still works
- [ ] Previous accessible features still accessible
- [ ] Previous performance not degraded

### ✅ Accessibility Verification
- [ ] Keyboard navigation tested
- [ ] Screen reader tested (NVDA or VoiceOver)
- [ ] Color contrast verified
- [ ] Focus visible and logical

### ✅ Performance Verification
- [ ] Lighthouse score not degraded (target: >90)
- [ ] Bundle size increase documented and justified
- [ ] No major re-render regressions (React DevTools Profiler)

**Verification:**
```bash
# Run Lighthouse audit
npm run build
# Open dist/index.html in browser
# Lighthouse (Chrome DevTools) → Generate report
```

### ✅ Test Evidence in PR
- [ ] Screenshot of success state
- [ ] Screenshot of error state (if applicable)
- [ ] Accessibility test results (screenshot of screen reader or NVDA output)
- [ ] Performance comparison (before/after Lighthouse score)
- [ ] List of devices/browsers tested

---

## Category 8: Release Readiness

### ✅ No Merge Blockers
- [ ] All CI/CD checks passing (TypeScript, ESLint, tests)
- [ ] No failing tests
- [ ] No security vulnerabilities reported
- [ ] No console errors or warnings
- [ ] PR review approved by at least one reviewer

### ✅ Rollback Plan
- [ ] Change is reversible (no data migrations that can't be undone)
- [ ] If rollback needed, clear procedure exists
- [ ] Deployment can be rolled back in <15 minutes
- [ ] No dependencies on undeployed backend changes (check release timeline)

### ✅ Communication Plan
- [ ] If breaking UX change, users notified in advance
- [ ] Release notes document what changed and why
- [ ] Known limitations or workarounds documented
- [ ] Escalation contact provided for urgent issues

### ✅ PR Description Complete
- [ ] What changed (feature, bug fix, refactor)
- [ ] Why it changed (business reason, issue link)
- [ ] How it was tested (manual test steps, test evidence)
- [ ] Any breaking changes or migration steps
- [ ] Links to related issues or documentation

**PR Template Example:**
```markdown
## What
Fixed loading state in ApprovalsList component.

## Why
Users were confused when page loaded; no indicator showed data was fetching.
Closes #1234

## How Tested
- Manual test on Chrome, Firefox, Safari
- Screen reader tested with NVDA
- Lighthouse score 96 (no regression)

## Screenshots
[Loading state]
[Success state]

## Breaking Changes
None

## Rollback Plan
Safe to revert; no data changes
```

---

## DoD Checklist Template

Use this checklist for every PR:

```
## Definition of Done Checklist

### Code Quality
- [ ] TypeScript strict mode passes (`tsc --noEmit`)
- [ ] ESLint passes (`npm run lint`)
- [ ] No console errors or warnings
- [ ] Code formatted with Prettier

### UI States
- [ ] Loading state implemented and visible
- [ ] Empty state handled and helpful
- [ ] Error state user-friendly with recovery action
- [ ] Success state confirmed

### Accessibility
- [ ] Keyboard navigation works (Tab, Shift+Tab, Enter, Escape)
- [ ] All interactive elements have ARIA labels or semantic HTML
- [ ] Focus management correct (dialog focus trap, restoration after close)
- [ ] Color contrast verified (4.5:1 minimum)
- [ ] Screen reader tested (NVDA or VoiceOver)

### Performance
- [ ] No unnecessary re-renders (React.memo, useCallback, useMemo)
- [ ] Cache invalidation correct (React Query)
- [ ] Bundle size impact acceptable
- [ ] Lighthouse score maintained (target: >90)

### Security & RBAC
- [ ] RoleGate used for visibility control
- [ ] No business logic in frontend
- [ ] No sensitive data exposed
- [ ] Input validated (frontend + backend)

### Documentation
- [ ] Code comments explain WHY (not WHAT)
- [ ] Components documented (JSDoc)
- [ ] User-facing docs updated (if applicable)

### Testing
- [ ] Tested on desktop (Chrome, Firefox, Safari)
- [ ] Tested on mobile (iOS Safari, Chrome Android)
- [ ] All UI states verified
- [ ] Accessibility verified
- [ ] Performance verified
- [ ] Test evidence in PR (screenshots, Lighthouse)

### Release Readiness
- [ ] All CI/CD checks passing
- [ ] No merge blockers
- [ ] Rollback plan documented
- [ ] PR description complete
- [ ] No breaking changes without communication plan

**Approved By:** [Reviewer Name]
**Approval Date:** [Date]
```

---

## When to Request Exemptions

Exemptions are **rare** and require:
1. Written justification (why DoD item is inappropriate)
2. Tech lead approval
3. Documented ADR (Architecture Decision Record)
4. Logged as tech debt (if not addressed)

**Example Exemptions:**
- ❌ "We're in a hurry" → Not a valid reason
- ✅ "This is a breaking security fix; rolling back is dangerous. Accessibility review deferred to next sprint with ADR." → Valid with documentation
- ❌ "We'll fix the console error later" → Not acceptable; fix it now
- ✅ "Third-party library throws console warning we cannot control. Documented with library version and tracking issue." → Valid with workaround

---

## Enforcement

| Check | Tool | Gate |
|-------|------|------|
| TypeScript | `tsc --noEmit` | CI/CD (auto) |
| ESLint | `npm run lint` | CI/CD (auto) |
| Accessibility | Manual + NVDA/VO | Manual review |
| Performance | Lighthouse | Manual review |
| UI States | Manual test | Manual review |
| Security/RBAC | Code review | Manual review |
| Documentation | Code review | Manual review |

---

**Definition of Done Version:** 1.0 | **Status:** Active | **Last Updated:** December 2025
