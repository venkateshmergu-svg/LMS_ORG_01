# Frontend Governance at a Glance

**Quick reference for developers, reviewers, and release engineers**

---

## The 5 Layers of Frontend Governance

```
LAYER 5: Release & Change Management ────────────────────────────────────────
         When to merge? How to deploy? How to rollback? Who to communicate?
         📄 [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md)

LAYER 4: API Contract Governance ────────────────────────────────────────────
         How to consume backend APIs? Handle breaking changes? Versioning?
         📄 [API_CONTRACT_GOVERNANCE.md](API_CONTRACT_GOVERNANCE.md)

LAYER 3: PR Review Checklist ────────────────────────────────────────────────
         🚪 GATE: What does reviewer check before approval?
         10 mandatory categories, blocking criteria, escalation path
         📄 [PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md)

LAYER 2: Coding Standards & Conventions ──────────────────────────────────────
         Naming, structure, patterns, anti-patterns, examples
         📄 [CODING_STANDARDS.md](CODING_STANDARDS.md)

LAYER 1: Definition of Done ──────────────────────────────────────────────────
         🚪 GATE: What must EVERY change satisfy?
         8 categories, 50+ items, enforced by CI/CD + review
         📄 [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)

         ┌─────────────────────────────────────────────────────────┐
         │ 📋 Code Quality: TypeScript strict, ESLint, no console   │
         │ 📊 UI States: Loading, empty, error, success            │
         │ ♿ Accessibility: WCAG AA, keyboard, ARIA, focus       │
         │ ⚡ Performance: Re-renders, caching, bundle size       │
         │ 🔒 Security: RoleGate, no frontend business logic      │
         │ 📚 Documentation: Comments, JSDoc, user docs           │
         │ 🧪 Testing: Manual + automated evidence                │
         │ 🚀 Release Ready: No blockers, rollback plan           │
         └─────────────────────────────────────────────────────────┘

```

---

## Before You Start Coding

**Read These:**
1. [CODING_STANDARDS.md](CODING_STANDARDS.md) – How to name things, structure components, use hooks
2. [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md#category-1-code-quality) – Code quality requirements

**Set Up:**
- Enable Prettier auto-format on save
- Enable ESLint in your editor
- TypeScript strict mode enabled in `tsconfig.json`

---

## Before You Submit a PR

**Self-Check (Use This Checklist):**

### Code Quality ✅
- [ ] `npm run lint` → Zero errors
- [ ] `npm run build` → Zero TypeScript errors
- [ ] Console clean in DevTools (no errors/warnings)
- [ ] No `any` types
- [ ] Code formatted (Prettier)

### UI States ✅
- [ ] Loading state visible (spinner or skeleton)
- [ ] Empty state helpful (message + action)
- [ ] Error state user-friendly (message + recovery option)
- [ ] Success state clear (confirmation shown)

### Accessibility ✅
- [ ] Keyboard navigation works (Tab through page)
- [ ] Focus visible and logical
- [ ] Form inputs have labels
- [ ] Buttons have descriptive text or aria-label
- [ ] No keyboard traps (except modals)
- [ ] Screen reader tested (NVDA or VoiceOver)
- [ ] Color contrast verified (4.5:1)

### Performance ✅
- [ ] No unnecessary re-renders (React.memo, useCallback, useMemo as needed)
- [ ] Cache invalidation correct (React Query)
- [ ] `npm run build` produces reasonable bundle size
- [ ] Lighthouse score >90 (run in DevTools)

### Security & RBAC ✅
- [ ] RoleGate used for visibility control
- [ ] No business logic in frontend
- [ ] No sensitive data exposed
- [ ] Input validated

### Documentation ✅
- [ ] Complex code has explanatory comments (WHY, not WHAT)
- [ ] Components have JSDoc
- [ ] Unusual behavior documented
- [ ] User-facing docs updated (if applicable)

### Testing ✅
- [ ] Tested on desktop (Chrome, Firefox, Safari)
- [ ] Tested on mobile (iOS Safari, Chrome Android)
- [ ] All UI states verified
- [ ] Error paths tested (disconnect network, simulate 500 error)
- [ ] Screenshots/video captured

### PR Description ✅
- [ ] What changed (clear, concise)
- [ ] Why it changed (business reason; link issue)
- [ ] How it was tested (reproducible steps)
- [ ] Screenshots/video attached
- [ ] Any breaking changes documented
- [ ] Rollback plan (safe to revert?)

**If all ✅:** Submit PR. If any ❌:** Fix and re-check before submitting.

---

## Reviewer: What to Check

**Use This Checklist (In Order):**

### Automated Gates ✅
- [ ] CI/CD green (TypeScript, ESLint, tests)
- [ ] No build errors
- [ ] PR description complete

### Category 1: Code Quality ✅
- [ ] TypeScript strict mode passes
- [ ] ESLint passes
- [ ] No `any` types
- [ ] No console errors

### Category 2: Functionality ✅
- [ ] Feature works as described
- [ ] All UI states implemented and visible
- [ ] Happy path tested (evidence: screenshot)
- [ ] Error paths tested (evidence: screenshot)

### Category 3: Accessibility ✅
- [ ] Keyboard navigation works
- [ ] ARIA labels present
- [ ] Focus management correct
- [ ] Color contrast verified
- [ ] Screen reader tested (evidence: screenshot/video)

### Category 4: Performance ✅
- [ ] No re-render regressions
- [ ] Cache strategy correct
- [ ] Bundle size impact reasonable
- [ ] Lighthouse score maintained (evidence: screenshot)

### Category 5: API & Error Handling ✅
- [ ] API endpoint consumed correctly
- [ ] Error handling comprehensive
- [ ] Network errors handled
- [ ] Validation errors user-friendly

### Category 6: Security & RBAC ✅
- [ ] RoleGate used (not role checking in components)
- [ ] No frontend business logic
- [ ] No sensitive data exposed

### Category 7: UX Consistency ✅
- [ ] Follows design system
- [ ] Responsive design verified (mobile + desktop screenshots)
- [ ] Consistent with existing pages

### Category 8: Documentation ✅
- [ ] Code comments explain WHY
- [ ] JSDoc present
- [ ] User docs updated (if needed)

### Category 9: Release Readiness ✅
- [ ] All checks passing
- [ ] No merge blockers
- [ ] Rollback plan clear

### Decision ✅
- [ ] **APPROVE:** All categories ✅
- [ ] **REQUEST CHANGES:** Note blocking issues; author fixes
- [ ] **ESCALATE:** Disagree with author? Tech lead mediates

---

## Change Risk Categories

### 🟢 Low Risk (Immediate Merge OK)
- Bug fix (accessibility bug, console error)
- Minor UI text update
- Component style refinement
- Performance optimization
- Documentation update

**Merge Criteria:**
- [ ] PR approved by 1 reviewer
- [ ] CI/CD passing
- [ ] No breaking changes
- [ ] Backward compatible

**Timeline:** Next daily release

---

### 🟡 Medium Risk (Plan for Release)
- New component or page
- Significant refactor
- New API integration
- Major style/layout changes
- Performance improvement >5%

**Merge Criteria:**
- [ ] PR approved by tech lead + 1 reviewer
- [ ] CI/CD passing
- [ ] Test evidence provided
- [ ] Documentation updated

**Timeline:** Next planned release

---

### 🔴 High Risk (Coordinate Release)
- Breaking UX change
- Breaking API contract change
- Security fix
- RBAC/authorization changes
- Critical bug fix

**Merge Criteria:**
- [ ] PR approved by tech lead + security
- [ ] CI/CD passing
- [ ] Breaking change documented (ADR)
- [ ] Rollback plan tested
- [ ] Stakeholder approval

**Timeline:** Scheduled release with 1+ week notice

---

## Deploying to Production

### Before Deployment (48 hours)
- [ ] Staging tests passed (regression, integration, smoke, browser, performance, accessibility)
- [ ] Release notes prepared
- [ ] Stakeholders notified
- [ ] Team briefed
- [ ] Rollback plan tested

### During Deployment
- [ ] Build production bundle (`npm run build`)
- [ ] Deploy to production
- [ ] Run smoke tests (login, approvals, leave)
- [ ] Monitor error rates
- [ ] Monitor performance

### After Deployment (First Hour)
- [ ] All critical paths working
- [ ] No console errors
- [ ] User feedback collected
- [ ] Performance acceptable
- [ ] Success announced

### If Issues (Anytime)
- ❌ Critical issue detected?
- → **ROLLBACK:** Revert to previous version (<15 minutes)
- → **ROOT CAUSE:** Investigate
- → **PREVENT:** Update testing or process

---

## API Integration Quick Steps

### Before Implementation
- [ ] Read API documentation
- [ ] Verify endpoint is stable (backend team confirmed)
- [ ] Understand response schema
- [ ] Plan error handling

### During Implementation
- [ ] Create TypeScript types (match API exactly)
- [ ] Create API client method (reusable)
- [ ] Create React Query hook
- [ ] Test against real backend
- [ ] Handle all error scenarios

### Testing
- [ ] Happy path: Data loads correctly
- [ ] Error path: Network error shows message
- [ ] Empty data: No data handled gracefully
- [ ] Performance: No unnecessary re-requests

---

## Accessibility Testing Quick Steps

### Keyboard Navigation
1. Open page in browser
2. Press Tab repeatedly
3. Verify: Can you reach all interactive elements?
4. Verify: Is Tab order logical (left-to-right, top-to-bottom)?
5. Verify: Can you activate with Enter or Space?
6. Verify: Escape closes modals?

### Screen Reader (NVDA - Windows)
1. Download NVDA (free): https://www.nvaccess.org/
2. Start NVDA
3. Tab through page, listen to announcements
4. Verify: Structure makes sense when read aloud
5. Verify: Form labels announced
6. Verify: Buttons are clickable
7. Verify: Errors are announced

### Color Contrast
1. Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
2. Pick text color and background
3. Verify: Ratio ≥ 4.5:1 for normal text
4. Verify: Ratio ≥ 3:1 for large text

---

## What Blocks Merge?

| Issue | Can Merge? |
|-------|-----------|
| TypeScript error | ❌ NO – Fix first |
| ESLint error | ❌ NO – Fix first |
| Console error | ❌ NO – Fix first |
| Accessibility violation | ❌ NO – Fix first |
| Security issue | ❌ NO – Fix first |
| No test evidence | ❌ NO – Provide evidence |
| Lighthouse <90 | ❌ NO – Investigate |
| Missing error handling | ❌ NO – Add handling |
| Code style (Prettier) | ✅ AUTO-FIX – Not a blocker |
| Minor doc gap | ✅ YES – Follow-up PR OK |

---

## Escalation Checklist

**If you disagree with code review feedback:**

1. **Understand** why reviewer thinks change is needed
2. **Ask questions** – Maybe you misunderstood?
3. **Explain** your perspective – Maybe reviewer missed something?
4. **Propose compromise** – Can you both agree on approach?
5. **Tech lead review** – If still disagree, ask tech lead to mediate
6. **Document decision** – Record why you chose this way

**Tech lead then:**
- Reviews both perspectives
- Makes final decision
- Documents in ADR (if architectural decision)
- Shares decision with both parties

---

## Key Principles (Memorize These)

1. **Backend is source of truth**
   - Frontend implements what backend allows
   - Backend always re-validates
   - Frontend never circumvents authorization

2. **Definition of Done is non-negotiable**
   - Every change meets ALL items
   - No "we'll fix it later"
   - Exceptions documented in ADRs only

3. **Accessibility is mandatory**
   - Not optional; not "nice to have"
   - WCAG 2.1 AA compliance required
   - Violations block merge

4. **Performance matters**
   - Lighthouse >90 target
   - Monitor bundle size
   - Optimize re-renders
   - Cache strategy correct

5. **Security > convenience**
   - RoleGate for visibility (backend for authorization)
   - No sensitive data in frontend
   - Input validation (frontend UX; backend enforcement)
   - HTTPS always

6. **Audit trail required**
   - Every change has reason (linked issue)
   - Every PR has approval trail
   - Deployment logged
   - Rollback plan documented

---

## Common Questions

**Q: "Can I use any?"**  
A: No. Type everything explicitly. If stuck, ask for help.

**Q: "Do I need a screenshot?"**  
A: Yes, for every UI change. Show what changed. Show error state.

**Q: "What's a good Lighthouse score?"**  
A: 90+ is good. 95+ is excellent. <80 needs investigation.

**Q: "Can I skip accessibility testing?"**  
A: No. Keyboard test + screen reader test mandatory.

**Q: "Is prop drilling OK?"**  
A: No. Use context or composition instead.

**Q: "Should I create a new component or use an existing one?"**  
A: Reuse existing if possible. Only create new if truly different.

**Q: "Can I add a new dependency?"**  
A: Only with tech lead approval. Check bundle size impact.

**Q: "What if I find a bug on main?"**  
A: Fix immediately. Create hotfix PR. No emergency bypass.

**Q: "Can I work on two features simultaneously?"**  
A: Not recommended. Focus on one PR at a time.

**Q: "What if the backend API changes?"**  
A: Follow [API_CONTRACT_GOVERNANCE.md](API_CONTRACT_GOVERNANCE.md). Coordinate with backend team.

**Q: "How long is a PR review?"**  
A: Target 24 hours. Complex changes may take longer.

**Q: "Can I merge my own PR?"**  
A: No. Someone else must approve and merge.

**Q: "What if there's a disagreement?"**  
A: Tech lead mediates. Decision documented in PR or ADR.

---

## Documents Reference

| Need to... | Read... |
|-----------|---------|
| Understand overall governance | [FRONTEND_GOVERNANCE.md](FRONTEND_GOVERNANCE.md) |
| Know what's required in my PR | [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) |
| Learn naming/structure conventions | [CODING_STANDARDS.md](CODING_STANDARDS.md) |
| Review someone's PR | [PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md) |
| Consume a backend API | [API_CONTRACT_GOVERNANCE.md](API_CONTRACT_GOVERNANCE.md) |
| Deploy to production | [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md) |

---

## Status

✅ **Governance Framework ACTIVE**

All developers, reviewers, and release engineers have clear, written, enforceable standards.

Questions? Consult the documentation. Still unclear? Ask your tech lead.

---

**Last Updated:** December 2025
