# Phase 29.1 – Go-Live Readiness Checklist

## Leave Management System (LMS) – Production Cutover

| **Document ID** | LMS-PHASE29-READINESS-001 |
|-----------------|---------------------------|
| **Version**     | 1.0                       |
| **Last Updated**| December 20, 2025         |
| **Status**      | ACTIVE                    |
| **Classification** | Internal – Restricted  |

---

## Purpose

This checklist provides mandatory verification points that **MUST** be completed and signed off before initiating production go-live. No deployment may proceed until all critical items are marked complete.

---

## Checklist Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete and verified |
| ⏳ | In progress |
| ❌ | Not started / Blocked |
| N/A | Not applicable |

---

## 1. Business Readiness

### 1.1 UAT Sign-Off

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 1.1.1 | UAT Phase 28 formally completed | QA Lead | ⏳ | | UAT completion report |
| 1.1.2 | All critical UAT defects resolved | QA Lead | ⏳ | | Defect tracker |
| 1.1.3 | UAT sign-off document signed | Business Owner | ⏳ | | Signed PDF |
| 1.1.4 | Test evidence archived | QA Lead | ⏳ | | SharePoint link |

### 1.2 Business Approval

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 1.2.1 | Business owner approval obtained | Project Sponsor | ⏳ | | Approval email/document |
| 1.2.2 | Go-live date confirmed by business | Product Owner | ⏳ | | Meeting minutes |
| 1.2.3 | Business impact assessment reviewed | Business Analyst | ⏳ | | Impact report |
| 1.2.4 | Stakeholder communication approved | Communications Lead | ⏳ | | Draft approval |

### 1.3 User Communication

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 1.3.1 | End-user announcement drafted | Communications | ⏳ | | Email draft |
| 1.3.2 | Training materials finalized | Training Lead | ⏳ | | Training docs |
| 1.3.3 | User guide published | Documentation | ⏳ | | Published URL |
| 1.3.4 | Support FAQ prepared | Support Team | ⏳ | | FAQ document |
| 1.3.5 | Go-live schedule communicated | PM | ⏳ | | Calendar invite |

### 1.4 Change Management

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 1.4.1 | Change request submitted | Release Manager | ⏳ | | CR ticket # |
| 1.4.2 | CAB approval obtained | Change Manager | ⏳ | | CAB minutes |
| 1.4.3 | Change window confirmed | Operations | ⏳ | | Calendar entry |
| 1.4.4 | Rollback plan reviewed by CAB | Change Manager | ⏳ | | CAB sign-off |

---

## 2. Technical Readiness

### 2.1 Build & Artifacts

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 2.1.1 | Production build artifact created | DevOps | ⏳ | | Build ID |
| 2.1.2 | Artifact versioned and tagged | DevOps | ⏳ | | Git tag |
| 2.1.3 | Artifact integrity verified (checksum) | DevOps | ⏳ | | SHA256 hash |
| 2.1.4 | Artifact stored in secure registry | DevOps | ⏳ | | Registry URL |
| 2.1.5 | Previous production artifact preserved | DevOps | ⏳ | | Rollback artifact ID |

### 2.2 CI/CD Pipeline

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 2.2.1 | All pipeline stages green | DevOps | ⏳ | | Pipeline URL |
| 2.2.2 | Unit tests passing (100%) | Dev Lead | ⏳ | | Test report |
| 2.2.3 | Integration tests passing | QA | ⏳ | | Test report |
| 2.2.4 | Security scan passed | Security | ⏳ | | Scan report |
| 2.2.5 | Code quality gates passed | Dev Lead | ⏳ | | SonarQube report |
| 2.2.6 | Dependency vulnerability scan clean | Security | ⏳ | | Snyk/Dependabot |

### 2.3 Infrastructure

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 2.3.1 | Production infrastructure provisioned | Platform | ⏳ | | Infra ticket |
| 2.3.2 | Database migrations tested | DBA | ⏳ | | Migration log |
| 2.3.3 | Database backup completed | DBA | ⏳ | | Backup ID |
| 2.3.4 | Load balancer configured | Platform | ⏳ | | Config verification |
| 2.3.5 | SSL certificates valid | Platform | ⏳ | | Cert expiry check |
| 2.3.6 | DNS configuration ready | Platform | ⏳ | | DNS verification |

### 2.4 Monitoring & Observability

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 2.4.1 | Application monitoring enabled | DevOps | ⏳ | | Dashboard URL |
| 2.4.2 | Log aggregation configured | DevOps | ⏳ | | Logging system |
| 2.4.3 | Alerting rules configured | DevOps | ⏳ | | Alert config |
| 2.4.4 | Health endpoints verified | Dev Lead | ⏳ | | Health check URL |
| 2.4.5 | Metrics dashboards ready | DevOps | ⏳ | | Grafana/Dashboard |
| 2.4.6 | On-call rotation confirmed | Operations | ⏳ | | PagerDuty/roster |

### 2.5 Feature Flags & Configuration

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 2.5.1 | Feature flags reviewed | Product Owner | ⏳ | | Flag configuration |
| 2.5.2 | Production config values set | DevOps | ⏳ | | Config file |
| 2.5.3 | Environment variables verified | DevOps | ⏳ | | Env verification |
| 2.5.4 | Rate limits configured | Platform | ⏳ | | Rate limit config |

---

## 3. Security & Compliance

### 3.1 Access Control

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 3.1.1 | RBAC configuration verified | Security | ⏳ | | RBAC audit |
| 3.1.2 | Admin accounts secured | Security | ⏳ | | Access review |
| 3.1.3 | Service accounts audited | Security | ⏳ | | Service account list |
| 3.1.4 | MFA enforced for admin access | Security | ⏳ | | MFA verification |
| 3.1.5 | Least privilege principle verified | Security | ⏳ | | Permissions audit |

### 3.2 Audit & Logging

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 3.2.1 | Audit logging enabled | Security | ⏳ | | Audit config |
| 3.2.2 | Audit log retention configured | Security | ⏳ | | Retention policy |
| 3.2.3 | Audit trail tamper-proof | Security | ⏳ | | Verification |
| 3.2.4 | PII handling compliant | Compliance | ⏳ | | Compliance check |
| 3.2.5 | Data classification verified | Compliance | ⏳ | | Classification doc |

### 3.3 Security Hardening

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 3.3.1 | No secrets in codebase | Security | ⏳ | | Secret scan |
| 3.3.2 | Secrets stored in vault | Security | ⏳ | | Vault config |
| 3.3.3 | Security headers configured | Security | ⏳ | | Header scan |
| 3.3.4 | CORS policy configured | Security | ⏳ | | CORS config |
| 3.3.5 | Input validation verified | Security | ⏳ | | Security review |
| 3.3.6 | SQL injection protection verified | Security | ⏳ | | Security scan |
| 3.3.7 | XSS protection verified | Security | ⏳ | | Security scan |

### 3.4 Compliance

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 3.4.1 | Regulatory requirements met | Compliance | ⏳ | | Compliance report |
| 3.4.2 | Privacy impact assessment done | Legal/Privacy | ⏳ | | PIA document |
| 3.4.3 | Data retention policy applied | Compliance | ⏳ | | Policy doc |
| 3.4.4 | Disaster recovery plan tested | Operations | ⏳ | | DR test results |

---

## 4. Operational Readiness

### 4.1 Support Structure

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 4.1.1 | Support team trained | Support Lead | ⏳ | | Training sign-off |
| 4.1.2 | Support contacts documented | Support Lead | ⏳ | | Contact list |
| 4.1.3 | Escalation matrix defined | Support Lead | ⏳ | | Escalation doc |
| 4.1.4 | Incident response on standby | Operations | ⏳ | | On-call confirmation |
| 4.1.5 | War room / bridge line ready | Operations | ⏳ | | Meeting details |

### 4.2 Rollback Readiness

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 4.2.1 | Rollback plan documented | DevOps | ⏳ | | Rollback plan doc |
| 4.2.2 | Rollback tested in staging | DevOps | ⏳ | | Test results |
| 4.2.3 | Rollback time verified (<15 min) | DevOps | ⏳ | | Timing test |
| 4.2.4 | Rollback authority defined | Release Manager | ⏳ | | Authority doc |
| 4.2.5 | Rollback triggers documented | DevOps | ⏳ | | Trigger criteria |

### 4.3 Documentation

| # | Item | Owner | Status | Sign-Off Date | Evidence |
|---|------|-------|--------|---------------|----------|
| 4.3.1 | Runbook finalized | DevOps | ⏳ | | Runbook doc |
| 4.3.2 | Architecture diagram current | Architect | ⏳ | | Diagram |
| 4.3.3 | API documentation updated | Dev Lead | ⏳ | | API docs URL |
| 4.3.4 | Known issues documented | QA | ⏳ | | Known issues list |

---

## 5. Final Pre-Go-Live Verification

### 5.1 Smoke Test Requirements

| # | Test | Owner | Status | Sign-Off Date |
|---|------|-------|--------|---------------|
| 5.1.1 | User authentication working | QA | ⏳ | |
| 5.1.2 | Leave request submission working | QA | ⏳ | |
| 5.1.3 | Leave approval workflow working | QA | ⏳ | |
| 5.1.4 | Leave balance display correct | QA | ⏳ | |
| 5.1.5 | Notification system working | QA | ⏳ | |
| 5.1.6 | Report generation working | QA | ⏳ | |
| 5.1.7 | Admin functions accessible | QA | ⏳ | |

### 5.2 Go-Live Readiness Summary

| Category | Total Items | Complete | Pending | Blocked |
|----------|-------------|----------|---------|---------|
| Business Readiness | 17 | 0 | 17 | 0 |
| Technical Readiness | 26 | 0 | 26 | 0 |
| Security & Compliance | 21 | 0 | 21 | 0 |
| Operational Readiness | 14 | 0 | 14 | 0 |
| Smoke Tests | 7 | 0 | 7 | 0 |
| **TOTAL** | **85** | **0** | **85** | **0** |

---

## 6. Sign-Off Section

### 6.1 Readiness Confirmation

By signing below, I confirm that all items in my area of responsibility have been verified and are ready for production go-live.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | | | |
| Product Owner | | | |
| Development Lead | | | |
| QA Lead | | | |
| DevOps Lead | | | |
| Security Lead | | | |
| Operations Lead | | | |
| Release Manager | | | |

### 6.2 Final Go-Live Authorization

| Decision | Authorized By | Date | Time |
|----------|---------------|------|------|
| ☐ GO | | | |
| ☐ NO-GO | | | |

**Reason (if NO-GO):**

_____________________________________________

---

## Appendix A: Critical Blockers

Any item marked as a blocker must be listed here with remediation plan:

| Item # | Description | Owner | Target Resolution | Status |
|--------|-------------|-------|-------------------|--------|
| | | | | |

---

## Appendix B: Accepted Risks

Items proceeding with known risks (requires explicit approval):

| Risk ID | Description | Impact | Mitigation | Approved By |
|---------|-------------|--------|------------|-------------|
| | | | | |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Release Team | Initial version |

---

**REMINDER: This checklist must be 100% complete before Go/No-Go decision meeting.**
