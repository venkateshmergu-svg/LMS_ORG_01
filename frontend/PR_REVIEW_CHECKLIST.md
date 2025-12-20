# PR Review Checklist – Phase 26.3

**Status:** Mandatory | **Scope:** All Pull Requests | **Effective:** Phase 26

---

## Overview

This checklist is used by PR reviewers to verify that every change meets the Definition of Done before approval. Reviewers must explicitly validate **all** items before marking PR as approved.

**Note:** Do not approve unless ALL checkboxes are satisfied. If items cannot be verified, request evidence from the author.

---

## PR Review Checklist Template

```markdown
## PR Review – Definition of Done Verification

**PR Title:** [Title]
**Author:** [Author Name]
**Linked Issue:** #[Issue Number]

---

### ✅ Code Quality
- [ ] TypeScript strict mode passes (`tsc --noEmit`)
- [ ] ESLint passes (`npm run lint`)
- [ ] No `any` types (all types explicit)
- [ ] No console errors or warnings
- [ ] Code formatted (Prettier)
- [ ] Naming conventions followed (PascalCase components, camelCase utilities)

**Evidence:** 
- [ ] Author has run `npm run lint` and `npm run build` locally

---

### ✅ Functionality
- [ ] Feature works as described in PR description
- [ ] No unintended side effects on other features
- [ ] All UI states implemented:
  - [ ] Loading state visible
  - [ ] Empty state handled
  - [ ] Error state user-friendly
  - [ ] Success state confirmed
- [ ] Happy path tested
- [ ] Error paths tested

**Evidence:**
- [ ] Author has provided screenshots or video demo
- [ ] Test steps documented in PR description

---

### ✅ Accessibility (WCAG 2.1 AA)
- [ ] Keyboard navigation works (Tab, Shift+Tab, Enter, Escape)
- [ ] All interactive elements keyboard accessible
- [ ] Focus visible and logical
- [ ] ARIA labels present for new interactive elements
- [ ] No keyboard traps (except intentional modals)
- [ ] Form errors linked with `aria-describedby`
- [ ] Screen reader tested (NVDA or VoiceOver)
- [ ] Color contrast verified (4.5:1 minimum)
- [ ] No reliance on color alone to convey information

**Evidence:**
- [ ] Author has tested with keyboard only
- [ ] Author has tested with screen reader (NVDA/VoiceOver)
- [ ] Screenshot or video of accessibility testing provided

---

### ✅ Performance
- [ ] No unnecessary re-renders (React.memo, useCallback, useMemo appropriate)
- [ ] Query cache & invalidation correct (React Query)
- [ ] Bundle size impact acceptable (<50KB for typical feature)
- [ ] Lighthouse score maintained (>90)
- [ ] No performance degradation vs baseline
- [ ] Load time not increased

**Evidence:**
- [ ] Author has run Lighthouse audit
- [ ] Before/after Lighthouse scores in PR description
- [ ] React DevTools Profiler analysis (if re-renders suspected)

---

### ✅ API Contract Adherence
- [ ] Uses existing API endpoints (no new backend assumptions)
- [ ] Handles API response shape correctly
- [ ] API error handling correct (4xx, 5xx, timeout)
- [ ] No speculative frontend changes for backend work
- [ ] Pagination/filtering implemented correctly
- [ ] Request/response types match backend contract

**Evidence:**
- [ ] Author has verified against backend API docs
- [ ] API contract review comment in PR

---

### ✅ Error Handling
- [ ] Network errors handled (timeout, 500, offline)
- [ ] Validation errors shown to user
- [ ] Error messages user-friendly (not raw API errors)
- [ ] Error suggests recovery action (retry, contact support)
- [ ] Error doesn't crash component
- [ ] Error state is visually distinct

**Evidence:**
- [ ] Screenshot of error state
- [ ] Error handling code review

---

### ✅ Security & RBAC
- [ ] `RoleGate` used for role-based visibility
- [ ] No business logic in frontend
- [ ] No hardcoded secrets or tokens
- [ ] No sensitive data exposed in logs/console
- [ ] HTTPS enforced
- [ ] Input validated (frontend + backend)
- [ ] No XSS vulnerabilities
- [ ] Backend remains source of truth for authorization

**Evidence:**
- [ ] Security review checklist item completed
- [ ] Code review for sensitive data handling

---

### ✅ UX Consistency
- [ ] Follows design system (buttons, spacing, colors)
- [ ] Consistent with existing pages/components
- [ ] No new fonts, colors, or spacing patterns
- [ ] Button text matches conventions (Submit, Cancel, etc.)
- [ ] Error/success messages follow existing patterns
- [ ] Loading indicators consistent with app style
- [ ] Responsive design consistent (mobile, tablet, desktop)

**Evidence:**
- [ ] Screenshots on mobile and desktop
- [ ] Designer review (if design changes)

---

### ✅ Documentation
- [ ] Code comments explain WHY (not WHAT)
- [ ] Components have JSDoc comments
- [ ] Complex logic documented
- [ ] User-facing docs updated (if applicable)
- [ ] README/component guide updated (if needed)
- [ ] No misleading or outdated comments

**Evidence:**
- [ ] Documentation files updated
- [ ] Code comments reviewed

---

### ✅ Testing & Evidence
- [ ] Tested on Chrome, Firefox, Safari (desktop)
- [ ] Tested on iOS Safari and Chrome Android (mobile)
- [ ] All UI states verified
- [ ] Accessibility verified
- [ ] Performance verified
- [ ] No regressions in existing features

**Evidence:**
- [ ] Screenshot of success state
- [ ] Screenshot of error state (if applicable)
- [ ] Mobile screenshot
- [ ] Accessibility test evidence (NVDA/VoiceOver)
- [ ] Lighthouse report (or audit result)

---

### ✅ Release Readiness
- [ ] All CI/CD checks passing (TypeScript, ESLint, tests)
- [ ] No merge conflicts
- [ ] No breaking changes without communication plan
- [ ] Rollback plan documented (if needed)
- [ ] No dependencies on undeployed backend changes
- [ ] Change is reversible

**Evidence:**
- [ ] CI/CD status green
- [ ] Rollback procedure documented (in PR or release notes)

---

### ✅ PR Description Complete
- [ ] What changed (clear, concise)
- [ ] Why it changed (linked to issue/business reason)
- [ ] How it was tested (reproducible test steps)
- [ ] Screenshots or video demo
- [ ] Known limitations or workarounds documented
- [ ] Breaking changes (if any) documented

**Evidence:**
- [ ] PR description is thorough and clear
- [ ] Issue link present

---

### 🔴 Blocking Issues (If Any)
- [ ] Issue: [Describe]
  - [ ] Status: Awaiting author fix
  - [ ] Resolution: [Author's plan]

---

## Reviewer Sign-Off

**Reviewed By:** [Reviewer Name]  
**Review Date:** [Date]  
**Status:** ✅ APPROVED / ❌ REQUEST CHANGES

**Approval Notes:**
[Any additional notes or observations]

---

## Special Cases

### Breaking Changes
If PR includes breaking changes (UX, API contract, accessibility):
- [ ] Tech lead approval required
- [ ] ADR (Architecture Decision Record) filed
- [ ] Release notes document impact
- [ ] User communication plan exists
- [ ] Rollback procedure clear

### Performance Regression
If Lighthouse score drops >5% or bundle size increases >50KB:
- [ ] Performance review completed
- [ ] Mitigation plan documented
- [ ] Performance engineer approval required
- [ ] Rollback plan exists

### Accessibility Issues
If any WCAG violations found:
- [ ] ❌ BLOCK merge
- [ ] Author must fix or file accessibility debt ADR
- [ ] A11y champion review required

### API Contract Changes
If consuming new backend endpoints or contract changes:
- [ ] Backend API documentation reviewed
- [ ] Version compatibility verified
- [ ] Backend tech lead approval required
- [ ] Backward compatibility considered

---

## Review Workflow

### 1. Author Submits PR
- [ ] Completes PR description with all sections
- [ ] Adds test evidence (screenshots, Lighthouse, etc.)
- [ ] Marks PR as "Ready for Review"

### 2. Reviewer Checks Automated Gates
- [ ] CI/CD status is green
- [ ] TypeScript strict mode passes
- [ ] ESLint passes
- [ ] Tests pass (if any)

### 3. Reviewer Conducts Manual Review
- [ ] Reads PR description thoroughly
- [ ] Reviews code changes
- [ ] Checks test evidence
- [ ] Asks questions if unclear

### 4. Reviewer Uses This Checklist
- [ ] Goes through each category
- [ ] Verifies evidence provided
- [ ] Requests additional evidence if needed
- [ ] Documents findings in PR comments

### 5. Author Responds to Feedback
- [ ] Fixes issues raised
- [ ] Pushes new commits
- [ ] Notifies reviewer when ready for re-review

### 6. Reviewer Approves or Requests Changes
- [ ] ✅ APPROVE: All items checked, evidence complete
- [ ] ❌ REQUEST CHANGES: List blocking issues, author fixes

### 7. Merge & Deploy
- [ ] Once approved, author merges PR
- [ ] Change deployed according to release schedule
- [ ] Deployment logged for audit trail

---

## Quick Reference: What Blocks Merge

| Issue | Severity | Merge Blocker |
|-------|----------|---------------|
| TypeScript error | Critical | ✅ YES |
| ESLint error | Critical | ✅ YES |
| Console error | Critical | ✅ YES |
| Accessibility violation (WCAG) | Critical | ✅ YES |
| Security issue | Critical | ✅ YES |
| No test evidence | High | ✅ YES |
| Performance regression >5% | High | ✅ YES |
| Missing error handling | Medium | ✅ YES |
| Code style issue | Low | ❌ NO (auto-fix) |
| Minor documentation gap | Low | ❌ NO (can add follow-up PR) |

---

## Tips for Effective Reviews

### ✅ DO
- Ask questions if unclear
- Request evidence; don't assume
- Be specific about issues (line numbers, code examples)
- Acknowledge good practices
- Approve quickly if everything checks out
- Provide constructive feedback

### ❌ DON'T
- Approve without verification
- Request changes for style preferences (use linter)
- Hold up PR for future improvements (file separate issue)
- Assume accessibility is fine without testing
- Skip performance check
- Merge code you don't understand

---

## Escalation Path

If reviewer and author disagree:

1. **First Level:** Reviewer documents concern in PR; author responds
2. **Second Level:** Tech lead reviews and mediates
3. **Third Level:** Team consensus or tech lead makes final call
4. **Documentation:** Decision logged in PR or ADR

---

## Performance Review Details

For performance-impacting changes, provide:

1. **Lighthouse Score** (before & after)
   ```
   Before: Desktop 94, Mobile 87
   After: Desktop 91, Mobile 84
   ```

2. **Bundle Size** (before & after)
   ```
   Before: main.js 245KB
   After: main.js 248KB (+3KB = 1.2% increase)
   ```

3. **Render Performance**
   - React DevTools Profiler: Screen capture of render time
   - Identify any components re-rendering excessively

4. **Network Performance**
   - No new unnecessary API calls
   - Cache strategy reviewed

---

## Security Review Details

For security-sensitive changes, verify:

1. **Authentication & Authorization**
   - Is token handling secure (httpOnly cookies)?
   - Does `RoleGate` properly reflect backend permissions?
   - No client-side privilege escalation?

2. **Data Protection**
   - No sensitive data in localStorage?
   - No passwords in logs or console?
   - User data encrypted in transit (HTTPS)?

3. **Input Validation**
   - Frontend validation is UX only
   - Backend re-validates all input?
   - No XSS vectors?

4. **API Safety**
   - Calls authenticated API endpoints?
   - Respects CORS?
   - Error messages safe (no system details)?

---

**PR Review Checklist Version:** 1.0 | **Status:** Active | **Last Updated:** December 2025
