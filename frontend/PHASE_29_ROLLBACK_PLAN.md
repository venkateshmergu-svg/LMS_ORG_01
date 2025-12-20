# Phase 29.3 – Rollback Plan

## Leave Management System (LMS) – Production Rollback Procedures

| **Document ID** | LMS-PHASE29-ROLLBACK-001 |
|-----------------|--------------------------|
| **Version**     | 1.0                      |
| **Last Updated**| December 20, 2025        |
| **Status**      | ACTIVE – NON-NEGOTIABLE  |
| **Classification** | Internal – Restricted |

---

## ⚠️ CRITICAL: READ BEFORE DEPLOYMENT

This document is **NON-NEGOTIABLE**. Every team member involved in production deployment MUST:
1. Read this document completely
2. Understand their role in rollback
3. Know the rollback triggers
4. Be able to execute rollback steps

**Rollback Target Time: < 15 minutes**

---

## 1. Rollback Overview

### 1.1 Rollback Strategy

| Aspect | Approach |
|--------|----------|
| **Method** | Blue-Green traffic switch |
| **Target Time** | < 15 minutes |
| **Data Strategy** | Forward-compatible migrations only |
| **Verification** | Smoke test post-rollback |

### 1.2 Rollback Capability Window

| Timeframe | Rollback Method | Complexity |
|-----------|-----------------|------------|
| 0-4 hours post-deploy | Traffic switch (instant) | Low |
| 4-24 hours post-deploy | Traffic switch + data review | Medium |
| 24+ hours post-deploy | Full redeployment + data migration | High |

---

## 2. Rollback Triggers

### 2.1 Automatic Rollback Triggers (IMMEDIATE)

These conditions trigger **immediate** rollback without approval delay:

| Trigger ID | Condition | Threshold | Auto-Action |
|------------|-----------|-----------|-------------|
| AUTO-001 | Error rate spike | > 5% for 5 minutes | Alert + Auto-rollback |
| AUTO-002 | Service unavailable | 0% success for 2 minutes | Alert + Auto-rollback |
| AUTO-003 | Database connection failure | 100% failures | Alert + Auto-rollback |
| AUTO-004 | Security breach detected | Any critical | Alert + Auto-rollback |

### 2.2 Manual Rollback Triggers (APPROVAL REQUIRED)

These conditions require Release Commander approval:

| Trigger ID | Condition | Threshold | Decision Time |
|------------|-----------|-----------|---------------|
| MAN-001 | Elevated error rate | 1-5% sustained | 5 minutes |
| MAN-002 | Performance degradation | p95 > 2x baseline | 10 minutes |
| MAN-003 | Critical functionality broken | Core feature failure | Immediate |
| MAN-004 | Data integrity issue | Any data corruption | Immediate |
| MAN-005 | Business-critical impact | Revenue/compliance risk | Immediate |
| MAN-006 | User-reported critical issues | 3+ similar reports | 10 minutes |
| MAN-007 | Integration failures | External system disconnection | 15 minutes |
| MAN-008 | Security vulnerability | High/Critical CVE discovered | Immediate |

### 2.3 Business Rollback Triggers

| Trigger ID | Condition | Authority |
|------------|-----------|-----------|
| BUS-001 | Leave processing failure | Business Owner |
| BUS-002 | Compliance violation detected | Compliance Officer |
| BUS-003 | Payroll integration error | HR Director |
| BUS-004 | Executive escalation | CIO/CTO |

---

## 3. Rollback Authority

### 3.1 Decision Authority Matrix

| Trigger Type | Primary Authority | Backup Authority | Escalation |
|--------------|-------------------|------------------|------------|
| Automatic | System (auto-triggered) | DevOps On-Call | Release Manager |
| Technical | Release Commander | DevOps Lead | CTO |
| Business | Business Owner | Product Owner | Executive Sponsor |
| Security | Security Lead | CISO | CTO |

### 3.2 Rollback Decision Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ROLLBACK DECISION FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ Issue Detected  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐      YES     ┌─────────────────┐
    │ Auto-trigger    │─────────────▶│ IMMEDIATE       │
    │ threshold met?  │              │ ROLLBACK        │
    └────────┬────────┘              └─────────────────┘
             │ NO
             ▼
    ┌─────────────────┐      YES     ┌─────────────────┐
    │ Critical issue  │─────────────▶│ Alert Release   │
    │ (data/security)?│              │ Commander       │
    └────────┬────────┘              └────────┬────────┘
             │ NO                             │
             ▼                                ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ Start timer     │              │ RC Decision     │
    │ (per threshold) │              │ (< 5 min)       │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             ▼                                ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ Issue resolved  │      NO      │ ROLLBACK or     │
    │ within window?  │─────────────▶│ CONTINUE?       │
    └────────┬────────┘              └─────────────────┘
             │ YES
             ▼
    ┌─────────────────┐
    │ Continue        │
    │ monitoring      │
    └─────────────────┘
```

### 3.3 Emergency Contact Chain

| Order | Role | Contact | When to Call |
|-------|------|---------|--------------|
| 1 | DevOps On-Call | [Phone] | First responder |
| 2 | Release Commander | [Phone] | All rollback decisions |
| 3 | DBA On-Call | [Phone] | Database issues |
| 4 | Security On-Call | [Phone] | Security incidents |
| 5 | Executive Escalation | [Phone] | Business critical |

---

## 4. Rollback Procedures

### 4.1 Pre-Rollback Checklist (60 seconds)

| Step | Action | Owner |
|------|--------|-------|
| 1 | Announce rollback decision on war room | Release Commander |
| 2 | Confirm Blue environment status | DevOps |
| 3 | Alert stakeholders (rollback starting) | Communications |
| 4 | Pause any pending transactions | DBA |

### 4.2 Rollback Execution Steps

#### Step 1: Traffic Switch (Estimated: 2 minutes)

```bash
# ROLLBACK STEP 1: Switch 100% traffic to Blue (previous version)
kubectl patch virtualservice lms-vs -n production --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "lms-blue"}, "weight": 100}
      ]
    }]
  }
}'

# Verify traffic switch
kubectl get virtualservice lms-vs -n production -o yaml | grep -A5 "route:"
```

**Verification Checklist:**
- [ ] Traffic 100% on Blue
- [ ] Green environment receiving 0 requests
- [ ] No new errors in Blue logs

#### Step 2: Verify Blue Environment (Estimated: 3 minutes)

```bash
# ROLLBACK STEP 2: Verify Blue environment health

# Health check
curl -s https://lms.company.com/api/health | jq

# Expected: version should be previous (v2.x.x)

# Verify database connectivity
curl -s https://lms.company.com/api/v1/status

# Check error rate
# (Monitor Grafana/dashboard for next 3 minutes)
```

**Verification Checklist:**
- [ ] Blue environment responding
- [ ] Correct (previous) version displayed
- [ ] Error rate normalized
- [ ] Response times normalized

#### Step 3: Stop Green Environment (Estimated: 2 minutes)

```bash
# ROLLBACK STEP 3: Scale down Green environment

# Scale down Green deployment
kubectl scale deployment lms-green --replicas=0 -n production

# Verify no Green pods running
kubectl get pods -l app=lms-green -n production
```

**Verification Checklist:**
- [ ] Green pods terminated
- [ ] No orphaned processes
- [ ] Resources released

#### Step 4: Database Rollback (IF REQUIRED) (Estimated: 5 minutes)

```bash
# ROLLBACK STEP 4: Database rollback (ONLY if data issues detected)

# WARNING: Only execute if explicitly authorized by DBA and Release Commander

# Check current migration version
alembic current

# Rollback to previous migration (if needed)
# alembic downgrade -1

# Verify migration status
alembic current
```

**⚠️ DATABASE ROLLBACK CRITERIA:**
- Only if Green deployment corrupted data
- Only if migrations are reversible
- Requires DBA explicit authorization

**Verification Checklist:**
- [ ] Migration rolled back (if executed)
- [ ] Data integrity verified
- [ ] No orphaned records

#### Step 5: Post-Rollback Validation (Estimated: 5 minutes)

```bash
# ROLLBACK STEP 5: Validate rollback success

# Run smoke tests
./scripts/smoke_test.sh --environment production

# Verify critical endpoints
curl -s https://lms.company.com/api/v1/leave/types
curl -s https://lms.company.com/api/v1/health
```

**Smoke Test Checklist:**
- [ ] User authentication working
- [ ] Leave balance retrieval working
- [ ] Leave submission working
- [ ] Approval workflow working
- [ ] Dashboard loading

---

## 5. Rollback Scenarios

### 5.1 Scenario A: Traffic Switch Only (Most Common)

**When:** Application issues, no data corruption
**Time:** < 5 minutes

| Step | Action | Duration |
|------|--------|----------|
| 1 | Announce rollback | 30 sec |
| 2 | Execute traffic switch | 2 min |
| 3 | Verify Blue health | 2 min |
| 4 | Confirm success | 30 sec |

### 5.2 Scenario B: Traffic Switch + Green Shutdown

**When:** Need to prevent Green from interfering
**Time:** < 8 minutes

| Step | Action | Duration |
|------|--------|----------|
| 1 | Announce rollback | 30 sec |
| 2 | Execute traffic switch | 2 min |
| 3 | Verify Blue health | 2 min |
| 4 | Scale down Green | 2 min |
| 5 | Confirm success | 1 min |

### 5.3 Scenario C: Full Rollback with Database

**When:** Data corruption detected
**Time:** < 15 minutes

| Step | Action | Duration |
|------|--------|----------|
| 1 | Announce rollback | 30 sec |
| 2 | Execute traffic switch | 2 min |
| 3 | Verify Blue health | 2 min |
| 4 | Scale down Green | 2 min |
| 5 | Database rollback | 5 min |
| 6 | Verify data integrity | 3 min |
| 7 | Confirm success | 30 sec |

### 5.4 Scenario D: Emergency Restore from Backup

**When:** Catastrophic failure, all else fails
**Time:** 30-60 minutes

| Step | Action | Duration |
|------|--------|----------|
| 1 | Escalate to executive level | 5 min |
| 2 | Enable maintenance mode | 2 min |
| 3 | Restore database from backup | 20-40 min |
| 4 | Redeploy last known good | 10 min |
| 5 | Verify restoration | 5 min |

---

## 6. Communication During Rollback

### 6.1 Rollback Communication Sequence

| Time | Action | Channel | Owner |
|------|--------|---------|-------|
| T+0 | "Rollback initiated" | War Room | Release Commander |
| T+0 | Update status page | Status Page | DevOps |
| T+2 min | "Traffic switched" | War Room | DevOps |
| T+5 min | "Rollback verification" | War Room | QA |
| T+8 min | "Rollback complete/failed" | War Room | Release Commander |
| T+10 min | Stakeholder notification | Email/Teams | Communications |

### 6.2 Rollback Communication Templates

#### Template: Rollback Initiated (War Room)

```
🔴 ROLLBACK INITIATED

Time: [TIMESTAMP]
Trigger: [TRIGGER REASON]
Authority: [DECISION MAKER]

Current Status: Switching traffic to Blue environment
ETA: [TIME] minutes

Action Required: All team members standby for verification tasks
```

#### Template: Rollback Complete (Stakeholders)

```
Subject: [LMS] Production Rollback Completed - [DATE]

Dear Stakeholders,

The LMS production deployment has been rolled back due to [BRIEF REASON].

Details:
- Rollback initiated: [TIME]
- Rollback completed: [TIME]
- Current version: [VERSION]
- Service status: OPERATIONAL

Impact:
- [DESCRIBE USER IMPACT]
- [ANY DATA CONSIDERATIONS]

Next Steps:
- Root cause analysis in progress
- Revised deployment timeline TBD

Please contact [SUPPORT EMAIL] for any questions.

Regards,
Release Management Team
```

---

## 7. Post-Rollback Procedures

### 7.1 Immediate Actions (Within 30 minutes)

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Confirm service stability | DevOps | ☐ |
| 2 | Send stakeholder notification | Communications | ☐ |
| 3 | Preserve Green environment logs | DevOps | ☐ |
| 4 | Create incident ticket | Release Manager | ☐ |
| 5 | Begin preliminary RCA | Dev Lead | ☐ |

### 7.2 Root Cause Analysis (Within 24 hours)

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Collect all relevant logs | DevOps | T+4h |
| 2 | Timeline reconstruction | Release Manager | T+8h |
| 3 | Technical root cause identified | Dev Lead | T+24h |
| 4 | Process gap analysis | QA Lead | T+24h |
| 5 | RCA document drafted | Release Manager | T+48h |

### 7.3 Corrective Actions

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Fix identified issue | Development | TBD |
| 2 | Add regression tests | QA | TBD |
| 3 | Update runbooks | DevOps | TBD |
| 4 | Process improvements | Release Manager | TBD |
| 5 | Re-deployment planning | Release Manager | TBD |

---

## 8. Audit Requirements

### 8.1 Rollback Audit Trail

Every rollback MUST be documented with:

| Item | Required |
|------|----------|
| Rollback decision time | ✅ |
| Decision authority | ✅ |
| Trigger reason | ✅ |
| Steps executed | ✅ |
| Commands run (with timestamps) | ✅ |
| Verification results | ✅ |
| Communication sent | ✅ |
| Total rollback time | ✅ |

### 8.2 Rollback Report Template

```markdown
# Rollback Incident Report

**Incident ID:** [INC-XXXX]
**Date:** [DATE]
**Deployment ID:** [DEP-XXXX]

## Summary
[Brief description of what happened]

## Timeline
| Time | Event |
|------|-------|
| HH:MM | Deployment started |
| HH:MM | Issue detected |
| HH:MM | Rollback decision |
| HH:MM | Rollback complete |

## Trigger
- Type: [Auto/Manual/Business]
- Condition: [Specific trigger]
- Decision maker: [Name]

## Impact
- Duration: [X minutes]
- Users affected: [Estimate]
- Data impact: [None/Description]

## Root Cause
[Preliminary or final RCA]

## Corrective Actions
| Action | Owner | Status |
|--------|-------|--------|
| | | |

## Lessons Learned
[Key takeaways]

## Approvals
- Report prepared by: [Name]
- Reviewed by: [Name]
- Approved by: [Name]
```

---

## 9. Rollback Testing Requirements

### 9.1 Pre-Production Rollback Test

Before any production deployment, rollback MUST be tested:

| Test | Environment | Frequency | Owner |
|------|-------------|-----------|-------|
| Traffic switch | Staging | Every release | DevOps |
| Full rollback | Staging | Monthly | DevOps |
| Database rollback | Staging | When migrations present | DBA |
| Backup restore | DR environment | Quarterly | DBA |

### 9.2 Rollback Test Checklist

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 1 | Traffic switch to Blue | < 1 minute | ☐ |
| 2 | Blue health verified | All checks pass | ☐ |
| 3 | Green shutdown | Clean termination | ☐ |
| 4 | Total rollback time | < 15 minutes | ☐ |
| 5 | Post-rollback smoke | All tests pass | ☐ |

---

## 10. Rollback Runbook Quick Reference

### 🚨 EMERGENCY ROLLBACK (Copy & Execute)

```bash
# ===========================================
# EMERGENCY ROLLBACK - EXECUTE IN ORDER
# ===========================================

# 1. SWITCH TRAFFIC TO BLUE (IMMEDIATE)
kubectl patch virtualservice lms-vs -n production --type merge -p '{"spec":{"http":[{"route":[{"destination":{"host":"lms-blue"},"weight":100}]}]}}'

# 2. VERIFY BLUE IS SERVING
curl -s https://lms.company.com/api/health

# 3. SCALE DOWN GREEN
kubectl scale deployment lms-green --replicas=0 -n production

# 4. VERIFY GREEN IS DOWN
kubectl get pods -l app=lms-green -n production

# 5. CHECK ERROR RATE (Wait 2 minutes, check dashboard)
# Dashboard: [URL]

# ===========================================
# ROLLBACK COMPLETE - NOTIFY WAR ROOM
# ===========================================
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Release Team | Initial version |

---

**⚠️ THIS DOCUMENT MUST BE REVIEWED AND SIGNED BY ALL DEPLOYMENT TEAM MEMBERS BEFORE GO-LIVE**

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Release Commander | | |
| | DevOps Lead | | |
| | DBA Lead | | |
| | Dev Lead | | |
| | QA Lead | | |
