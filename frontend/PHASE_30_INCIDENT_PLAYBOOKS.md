# Phase 30.3 – Incident Response Playbooks

## Leave Management System (LMS) – Operational Response Procedures

| **Document ID** | LMS-PHASE30-PLAYBOOK-001 |
|-----------------|---------------------------|
| **Version**     | 1.0                       |
| **Last Updated**| December 20, 2025         |
| **Status**      | ACTIVE                    |
| **Classification** | Internal – Restricted  |

---

## 1. Overview

This document provides step-by-step incident response playbooks for common production scenarios in the Leave Management System. Each playbook is designed for rapid execution during incidents.

### 1.1 Playbook Index

| ID | Playbook | Severity | Page |
|----|----------|----------|------|
| PB-001 | Production Outage | SEV-1 | Section 2 |
| PB-002 | Data Inconsistency | SEV-1/2 | Section 3 |
| PB-003 | Security Incident | SEV-1 | Section 4 |
| PB-004 | Integration Failure (HRIS/Payroll) | SEV-1/2 | Section 5 |
| PB-005 | Performance Degradation | SEV-2/3 | Section 6 |
| PB-006 | Authentication Failure | SEV-1/2 | Section 7 |
| PB-007 | Database Issues | SEV-1/2 | Section 8 |

---

## 2. PB-001: Production Outage

### 2.1 Scenario Description

**Definition:** The LMS application is completely inaccessible to all users.

**Detection Signals:**
- Health check endpoint failing
- Monitoring alerts (Datadog/Prometheus)
- Multiple user reports simultaneously
- Load balancer showing no healthy targets
- APM showing 0 successful requests

### 2.2 Immediate Actions (First 15 Minutes)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **CONFIRM** outage via multiple checks | On-Call | 2 min |
| 2 | **OPEN** incident bridge/war room | On-Call | 2 min |
| 3 | **PAGE** all required responders | On-Call | 2 min |
| 4 | **UPDATE** status page to "Investigating" | DevOps | 3 min |
| 5 | **NOTIFY** stakeholders (initial) | Incident Lead | 5 min |
| 6 | **BEGIN** parallel diagnostics | All | Ongoing |

### 2.3 Diagnostic Checklist

```bash
# 1. Check application health
curl -s https://lms.company.com/api/health

# 2. Check pod/container status
kubectl get pods -n production -l app=lms

# 3. Check recent deployments
kubectl rollout history deployment/lms -n production

# 4. Check load balancer
kubectl get svc lms -n production
kubectl describe ingress lms -n production

# 5. Check database connectivity
kubectl exec -it <pod> -n production -- nc -zv $DB_HOST 5432

# 6. Check recent logs
kubectl logs -l app=lms -n production --tail=100

# 7. Check resource usage
kubectl top pods -n production
```

### 2.4 Decision Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION OUTAGE DECISION TREE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │ Outage Confirmed│
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Recent deployment?      │
                    └─────────────┬───────────┘
                          YES     │     NO
                    ┌─────────────┴───────────┐
                    │                         │
                    ▼                         ▼
           ┌────────────────┐       ┌────────────────┐
           │ ROLLBACK       │       │ Infrastructure │
           │ immediately    │       │ check          │
           └────────────────┘       └───────┬────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                              ▼                           ▼
                    ┌────────────────┐         ┌────────────────┐
                    │ DB issue?      │         │ External dep?  │
                    └───────┬────────┘         └───────┬────────┘
                            │                          │
                    ┌───────┴───────┐          ┌───────┴───────┐
                    │ YES           │          │ YES           │
                    ▼               ▼          ▼               ▼
              ┌──────────┐   ┌──────────┐ ┌──────────┐   ┌──────────┐
              │DB Playbook│   │ Continue │ │ Vendor   │   │ Continue │
              │ (PB-007) │   │ diagnosis│ │ escalate │   │ diagnosis│
              └──────────┘   └──────────┘ └──────────┘   └──────────┘
```

### 2.5 Rollback Procedure

**Trigger:** Recent deployment identified as cause

```bash
# 1. Check current and previous versions
kubectl rollout history deployment/lms -n production

# 2. Rollback to previous version
kubectl rollout undo deployment/lms -n production

# 3. Verify rollback
kubectl rollout status deployment/lms -n production

# 4. Confirm health
curl -s https://lms.company.com/api/health
```

### 2.6 Escalation Path

| Time | Action |
|------|--------|
| T+15m | If no progress, escalate to Engineering Manager |
| T+30m | If no progress, escalate to IT Director |
| T+1h | If no progress, activate DR (if applicable) |

### 2.7 Resolution & Closure

| Step | Action | Owner |
|------|--------|-------|
| 1 | Confirm all health checks passing | DevOps |
| 2 | Verify user access restored | QA/Support |
| 3 | Update status page to "Resolved" | DevOps |
| 4 | Send resolution notification | Incident Lead |
| 5 | Document incident timeline | Incident Lead |
| 6 | Schedule PIR within 5 days | Incident Lead |

---

## 3. PB-002: Data Inconsistency

### 3.1 Scenario Description

**Definition:** Leave balances, accruals, or transaction data showing incorrect values.

**Detection Signals:**
- User reports of wrong balances
- Reconciliation job failures
- Audit log anomalies
- Integration mismatch alerts
- Payroll discrepancy reports

### 3.2 Severity Assessment

| Condition | Severity |
|-----------|----------|
| All users affected | SEV-1 |
| Large group (>100 users) | SEV-1 |
| Department affected | SEV-2 |
| Individual users (<10) | SEV-3 |

### 3.3 Immediate Actions

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **STOP** any running batch jobs | DevOps | 2 min |
| 2 | **IDENTIFY** scope of impact | Tier 2 | 15 min |
| 3 | **PRESERVE** evidence (logs, data snapshots) | DBA | 10 min |
| 4 | **NOTIFY** affected users (if known) | Support | 15 min |
| 5 | **DISABLE** self-service if widespread | DevOps | 5 min |

### 3.4 Investigation Checklist

```sql
-- 1. Check recent balance changes
SELECT user_id, leave_type, old_balance, new_balance, changed_at, changed_by
FROM leave_balance_audit
WHERE changed_at > NOW() - INTERVAL '24 hours'
ORDER BY changed_at DESC;

-- 2. Identify affected users
SELECT COUNT(DISTINCT user_id), leave_type
FROM leave_balance_audit
WHERE changed_at > NOW() - INTERVAL '24 hours'
GROUP BY leave_type;

-- 3. Check for recent batch jobs
SELECT job_name, status, started_at, completed_at, records_processed
FROM batch_job_history
WHERE started_at > NOW() - INTERVAL '24 hours';

-- 4. Compare with HRIS source
SELECT lms.user_id, lms.balance, hris.balance, 
       lms.balance - hris.balance as diff
FROM lms_balances lms
JOIN hris_sync_data hris ON lms.user_id = hris.user_id
WHERE ABS(lms.balance - hris.balance) > 0;
```

### 3.5 Remediation Options

| Option | When to Use | Approval |
|--------|-------------|----------|
| **Point-in-time restore** | Widespread corruption | DBA + IT Director |
| **Targeted data correction** | Known subset affected | Tier 2 Lead + Business |
| **Batch recalculation** | Calculation error | Tier 3 + Business |
| **Manual adjustment** | Individual cases | Tier 2 + Manager |

### 3.6 Data Correction Process

```
CRITICAL: All data corrections require:
1. Approval from Business Owner
2. Documented change request
3. Audit log entry
4. Before/after evidence
5. Verification step
```

| Step | Action | Owner |
|------|--------|-------|
| 1 | Document current (incorrect) state | Tier 2 |
| 2 | Calculate correct values | Tier 2 + Business |
| 3 | Obtain written approval | Business Owner |
| 4 | Execute correction (with audit entry) | DBA/Tier 3 |
| 5 | Verify correction | Tier 2 |
| 6 | Notify affected users | Support |
| 7 | Archive evidence | Tier 2 |

### 3.7 Rollback Decision Criteria

**Consider database restore if:**
- More than 1000 users affected
- Multiple data types corrupted
- No clear correction path
- Corruption ongoing
- Compliance/audit risk

---

## 4. PB-003: Security Incident

### 4.1 Scenario Description

**Definition:** Confirmed or suspected unauthorized access, data breach, or security vulnerability exploitation.

**Detection Signals:**
- SIEM/security alerts
- Unusual access patterns
- Failed authentication spikes
- Unauthorized data access logs
- External breach notification
- Vulnerability scan findings (critical)

### 4.2 Immediate Actions (CRITICAL)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **ALERT** Security team immediately | Discoverer | 1 min |
| 2 | **DO NOT** attempt to investigate alone | All | - |
| 3 | **PRESERVE** all logs and evidence | Security | Immediate |
| 4 | **ISOLATE** affected systems if active breach | Security | 5 min |
| 5 | **NOTIFY** CISO | Security Lead | 5 min |
| 6 | **ACTIVATE** security incident response team | CISO | 10 min |

### 4.3 Security Incident Classification

| Type | Description | Response |
|------|-------------|----------|
| **Data Breach** | Confirmed unauthorized data access | Full IR, Legal, Regulatory |
| **Account Compromise** | User credentials stolen/misused | Reset, Investigate, Notify |
| **Vulnerability Exploit** | Active exploitation detected | Patch, Block, Investigate |
| **Insider Threat** | Internal unauthorized access | HR, Legal, Investigate |
| **Malware** | Malicious code detected | Isolate, Clean, Investigate |

### 4.4 Evidence Preservation

```bash
# CRITICAL: Preserve evidence before any remediation

# 1. Capture current state
kubectl logs -l app=lms -n production --all-containers > incident_logs_$(date +%Y%m%d_%H%M%S).log

# 2. Export audit logs
SELECT * FROM audit_log 
WHERE timestamp > '[INCIDENT_START]'
INTO OUTFILE '/secure/audit_export.csv';

# 3. Capture network state
kubectl get networkpolicy -n production -o yaml > network_state.yaml

# 4. Document running processes
kubectl exec <pod> -- ps aux > processes.txt
```

### 4.5 Containment Actions

| Threat Type | Containment Action |
|-------------|-------------------|
| Compromised account | Disable account, revoke all sessions |
| API abuse | Block IP/token, rate limit |
| SQL injection | WAF rule, disable endpoint |
| Data exfiltration | Network isolation, egress block |
| Privilege escalation | Revoke permissions, audit access |

### 4.6 Communication Protocol

```
SECURITY INCIDENT COMMUNICATION RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• All communications via SECURE channels only
• NO details in email/chat initially
• Security team controls messaging
• Legal/Compliance MUST approve external comms
• Regulatory notification per compliance requirements
```

### 4.7 Escalation & Notification

| Time | Action | Notify |
|------|--------|--------|
| Immediate | Security team engaged | CISO |
| T+30m | Initial assessment complete | CIO, Legal |
| T+1h | Containment status | Executive team |
| If data breach | Regulatory assessment | Compliance, Legal |
| As required | Law enforcement | Legal (coordinates) |

### 4.8 Post-Incident Requirements

| Requirement | Timeline |
|-------------|----------|
| Forensic analysis complete | 72 hours |
| Preliminary report | 5 days |
| Full PIR | 10 days |
| Regulatory filings (if required) | Per regulation |
| User notification (if required) | Per regulation/policy |

---

## 5. PB-004: Integration Failure (HRIS/Payroll)

### 5.1 Scenario Description

**Definition:** HRIS or Payroll system integration has stopped functioning, causing data sync failures.

**Detection Signals:**
- Integration monitoring alerts
- Sync job failures
- Missing employee updates
- Payroll feed errors
- Data discrepancy reports

### 5.2 Severity Assessment

| Condition | Severity |
|-----------|----------|
| Payroll feed failed (during payroll window) | SEV-1 |
| Complete HRIS sync failure | SEV-2 |
| Partial sync failure | SEV-2 |
| Sync delayed (< 4 hours) | SEV-3 |

### 5.3 Immediate Actions

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **VERIFY** integration status | Tier 2 | 5 min |
| 2 | **CHECK** external system status | Tier 2 | 5 min |
| 3 | **NOTIFY** integration partner | Tier 2 | 10 min |
| 4 | **ASSESS** business impact | Business Analyst | 15 min |
| 5 | **COMMUNICATE** to affected teams | Support | 20 min |

### 5.4 Diagnostic Checklist

```bash
# 1. Check integration job status
curl -s https://lms.company.com/api/v1/integration/status

# 2. Check connectivity to external system
nc -zv hris.company.com 443
nc -zv payroll.company.com 443

# 3. Check API credentials
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $HRIS_TOKEN" \
  https://hris.company.com/api/health

# 4. Review integration logs
kubectl logs -l app=lms-integration-worker -n production --tail=200

# 5. Check message queue
kubectl exec <pod> -- rabbitmqctl list_queues | grep integration
```

### 5.5 Common Causes & Resolutions

| Cause | Resolution |
|-------|------------|
| Credential expired | Rotate API key/token |
| Network connectivity | Check firewall, DNS, routing |
| External system down | Wait for partner resolution |
| Data format change | Update parser, coordinate with partner |
| Rate limit exceeded | Backoff and retry, request limit increase |
| Certificate expired | Renew certificate |

### 5.6 Manual Sync Procedure

**When:** Automated sync failed, manual intervention required

```bash
# 1. Trigger manual sync (with approval)
curl -X POST https://lms.company.com/api/v1/integration/sync \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"type": "hris", "mode": "full"}'

# 2. Monitor progress
curl -s https://lms.company.com/api/v1/integration/sync/status/{job_id}
```

### 5.7 Payroll-Specific Procedures

```
⚠️ PAYROLL INTEGRATION FAILURE - CRITICAL PATH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If failure occurs during payroll processing window:

1. IMMEDIATELY escalate to SEV-1
2. CONTACT Payroll department directly
3. ASSESS manual export options
4. PREPARE fallback data file
5. COORDINATE with Payroll for manual processing
6. DOCUMENT all manual steps for audit
```

### 5.8 Vendor Escalation

| Level | Contact | When |
|-------|---------|------|
| L1 | Vendor support portal | Initial contact |
| L2 | Vendor phone support | No response in 30 min |
| L3 | Vendor account manager | Critical issue, no progress |
| L4 | Executive escalation | Business-critical, SLA breach |

---

## 6. PB-005: Performance Degradation

### 6.1 Scenario Description

**Definition:** System response times significantly slower than baseline, affecting user experience.

**Detection Signals:**
- APM alerts (response time > threshold)
- User complaints of slowness
- Increased timeout errors
- High CPU/memory utilization
- Database slow query alerts

### 6.2 Severity Assessment

| Condition | Severity |
|-----------|----------|
| System unusable (>10s response) | SEV-2 |
| Significantly degraded (>3s) | SEV-2 |
| Noticeably slow (>1s) | SEV-3 |
| Minor slowdown | SEV-4 |

### 6.3 Immediate Actions

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **VERIFY** via APM dashboard | DevOps | 2 min |
| 2 | **IDENTIFY** affected components | DevOps | 5 min |
| 3 | **CHECK** resource utilization | DevOps | 5 min |
| 4 | **REVIEW** recent changes | DevOps | 5 min |
| 5 | **SCALE** if resource-bound | DevOps | 10 min |

### 6.4 Diagnostic Commands

```bash
# 1. Check pod resource usage
kubectl top pods -n production

# 2. Check node resources
kubectl top nodes

# 3. Check for resource throttling
kubectl describe pod <pod> -n production | grep -A5 "Limits\|Requests"

# 4. Check HPA status
kubectl get hpa -n production

# 5. Check database connections
kubectl exec <pod> -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# 6. Check slow queries
kubectl exec <db-pod> -- psql -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
  FROM pg_stat_activity 
  WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '1 second';"
```

### 6.5 Performance Decision Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE ISSUE DECISION TREE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │ Slowness        │
                         │ Confirmed       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Check Resource Usage    │
                    └─────────────┬───────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌─────────────────┐         ┌─────────────────┐
          │ CPU/Memory High │         │ Resources OK    │
          │ (>80%)          │         │                 │
          └────────┬────────┘         └────────┬────────┘
                   │                           │
                   ▼                           ▼
          ┌─────────────────┐         ┌─────────────────┐
          │ Scale Up/Out    │         │ Check Database  │
          │ or Optimize     │         └────────┬────────┘
          └─────────────────┘                  │
                                     ┌─────────┴─────────┐
                                     │                   │
                                     ▼                   ▼
                           ┌─────────────────┐  ┌─────────────────┐
                           │ Slow Queries?   │  │ Check External  │
                           │ Yes: Optimize   │  │ Dependencies    │
                           └─────────────────┘  └─────────────────┘
```

### 6.6 Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| High CPU | Scale up replicas |
| High Memory | Restart pods (rolling) |
| Connection pool exhausted | Increase pool size |
| Slow queries | Kill query, add index |
| External dependency slow | Enable caching, circuit breaker |

### 6.7 Scaling Commands

```bash
# Scale horizontally
kubectl scale deployment lms --replicas=6 -n production

# Or use HPA
kubectl patch hpa lms -n production -p '{"spec":{"maxReplicas":10}}'

# Verify scaling
kubectl get pods -n production -w
```

---

## 7. PB-006: Authentication Failure

### 7.1 Scenario Description

**Definition:** Users unable to authenticate to the system.

**Detection Signals:**
- Multiple failed login reports
- Auth service errors in logs
- SSO/SAML failures
- Token validation errors
- Session management issues

### 7.2 Severity Assessment

| Condition | Severity |
|-----------|----------|
| All users affected | SEV-1 |
| SSO completely down | SEV-1 |
| Subset of users affected | SEV-2 |
| Intermittent failures | SEV-3 |

### 7.3 Diagnostic Checklist

```bash
# 1. Check auth service health
curl -s https://lms.company.com/api/auth/health

# 2. Check SSO/IdP status
curl -s -o /dev/null -w "%{http_code}" https://sso.company.com/health

# 3. Check auth logs for errors
kubectl logs -l app=lms -n production | grep -i "auth\|login\|token" | tail -50

# 4. Verify SAML/OIDC configuration
kubectl get secret lms-auth-config -n production -o yaml

# 5. Check certificate validity
echo | openssl s_client -servername sso.company.com -connect sso.company.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 7.4 Common Causes & Resolutions

| Cause | Resolution |
|-------|------------|
| SSO/IdP down | Escalate to identity team |
| Certificate expired | Renew certificate |
| Token signing key rotated | Update LMS configuration |
| Session store (Redis) down | Restart Redis, check cluster |
| DNS issue | Check DNS resolution |
| Clock skew | Sync NTP across systems |

---

## 8. PB-007: Database Issues

### 8.1 Scenario Description

**Definition:** Database performance problems, connectivity issues, or data integrity concerns.

**Detection Signals:**
- Database connection timeouts
- Slow query alerts
- Replication lag alerts
- Storage alerts
- Connection pool exhaustion

### 8.2 Severity Assessment

| Condition | Severity |
|-----------|----------|
| Database unreachable | SEV-1 |
| Data corruption suspected | SEV-1 |
| Severe performance impact | SEV-2 |
| Replication lag (< 1 hour) | SEV-3 |

### 8.3 Diagnostic Checklist

```sql
-- 1. Check connection count
SELECT count(*) FROM pg_stat_activity;

-- 2. Check for locks
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 3. Check slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds';

-- 4. Check replication status
SELECT client_addr, state, sent_lsn, write_lsn, replay_lsn
FROM pg_stat_replication;

-- 5. Check table bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### 8.4 Emergency Actions

| Issue | Action |
|-------|--------|
| Connection exhaustion | Kill idle connections, increase pool |
| Long-running query | Terminate query: `SELECT pg_terminate_backend(pid)` |
| Lock contention | Identify and kill blocking query |
| Storage full | Emergency cleanup, expand storage |
| Replication broken | Rebuild replica from primary |

---

## 9. Playbook Maintenance

### 9.1 Review Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Playbook accuracy review | Quarterly | Tier 3 Lead |
| Tabletop exercises | Semi-annual | All tiers |
| Post-incident playbook updates | After each SEV-1/2 | Incident Lead |
| Contact information update | Monthly | Operations |

### 9.2 Change Control

| Change | Approval |
|--------|----------|
| Minor updates (contacts, commands) | Tier 3 Lead |
| New playbook | Engineering Manager |
| Procedure changes | IT Director |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Operations Team | Initial version |
