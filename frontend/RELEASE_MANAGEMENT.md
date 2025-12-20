# Release & Change Management – Phase 26.5

**Status:** Mandatory | **Scope:** Deployment & Release Procedures | **Effective:** Phase 26

---

## Overview

This document defines how frontend changes are tested, deployed, rolled back, and communicated. The goal is to enable safe, audit-ready releases with minimal risk and fast incident response.

**Key Principle:** All releases are documented, reversible, and tested before deployment.

---

## Table of Contents
1. [Release Readiness Criteria](#release-readiness-criteria)
2. [Pre-Release Testing](#pre-release-testing)
3. [Deployment Process](#deployment-process)
4. [Rollback Procedures](#rollback-procedures)
5. [Communication Plan](#communication-plan)
6. [Breaking UX Changes](#breaking-ux-changes)
7. [Incident Response](#incident-response)
8. [Release Sign-Off](#release-sign-off)

---

## Release Readiness Criteria

### Prerequisite: PR Approval
Before any code is deployed, it must:

- ✅ Have passing CI/CD checks (TypeScript, ESLint, tests)
- ✅ Be reviewed and approved by at least one reviewer using the [PR Review Checklist](PR_REVIEW_CHECKLIST.md)
- ✅ Have all Definition of Done items verified
- ✅ Be merged to `main` or release branch

### Change Categories & Merge Rules

#### 🟢 Category 1: Low-Risk Changes (Bug Fixes, Minor Updates)
**Examples:**
- Bug fix (accessibility bug, console error)
- Minor UI text update
- Component style refinement
- Performance optimization
- Documentation update

**Merge Criteria:**
- [ ] PR approved by one reviewer
- [ ] All CI/CD checks passing
- [ ] No breaking changes to API contracts or UX
- [ ] Backward compatible

**Can Merge:** ✅ Immediately after approval

**Release Timeline:** Next scheduled release (daily/weekly)

#### 🟡 Category 2: Medium-Risk Changes (New Features, Significant Changes)
**Examples:**
- New component or page
- Significant refactor
- New API integration
- Major style/layout changes
- Performance improvement (>5%)

**Merge Criteria:**
- [ ] PR approved by tech lead + one reviewer
- [ ] All CI/CD checks passing
- [ ] Performance impact documented
- [ ] Test evidence provided (manual testing, screenshots)
- [ ] Documentation updated

**Can Merge:** ✅ After tech lead approval

**Release Timeline:** Planned release (can defer if needed)

#### 🔴 Category 3: High-Risk Changes (Breaking Changes, Critical Fixes)
**Examples:**
- Breaking UX change (workflow change, button relocation)
- Breaking API contract change
- Security fix
- Critical bug fix (system down)
- RBAC/authorization changes

**Merge Criteria:**
- [ ] PR approved by tech lead + security lead
- [ ] All CI/CD checks passing
- [ ] Breaking change documented in ADR
- [ ] Rollback plan documented and tested
- [ ] Communication plan in place
- [ ] Release date coordinated with stakeholders

**Can Merge:** ✅ Only after tech lead + security review + stakeholder approval

**Release Timeline:** Scheduled release with communication 1+ week in advance

---

## Pre-Release Testing

### Testing Checklist (Before Deploying to Production)

All changes must be tested in a staging environment before production:

#### 1. Regression Testing
- [ ] Existing pages still load and function correctly
- [ ] Navigation works (no broken links)
- [ ] Existing API calls still work
- [ ] Previous accessibility features still accessible
- [ ] Previous performance maintained (no degradation)

**Test Steps:**
```bash
# 1. Build and deploy to staging
npm run build
# Deploy to staging environment

# 2. Test main workflows
# - Approvals page loads and displays data
# - Leave request creation works
# - Dashboard renders correctly
# - Audit page displays information
# - Navigation between pages works

# 3. Test error paths
# - Network error handling (disconnect wifi)
# - API error handling (401, 500, timeout)
# - Edge cases (empty data, large datasets)

# 4. Test accessibility
# - Keyboard navigation works
# - Screen reader works (NVDA/VoiceOver)
# - Focus visible and logical

# 5. Test performance
# - Page load time acceptable
# - No console errors
# - Lighthouse score >90
```

#### 2. Integration Testing
- [ ] New API endpoints work with frontend code
- [ ] API response format matches types
- [ ] Error responses handled correctly
- [ ] Authentication/authorization working
- [ ] Rate limiting respected

**Test Steps:**
```bash
# Test API integration against staging backend
# 1. Create request with new code
# 2. Verify response is correct shape
# 3. Verify error handling (network, 400s, 500s)
# 4. Verify authentication (valid token, expired token, no token)
# 5. Check for any 401/403 errors
```

#### 3. Smoke Testing
Quick validation that critical paths work:

```bash
# Critical Path 1: User Login
# 1. Open app
# 2. See login form
# 3. Click login button
# 4. Redirected to auth provider
# 5. After auth, see dashboard

# Critical Path 2: View Approvals
# 1. Navigate to Approvals page
# 2. Page loads and displays list
# 3. Click on an approval
# 4. Details display correctly

# Critical Path 3: Create Leave Request
# 1. Navigate to Leave Request form
# 2. Fill form
# 3. Click submit
# 4. Confirmation message shown
# 5. Redirect to list

# Critical Path 4: Accessibility
# 1. Tab through page (keyboard only)
# 2. All interactive elements reachable
# 3. Screen reader announces elements
# 4. Focus visible and logical
```

#### 4. Browser & Device Testing
- [ ] Chrome (desktop, mobile)
- [ ] Firefox (desktop)
- [ ] Safari (desktop, iOS)
- [ ] Edge (desktop)
- [ ] Mobile responsiveness verified

**Test Matrix:**
| Browser | Desktop | Mobile | Status |
|---------|---------|--------|--------|
| Chrome | ✅ | ✅ | Tested |
| Firefox | ✅ | — | Tested |
| Safari | ✅ | ✅ | Tested |
| Edge | ✅ | — | Tested |

#### 5. Performance Testing
- [ ] Lighthouse score ≥90 (mobile)
- [ ] Page load time <3s
- [ ] No Core Web Vitals violations
- [ ] Bundle size increase documented

**Test Steps:**
```bash
npm run build
# Open dist/index.html in Chrome
# DevTools → Lighthouse → Generate report
# Record score and metrics
```

#### 6. Accessibility Testing
- [ ] WCAG 2.1 AA compliance verified
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] No color contrast issues
- [ ] Focus management correct

**Test Steps:**
```bash
# 1. Keyboard navigation
# - Tab through entire page
# - Tab order is logical
# - Focus visible and clear

# 2. Screen reader (NVDA on Windows, VoiceOver on Mac)
# - Open NVDA/VoiceOver
# - Tab through page
# - Listen to announcements
# - Verify structure makes sense

# 3. Color contrast
# - Use WebAIM Contrast Checker
# - Verify 4.5:1 ratio for normal text
# - Verify 3:1 ratio for large text
```

### Test Evidence Collection
Document test results for audit trail:

```markdown
## Release Testing Log

**Release:** v1.2.0
**Date:** 2025-01-01
**Tester:** Jane Doe

### Regression Testing
- [x] Dashboard loads correctly
- [x] Approvals page displays data
- [x] Leave request creation works
- [x] Navigation functional
- [x] No console errors
**Status:** ✅ PASS

### Integration Testing
- [x] New approval API endpoint works
- [x] Response format correct
- [x] Error handling (401, 500, timeout) works
**Status:** ✅ PASS

### Smoke Testing
- [x] Login flow works
- [x] Dashboard loads
- [x] Approvals list displays
- [x] Create leave request works
**Status:** ✅ PASS

### Browser Testing
| Browser | Status |
|---------|--------|
| Chrome (Desktop) | ✅ PASS |
| Firefox (Desktop) | ✅ PASS |
| Safari (macOS) | ✅ PASS |
| Chrome (iOS) | ✅ PASS |

### Performance Testing
- Lighthouse Score: 94 (desktop), 87 (mobile)
- Page Load: 2.3s (desktop), 3.1s (mobile)
- Status: ✅ PASS (within acceptable range)

### Accessibility Testing
- Keyboard navigation: ✅ PASS
- Screen reader (NVDA): ✅ PASS
- Color contrast: ✅ PASS
- Focus management: ✅ PASS

### Overall Status
✅ **APPROVED FOR PRODUCTION RELEASE**

Signed: Jane Doe (QA Engineer)
Date: 2025-01-01
```

---

## Deployment Process

### Phase 1: Pre-Deployment (48 hours before)
1. **Finalize Release Package**
   - [ ] All PRs merged to `main`
   - [ ] Create release branch (e.g., `release/v1.2.0`)
   - [ ] Tag version in Git
   - [ ] Generate release notes

2. **Notify Stakeholders**
   - [ ] Send release notification email
   - [ ] Attach release notes and known issues
   - [ ] Provide rollback timeline
   - [ ] Identify escalation contact

3. **Prepare Rollback Plan**
   - [ ] Document previous version to rollback to
   - [ ] Test rollback procedure (if possible)
   - [ ] Prepare rollback script/steps
   - [ ] Brief on-call engineer on rollback

### Phase 2: Deployment (During Maintenance Window)
1. **Pre-Deployment Checks**
   - [ ] Staging tests completed successfully
   - [ ] Release notes reviewed
   - [ ] Team members available for monitoring
   - [ ] On-call engineer briefed

2. **Deploy to Production**
   ```bash
   # Build production bundle
   npm run build

   # Deploy to production
   # (Exact steps depend on hosting platform)
   # Examples:
   # - Push to production branch (auto-deploy)
   # - Run deploy script
   # - Use CI/CD pipeline
   # - Upload to S3/CDN

   # Verify deployment
   # - Open production URL
   # - Check version number (if shown)
   # - Run smoke tests
   ```

3. **Post-Deployment Verification**
   - [ ] Production URL loads (no 404/500)
   - [ ] Critical paths work (login, approvals, leave)
   - [ ] No console errors
   - [ ] API calls successful
   - [ ] Performance acceptable (monitoring dashboard)

4. **Monitoring (First Hour)**
   - [ ] Monitor error rates (should be 0%)
   - [ ] Monitor performance (page load time)
   - [ ] Watch for support tickets (user issues)
   - [ ] Check logs for warnings/errors

5. **Post-Deployment Communication**
   - [ ] Send deployment success notification
   - [ ] Update status page (if applicable)
   - [ ] Post to team Slack/Teams channel

### Phase 3: Post-Deployment (First Day)
1. **Validate in Production**
   - [ ] Run full smoke test suite
   - [ ] Check error monitoring (Sentry/New Relic)
   - [ ] Review user feedback
   - [ ] Monitor performance metrics

2. **Document Deployment**
   - [ ] Record deployment timestamp
   - [ ] Note any issues encountered
   - [ ] Capture performance baseline
   - [ ] Update deployment log

3. **Debrief (If Issues)**
   - [ ] Root cause analysis
   - [ ] Document what happened
   - [ ] Identify prevention measures
   - [ ] Schedule follow-up

---

## Rollback Procedures

### When to Rollback
Rollback immediately if:
- ❌ Production is down (500 errors)
- ❌ Critical user workflow broken
- ❌ Data loss or corruption
- ❌ Security vulnerability exposed
- ❌ Performance degradation >50%
- ❌ Major accessibility regression

**Do NOT rollback for:**
- ✅ Minor UI text issue (fix forward)
- ✅ Small performance regression <5% (monitor)
- ✅ Single user unable to access (likely user issue; troubleshoot)

### Rollback Timeline
- **Decision Time:** <5 minutes (if issues obvious)
- **Execution Time:** <15 minutes (rollback must be fast)
- **Verification Time:** <5 minutes

**Total:** Service restored within **30 minutes** of issue detection

### Rollback Steps

#### 1. Declare Incident
```bash
# Alert the team
# - Post to incident Slack channel
# - Page on-call engineer
# - Notify tech lead

Message: "INCIDENT: Production deployment has critical issue.
          Rolling back to [previous version].
          ETA for fix: 15 minutes"
```

#### 2. Execute Rollback
```bash
# Option A: Revert to Previous Build
# (If deployment was recent and previous build still accessible)
cd /production
git revert <commit-hash>
npm run build
# Deploy

# Option B: Restore from Backup
# (If infrastructure supports point-in-time restore)
aws s3 restore backup-v1.1.9
npm run deploy

# Option C: Manual Rollback Script
# (Pre-prepared script for common rollback)
./scripts/rollback-to-v1.1.9.sh
```

#### 3. Verify Rollback
```bash
# Smoke tests
# 1. Open production URL
# 2. Login works
# 3. Dashboard loads
# 4. Approvals display
# 5. No console errors
# 6. Version matches expected (v1.1.9)
```

#### 4. Declare Resolution
```bash
# Post to incident channel
Message: "✅ RESOLVED: Rolled back to v1.1.9.
          All services operational.
          Root cause investigation to follow."
```

#### 5. Root Cause Analysis (Next Day)
- [ ] Identify what broke
- [ ] Why didn't it catch in testing?
- [ ] How to prevent in future?
- [ ] Update testing process or documentation

### Rollback Decision Matrix

| Scenario | Severity | Action | Timeline |
|----------|----------|--------|----------|
| App won't load | Critical | Rollback immediately | <5 min |
| Key workflow broken (approvals) | Critical | Rollback immediately | <5 min |
| API returns 500s | Critical | Rollback immediately | <5 min |
| Performance drop 50%+ | High | Rollback within 30 min | <15 min |
| Accessibility broken | High | Rollback within 1 hour | <30 min |
| Data incorrect | Critical | Rollback + investigation | <5 min |
| Single feature has bug | Medium | Fix forward + hotfix | Monitor |
| Minor UI text issue | Low | Fix forward | Next release |

---

## Communication Plan

### 1. Pre-Release Communication (1 week before)

**Audience:** End users, support team, stakeholders

**Message Template:**
```
Subject: Scheduled System Update – [App Name]

Dear Users,

We are planning a system update on [Date] at [Time] (in [Timezone]).

WHAT'S CHANGING:
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]

WHY WE'RE MAKING THIS CHANGE:
- Improve performance
- Fix reported bugs
- Add requested features

EXPECTED IMPACT:
- Estimated downtime: [X] minutes (if any)
- Some features may be temporarily unavailable

HOW TO PREPARE:
- Save any in-progress work before [Time]
- Plan to resume work after [Time]

SUPPORT:
If you have questions, contact: [support email]

Thank you for your patience.
```

### 2. Release Day Communication (Deployment Start)

**Audience:** All users, support team, stakeholders

**Message Template:**
```
Subject: System Update In Progress – [App Name]

The system update is now in progress.

CURRENT STATUS:
- Application may be temporarily unavailable
- Expected duration: [X] minutes
- Estimated completion: [Time]

WE APOLOGIZE FOR ANY INCONVENIENCE

Updates will be posted here as we progress.
Status dashboard: [link]
```

### 3. Deployment Complete Communication (Within 1 hour)

**Audience:** All users, support team

**Message Template:**
```
Subject: System Update Complete – [App Name]

✅ The system update is complete.

WHAT CHANGED:
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]

KNOWN ISSUES:
- [Issue 1]: [Impact and workaround]
- None known at this time

IF YOU EXPERIENCE ISSUES:
- Clear your browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Contact support: [email]

Thank you for your patience!
```

### 4. Issue/Rollback Communication (If Needed)

**Audience:** All users, support team

**Message Template:**
```
Subject: System Update – Issue Detected; Rolling Back

We detected an issue with today's update and are rolling back.

CURRENT STATUS:
- System will be temporarily offline (5-15 minutes)
- We are restoring the previous version
- Expected restoration time: [Time]

WHAT HAPPENED:
- [Brief, honest explanation]

OUR APOLOGIES:
- We did not catch this in testing
- We are investigating why

NEXT STEPS:
- We will investigate and test more thoroughly
- Update will be redeployed when ready

Thank you for your patience.
```

---

## Breaking UX Changes

### Definition
A **breaking UX change** is any change that:
- Changes how users complete a workflow (e.g., button location, approval steps)
- Removes or relocates commonly-used features
- Changes terminology (e.g., "Approve" → "Accept")
- Changes page structure significantly
- Changes validation/error messaging

### Process for Breaking Changes

#### Step 1: Plan (2+ weeks before implementation)
- [ ] Document the change
- [ ] Explain why change is necessary
- [ ] Plan migration path (if users have existing workflows)
- [ ] Schedule training/communication

#### Step 2: Implement with Feature Flags (1 week before release)
```typescript
// ✅ GOOD: Feature flag for breaking change
const showNewApprovalFlow = featureFlags.isEnabled('new-approval-flow');

return (
  <div>
    {showNewApprovalFlow ? (
      <NewApprovalWorkflow /> // New workflow
    ) : (
      <OldApprovalWorkflow /> // Old workflow (still available)
    )}
  </div>
);
```

#### Step 3: Gradual Rollout
- **Day 1-3:** Enable for 10% of users (testing group)
- **Day 4-5:** Enable for 25% of users (early adopters)
- **Day 6-7:** Enable for 50% of users (half the user base)
- **Day 8+:** Enable for 100% of users (complete rollout)

#### Step 4: Communicate (1 week before, during, and after)
- **1 week before:** Announce change is coming
- **3 days before:** Release training materials
- **Day 1:** Start gradual rollout; monitor feedback
- **After:** Gather feedback; iterate if needed

#### Step 5: Remove Old Workflow (2+ weeks after 100% rollout)
Once users have migrated and stabilized:
```typescript
// ✅ GOOD: After migration complete, remove old workflow
return <NewApprovalWorkflow />; // Old workflow removed
```

### Communication for Breaking Changes

**Email to Users (1 week before):**
```
Subject: Important Update to [Feature] – What's Changing

Dear Users,

Next week, we're making changes to how the Approval Workflow works.

WHAT'S CHANGING:
- We're moving the approval buttons to the top of the card (was at bottom)
- We're renaming "Approve Later" to "Defer Decision"
- We're adding a required comment field for rejections

WHY:
- Users told us it was hard to find approval buttons
- More context needed for rejection decisions
- Simplified workflow reduces confusion

WHEN:
- Changes roll out starting [Date]
- Most users will see changes by [Date]

HOW TO PREPARE:
- Review the attached guide [link]
- Training session on [Date] at [Time]
- Contact support if you have questions

We're here to help. Thank you for your feedback!
```

---

## Incident Response

### 1. Issue Detection
Issues discovered through:
- Monitoring dashboards (performance, error rates)
- User reports (support tickets, emails)
- Internal testing (QA or team members)

**Response Time:** Acknowledge within 5 minutes

### 2. Severity Classification

| Severity | Impact | Response | Example |
|----------|--------|----------|---------|
| Critical | System down, data loss, security | Rollback immediately | App returns 500 |
| High | Key workflow broken | Investigate + fix/rollback within 1 hour | Approvals unavailable |
| Medium | Feature has bug, performance degraded | Fix within business day | Slow page load |
| Low | Minor UI issue | Schedule in next release | Typo, color off |

### 3. Incident Timeline

**T=0 (Issue Detected)**
```
- Post to #incidents Slack channel
- Alert on-call engineer
- Notify tech lead
- Gather initial information (error message, user impact)
```

**T=5 min (Initial Response)**
```
- Confirm issue reproducible
- Determine severity
- Decide: Fix forward vs rollback vs investigate
```

**T=15 min (Action Taken)**
```
- If rollback: Execute rollback (< 15 min)
- If hotfix: Deploy fix (< 30 min)
- If investigate: Root cause analysis (< 1 hour)
```

**T=1 hour (Status Update)**
```
- Post incident status to all stakeholders
- Update communication timeline
- Continue monitoring
```

**T=24 hours (Postmortem)**
```
- Root cause analysis complete
- Prevention measures identified
- Action items assigned
- Report shared with team
```

### 4. Incident Log Template

```markdown
## Incident Report

**Incident ID:** INC-2025-001
**Date/Time:** 2025-01-01 14:30 UTC
**Severity:** Critical
**Status:** Resolved

### Summary
Approval page returned 500 errors after v1.2.0 deployment.

### Timeline
- 14:30: User reports "Can't access approvals"
- 14:32: Team confirms issue in production
- 14:33: Decision to rollback made
- 14:45: Rolled back to v1.1.9
- 14:50: All systems operational

### Root Cause
New API endpoint for approvals was not deployed with frontend code.
Mismatch between frontend expecting /api/v2/approvals and backend only having /api/v1/approvals.

### Resolution
Coordinated frontend and backend deployment.

### Prevention
- [ ] Add pre-deployment checklist to verify backend endpoint availability
- [ ] Improve communication between frontend and backend teams
- [ ] Add smoke test that specifically tests new API endpoints

### Action Items
- [ ] Update deployment checklist by [Date] – [Owner]
- [ ] Schedule backend/frontend sync meeting by [Date] – [Owner]
- [ ] Add smoke test for API integration by [Date] – [Owner]

### Lessons Learned
- Feature flag would have allowed partial rollout
- Better pre-release testing with real backend would have caught this
- Communication gap between teams

**Incident Manager:** Jane Doe
**Report Date:** 2025-01-02
```

---

## Release Sign-Off

### Pre-Release Sign-Off
Before deploying to production, all stakeholders must sign off:

```markdown
## Release Sign-Off – v1.2.0

**Release Date:** 2025-01-01
**Release Manager:** John Doe

### Approvals Required
- [ ] Tech Lead: Code quality, architecture – [Name/Date]
- [ ] Security Lead: Security review, vulnerabilities – [Name/Date]
- [ ] QA Lead: Test results, bug fixes – [Name/Date]
- [ ] Product Owner: Feature completeness, priority – [Name/Date]

### Release Notes
[Attached separately]

### Known Issues
- Minor visual misalignment on mobile (will fix in v1.2.1)

### Rollback Plan
If critical issue: Rollback to v1.1.9 (< 15 minutes)

### Communication Sent
- [ ] Pre-release notification to users
- [ ] Team briefing completed
- [ ] Support team trained

### Final Approval
I approve this release for production deployment.

**Signed:** [Tech Lead Name]
**Date:** 2025-01-01
```

---

## Release Checklist

Use this checklist before every production release:

```markdown
## Release Checklist – v[VERSION]

### Pre-Release (48 hours before)
- [ ] All code merged and reviewed
- [ ] Release notes prepared
- [ ] Staging tests completed (all pass)
- [ ] Performance baseline captured
- [ ] Rollback plan documented
- [ ] Stakeholders notified
- [ ] Support team trained

### Deployment Day
- [ ] All team members available
- [ ] On-call engineer briefed
- [ ] Build process verified (`npm run build`)
- [ ] Deployment script ready
- [ ] Monitoring dashboards accessible
- [ ] Slack incident channel open

### Deployment
- [ ] Deploy to production
- [ ] Smoke tests pass (login, approvals, leave)
- [ ] No console errors
- [ ] API calls working
- [ ] Performance acceptable

### Post-Deployment
- [ ] Deployment success announced
- [ ] Monitor error rates (< 0.1%)
- [ ] Monitor performance (page load < 3s)
- [ ] Check support tickets
- [ ] Confirm no user issues

### Debrief (Next Day)
- [ ] Release successful? YES / NO
- [ ] Any issues encountered?
- [ ] Lessons learned captured
- [ ] Actions items filed
- [ ] Deployment log updated

**Deployed By:** [Name]
**Deployment Time:** [Time]
**Status:** ✅ SUCCESS / ❌ ROLLED BACK
```

---

**Release & Change Management Version:** 1.0 | **Status:** Active | **Last Updated:** December 2025
