# Phase 29.2 – Cutover Strategy & Execution Plan

## Leave Management System (LMS) – Production Deployment

| **Document ID** | LMS-PHASE29-CUTOVER-001 |
|-----------------|-------------------------|
| **Version**     | 1.0                     |
| **Last Updated**| December 20, 2025       |
| **Status**      | ACTIVE                  |
| **Classification** | Internal – Restricted |

---

## 1. Executive Summary

This document defines the cutover strategy for deploying the Leave Management System (LMS) to production. It includes the deployment approach, timeline, step-by-step execution plan, and validation criteria.

---

## 2. Cutover Approach

### 2.1 Deployment Strategy: **Phased Blue-Green Deployment**

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Strategy** | Blue-Green with Canary | Minimize risk, enable instant rollback |
| **Traffic Migration** | Phased (10% → 50% → 100%) | Gradual validation, controlled exposure |
| **Data Migration** | Pre-cutover migration window | Zero downtime for users |
| **Rollback Method** | Traffic switch to Blue | Sub-minute rollback capability |

### 2.2 Environment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LOAD BALANCER                            │
│                    (Traffic Controller)                         │
└─────────────────────┬───────────────────┬───────────────────────┘
                      │                   │
                      ▼                   ▼
           ┌──────────────────┐  ┌──────────────────┐
           │   BLUE (Current) │  │  GREEN (New)     │
           │   LMS v2.x.x     │  │  LMS v3.0.0      │
           │   ✅ Active      │  │  ⏳ Standby      │
           └────────┬─────────┘  └────────┬─────────┘
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌──────────────────┐
                    │    DATABASE      │
                    │  (Shared/Migrated)│
                    └──────────────────┘
```

---

## 3. Go-Live Window

### 3.1 Primary Deployment Window

| Parameter | Value |
|-----------|-------|
| **Date** | [TBD - Suggested: Weekend] |
| **Start Time** | 22:00 UTC (Saturday) |
| **End Time** | 02:00 UTC (Sunday) |
| **Duration** | 4 hours |
| **Timezone Reference** | UTC |
| **Business Impact** | Minimal (off-peak hours) |

### 3.2 Backup Window

| Parameter | Value |
|-----------|-------|
| **Date** | [TBD - Following weekend] |
| **Start Time** | 22:00 UTC |
| **Reason** | Contingency if primary window fails |

### 3.3 Blackout Periods (No Deployment Allowed)

| Period | Reason |
|--------|--------|
| Month-end (last 3 business days) | Payroll processing |
| Quarter-end | Financial close activities |
| Public holidays | Reduced support availability |
| Major business events | Critical business operations |

---

## 4. Cutover Timeline

### 4.1 Detailed Timeline

| Time (UTC) | Phase | Activity | Owner | Duration |
|------------|-------|----------|-------|----------|
| T-7 days | Prep | Final code freeze | Dev Lead | - |
| T-3 days | Prep | Production artifact build | DevOps | 2h |
| T-2 days | Prep | Staging final validation | QA | 4h |
| T-1 day | Prep | Go/No-Go meeting | Release Mgr | 1h |
| T-1 day | Prep | Pre-deployment communications | PM | 1h |
| **T-0** | **Go-Live** | **Cutover begins** | **Release Mgr** | - |

### 4.2 Cutover Night Timeline

| Time | Step | Activity | Owner | Est. Duration |
|------|------|----------|-------|---------------|
| 22:00 | 1 | War room opens, team check-in | Release Mgr | 15 min |
| 22:15 | 2 | Pre-cutover verification | DevOps | 15 min |
| 22:30 | 3 | Database backup verification | DBA | 15 min |
| 22:45 | 4 | Enable maintenance mode (optional) | DevOps | 5 min |
| 22:50 | 5 | Database migrations | DBA | 20 min |
| 23:10 | 6 | Deploy Green environment | DevOps | 15 min |
| 23:25 | 7 | Green environment health check | DevOps | 10 min |
| 23:35 | 8 | Canary traffic (10%) | DevOps | 5 min |
| 23:40 | 9 | Canary monitoring period | All | 15 min |
| 23:55 | 10 | Checkpoint #1 - Go/No-Go | Release Mgr | 5 min |
| 00:00 | 11 | Increase traffic (50%) | DevOps | 5 min |
| 00:05 | 12 | Extended monitoring | All | 20 min |
| 00:25 | 13 | Checkpoint #2 - Go/No-Go | Release Mgr | 5 min |
| 00:30 | 14 | Full traffic (100%) | DevOps | 5 min |
| 00:35 | 15 | Post-deployment validation | QA | 30 min |
| 01:05 | 16 | Disable maintenance mode | DevOps | 5 min |
| 01:10 | 17 | Smoke tests | QA | 20 min |
| 01:30 | 18 | Final checkpoint | Release Mgr | 10 min |
| 01:40 | 19 | Go-live confirmation | Release Mgr | 5 min |
| 01:45 | 20 | Post-deployment communications | PM | 15 min |
| 02:00 | 21 | War room closes | Release Mgr | - |

---

## 5. Pre-Cutover Checks

### 5.1 T-Minus 24 Hours

| # | Check | Owner | Status |
|---|-------|-------|--------|
| 1 | Go/No-Go decision obtained | Release Mgr | ☐ |
| 2 | All team members confirmed available | Release Mgr | ☐ |
| 3 | War room / bridge details distributed | PM | ☐ |
| 4 | Rollback plan reviewed with team | DevOps | ☐ |
| 5 | Stakeholder notification sent | PM | ☐ |
| 6 | Production artifact verified | DevOps | ☐ |
| 7 | Monitoring dashboards prepared | DevOps | ☐ |

### 5.2 T-Minus 1 Hour (Pre-Cutover)

| # | Check | Command/Action | Expected Result | Owner | Status |
|---|-------|----------------|-----------------|-------|--------|
| 1 | Team check-in complete | Roll call | All present | Release Mgr | ☐ |
| 2 | Production DB accessible | `SELECT 1` | Success | DBA | ☐ |
| 3 | Current version verified | `/api/health` | v2.x.x | DevOps | ☐ |
| 4 | Backup verified | Check backup status | Valid backup | DBA | ☐ |
| 5 | Green environment ready | Health check | Healthy | DevOps | ☐ |
| 6 | Load balancer accessible | LB status check | Healthy | Platform | ☐ |
| 7 | Monitoring operational | Dashboard check | All green | DevOps | ☐ |
| 8 | Alerting enabled | Test alert | Alert received | DevOps | ☐ |
| 9 | Rollback artifact verified | Artifact check | Available | DevOps | ☐ |
| 10 | Communication channels ready | Test message | Received | PM | ☐ |

---

## 6. Deployment Steps

### 6.1 Step 1: Database Backup

```bash
# Verify current backup status
# Automated backup should have completed within last 4 hours

# Manual backup if required (DBA responsibility)
pg_dump -h $DB_HOST -U $DB_USER -d lms_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup integrity
pg_restore --list backup_*.sql | head -20
```

**Verification:**
- [ ] Backup file created successfully
- [ ] Backup size is reasonable (compare to previous)
- [ ] Backup integrity verified

### 6.2 Step 2: Database Migration

```bash
# Run migrations against production database
# Migrations should be backward-compatible

alembic upgrade head

# Verify migration status
alembic current
```

**Verification:**
- [ ] All migrations applied successfully
- [ ] No errors in migration log
- [ ] Database schema verified

### 6.3 Step 3: Deploy Green Environment

```bash
# Pull the production-approved container image
docker pull registry.company.com/lms:v3.0.0

# Deploy to Green environment
kubectl set image deployment/lms-green lms=registry.company.com/lms:v3.0.0 -n production

# Wait for rollout
kubectl rollout status deployment/lms-green -n production --timeout=300s
```

**Verification:**
- [ ] All pods running
- [ ] Health checks passing
- [ ] No error logs in pod startup

### 6.4 Step 4: Green Environment Health Check

```bash
# Internal health check
curl -s https://lms-green.internal.company.com/api/health | jq

# Expected response:
# {
#   "status": "healthy",
#   "version": "3.0.0",
#   "database": "connected",
#   "timestamp": "..."
# }

# Verify API endpoints
curl -s https://lms-green.internal.company.com/api/v1/status
```

**Verification:**
- [ ] Health endpoint returns healthy
- [ ] Correct version displayed
- [ ] Database connection confirmed
- [ ] All dependent services connected

### 6.5 Step 5: Canary Traffic (10%)

```bash
# Update load balancer to send 10% traffic to Green
kubectl patch virtualservice lms-vs -n production --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "lms-blue"}, "weight": 90},
        {"destination": {"host": "lms-green"}, "weight": 10}
      ]
    }]
  }
}'

# Verify traffic distribution
kubectl get virtualservice lms-vs -n production -o yaml
```

**Verification:**
- [ ] Traffic split confirmed (90/10)
- [ ] Green environment receiving requests
- [ ] No errors in Green environment logs

### 6.6 Step 6: Canary Monitoring (15 minutes)

**Monitor the following during canary phase:**

| Metric | Threshold | Action if Breached |
|--------|-----------|-------------------|
| Error rate | < 1% | Immediate rollback |
| Response time (p95) | < 500ms | Investigate, consider rollback |
| CPU utilization | < 70% | Investigate |
| Memory utilization | < 80% | Investigate |
| Failed requests | < 0.5% | Immediate rollback |

### 6.7 Step 7: Increase Traffic (50%)

```bash
# Update load balancer to send 50% traffic to Green
kubectl patch virtualservice lms-vs -n production --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "lms-blue"}, "weight": 50},
        {"destination": {"host": "lms-green"}, "weight": 50}
      ]
    }]
  }
}'
```

**Verification:**
- [ ] Traffic split confirmed (50/50)
- [ ] Both environments handling load
- [ ] No degradation in Green environment

### 6.8 Step 8: Full Traffic (100%)

```bash
# Update load balancer to send 100% traffic to Green
kubectl patch virtualservice lms-vs -n production --type merge -p '
{
  "spec": {
    "http": [{
      "route": [
        {"destination": {"host": "lms-green"}, "weight": 100}
      ]
    }]
  }
}'
```

**Verification:**
- [ ] All traffic on Green environment
- [ ] Blue environment idle
- [ ] Production URL resolves to Green

---

## 7. Post-Deployment Validation

### 7.1 Automated Smoke Tests

| Test ID | Test Case | Expected Result | Status |
|---------|-----------|-----------------|--------|
| SMOKE-001 | User login | Successful authentication | ☐ |
| SMOKE-002 | View leave balance | Balance displayed | ☐ |
| SMOKE-003 | Submit leave request | Request created | ☐ |
| SMOKE-004 | Approve leave request | Status updated | ☐ |
| SMOKE-005 | Reject leave request | Status updated | ☐ |
| SMOKE-006 | View leave history | History displayed | ☐ |
| SMOKE-007 | Generate report | Report generated | ☐ |
| SMOKE-008 | Admin dashboard access | Dashboard loads | ☐ |
| SMOKE-009 | Notification delivery | Notification received | ☐ |
| SMOKE-010 | API health check | All endpoints healthy | ☐ |

### 7.2 Manual Verification

| # | Verification | Owner | Status |
|---|--------------|-------|--------|
| 1 | Production URL accessible | QA | ☐ |
| 2 | SSL certificate valid | DevOps | ☐ |
| 3 | Correct version in footer/about | QA | ☐ |
| 4 | Audit logs being generated | Security | ☐ |
| 5 | Metrics flowing to dashboards | DevOps | ☐ |
| 6 | No critical errors in logs | DevOps | ☐ |
| 7 | Email notifications working | QA | ☐ |
| 8 | Integration endpoints responding | DevOps | ☐ |

### 7.3 Business Verification

| # | Verification | Owner | Status |
|---|--------------|-------|--------|
| 1 | Sample leave request workflow | Business Rep | ☐ |
| 2 | Manager approval capability | Business Rep | ☐ |
| 3 | HR admin functions | HR Rep | ☐ |
| 4 | Reporting accuracy | Business Rep | ☐ |

---

## 8. Cutover Checkpoints

### 8.1 Checkpoint #1 (After Canary 10%)

| Question | Answer | Action |
|----------|--------|--------|
| Error rate acceptable? | Yes/No | Continue/Rollback |
| Response times acceptable? | Yes/No | Continue/Rollback |
| Any critical alerts? | Yes/No | Investigate/Rollback |
| Team consensus to proceed? | Yes/No | Continue/Hold |

**Decision:** ☐ PROCEED TO 50% / ☐ HOLD / ☐ ROLLBACK

### 8.2 Checkpoint #2 (After 50% Traffic)

| Question | Answer | Action |
|----------|--------|--------|
| Error rate acceptable? | Yes/No | Continue/Rollback |
| Performance stable? | Yes/No | Continue/Rollback |
| User-reported issues? | Yes/No | Investigate/Rollback |
| Team consensus to proceed? | Yes/No | Continue/Hold |

**Decision:** ☐ PROCEED TO 100% / ☐ HOLD / ☐ ROLLBACK

### 8.3 Final Checkpoint (After 100% Traffic)

| Question | Answer | Action |
|----------|--------|--------|
| All smoke tests passed? | Yes/No | Confirm/Investigate |
| Business validation passed? | Yes/No | Confirm/Investigate |
| Monitoring healthy? | Yes/No | Confirm/Investigate |
| Ready to declare go-live? | Yes/No | Declare/Hold |

**Decision:** ☐ GO-LIVE CONFIRMED / ☐ EXTENDED MONITORING / ☐ ROLLBACK

---

## 9. Post-Cutover Activities

### 9.1 Immediate (Within 1 hour)

- [ ] Send go-live confirmation to stakeholders
- [ ] Update status page
- [ ] Confirm hypercare team handoff
- [ ] Archive deployment logs
- [ ] Update CMDB/service registry

### 9.2 Next Business Day

- [ ] Business validation walkthrough
- [ ] Review overnight logs
- [ ] Address any user feedback
- [ ] Decommission planning for Blue environment
- [ ] Post-implementation review scheduled

---

## 10. War Room Protocol

### 10.1 War Room Details

| Item | Details |
|------|---------|
| **Bridge Line** | [Conference number/link] |
| **Chat Channel** | #lms-golive-war-room |
| **Status Dashboard** | [Dashboard URL] |
| **Incident Channel** | #lms-incidents |

### 10.2 War Room Roles

| Role | Name | Responsibility |
|------|------|----------------|
| **Release Commander** | [Name] | Overall coordination, Go/No-Go decisions |
| **DevOps Lead** | [Name] | Deployment execution, infrastructure |
| **DBA** | [Name] | Database operations |
| **QA Lead** | [Name] | Validation and smoke tests |
| **Dev Lead** | [Name] | Application issues |
| **Security** | [Name] | Security verification |
| **Business Rep** | [Name] | Business validation |
| **Communications** | [Name] | Stakeholder updates |

### 10.3 Communication Protocol

1. **Status updates** every 15 minutes during cutover
2. **Issues** reported immediately in incident channel
3. **Decisions** documented in real-time
4. **Rollback** requires Release Commander approval

---

## 11. Success Criteria

### 11.1 Cutover Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Deployment completed | Within window | Timeline adherence |
| Zero critical errors | 0 | Error monitoring |
| All smoke tests pass | 100% | Test results |
| Business validation pass | Yes | Business sign-off |
| No rollback required | Yes | Deployment status |

### 11.2 Definition of Done

The cutover is considered complete when:

- [x] 100% traffic on new version
- [x] All smoke tests passing
- [x] Business validation completed
- [x] No critical issues open
- [x] Monitoring confirmed healthy
- [x] Go-live announcement sent
- [x] Hypercare team briefed

---

## Appendix A: Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Release Manager | | | |
| DevOps On-Call | | | |
| DBA On-Call | | | |
| Security On-Call | | | |
| Business Sponsor | | | |

---

## Appendix B: Reference Documents

| Document | Location |
|----------|----------|
| Go-Live Readiness Checklist | PHASE_29_GOLIVE_READINESS_CHECKLIST.md |
| Rollback Plan | PHASE_29_ROLLBACK_PLAN.md |
| Communication Plan | PHASE_29_COMMUNICATION_PLAN.md |
| Day-1 Support Plan | PHASE_29_DAY1_SUPPORT_PLAN.md |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Release Team | Initial version |
