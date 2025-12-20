# Phase 30.2 – Incident Classification & SLA Matrix

## Leave Management System (LMS) – Severity Levels & Service Level Agreements

| **Document ID** | LMS-PHASE30-SLA-001 |
|-----------------|----------------------|
| **Version**     | 1.0                  |
| **Last Updated**| December 20, 2025    |
| **Status**      | ACTIVE               |
| **Classification** | Internal          |

---

## 1. Purpose

This document defines the incident classification framework and Service Level Agreements (SLAs) for the Leave Management System. Consistent classification ensures appropriate prioritization, resource allocation, and stakeholder communication.

---

## 2. Incident Severity Definitions

### 2.1 Severity Overview

| Severity | Name | Definition | Business Impact |
|----------|------|------------|-----------------|
| **SEV-1** | Critical | Complete system failure or security breach | Business stopped |
| **SEV-2** | High | Major functionality impaired | Significant impact |
| **SEV-3** | Medium | Partial functionality affected | Moderate impact |
| **SEV-4** | Low | Minor issues, cosmetic defects | Minimal impact |

---

## 3. SEV-1 – Critical

### 3.1 Definition

A SEV-1 incident represents a **complete system failure** or **critical security breach** that affects all users and/or poses immediate risk to the organization.

### 3.2 Qualifying Conditions

| Condition | Example |
|-----------|---------|
| **Complete Outage** | LMS application inaccessible to all users |
| **Security Breach** | Confirmed unauthorized data access |
| **Data Loss** | Production data corruption or loss |
| **Payroll Impact** | Leave data unavailable for payroll processing |
| **Compliance Violation** | Audit-critical function unavailable |
| **Safety Impact** | System failure affecting employee safety tracking |

### 3.3 SLA Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| **Response Time** | 15 minutes | 15 minutes |
| **Initial Assessment** | 30 minutes | 30 minutes |
| **Resolution Target** | 4 hours | 8 hours |
| **Update Frequency** | Every 30 minutes | Every 30 minutes |
| **Escalation to Executive** | 1 hour if unresolved | 1 hour |

### 3.4 Response Requirements

| Requirement | Details |
|-------------|---------|
| **War Room** | Immediate activation |
| **Bridge Line** | Open within 15 minutes |
| **On-Call** | All relevant on-call resources engaged |
| **Executive Notification** | Within 30 minutes |
| **Status Page** | Updated within 15 minutes |
| **PIR** | Mandatory within 5 business days |

### 3.5 Communication Cadence

| Time | Communication |
|------|---------------|
| T+0 | Incident detected, war room opened |
| T+15m | Initial notification to stakeholders |
| T+30m | Status update #1 |
| T+1h | Status update #2 (executive if unresolved) |
| Every 30m | Ongoing updates until resolved |
| Resolution | Resolution notification |
| T+24h | Preliminary incident report |
| T+5d | Full PIR published |

---

## 4. SEV-2 – High

### 4.1 Definition

A SEV-2 incident represents **major functionality impairment** affecting a large user group or critical business process, but the system remains partially operational.

### 4.2 Qualifying Conditions

| Condition | Example |
|-----------|---------|
| **Core Feature Down** | Leave submission not working |
| **Approval Blocked** | Approval workflow completely broken |
| **Large Group Affected** | Entire department/location impacted |
| **Integration Failure** | HRIS/Payroll sync completely broken |
| **Severe Performance** | System unusable due to performance |
| **Data Accuracy** | Widespread incorrect balance calculations |

### 4.3 SLA Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| **Response Time** | 30 minutes | 1 hour |
| **Initial Assessment** | 1 hour | 2 hours |
| **Resolution Target** | 8 hours | 24 hours |
| **Update Frequency** | Every 1 hour | Every 2 hours |
| **Escalation** | 4 hours if unresolved | 4 hours |

### 4.4 Response Requirements

| Requirement | Details |
|-------------|---------|
| **Incident Channel** | Activate #lms-incidents |
| **On-Call** | Primary on-call engaged |
| **Management Notification** | Within 1 hour |
| **Status Page** | Updated within 30 minutes |
| **PIR** | Mandatory within 10 business days |

### 4.5 Communication Cadence

| Time | Communication |
|------|---------------|
| T+0 | Incident detected |
| T+30m | Initial notification |
| T+1h | First status update |
| Every 1h | Ongoing updates |
| Resolution | Resolution notification |
| T+48h | Incident summary |
| T+10d | PIR published |

---

## 5. SEV-3 – Medium

### 5.1 Definition

A SEV-3 incident represents **partial functionality issues** affecting a subset of users or non-critical features, typically with workarounds available.

### 5.2 Qualifying Conditions

| Condition | Example |
|-----------|---------|
| **Partial Feature Issue** | Some leave types not displaying correctly |
| **Limited User Impact** | Single team/small group affected |
| **Workaround Available** | Issue can be bypassed |
| **Performance Degradation** | Slower than normal but usable |
| **Reporting Issues** | Non-critical reports failing |
| **UI Glitches** | Functional but display issues |

### 5.3 SLA Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| **Response Time** | 4 hours | 8 hours |
| **Initial Assessment** | 8 hours | 1 business day |
| **Resolution Target** | 3 business days | 5 business days |
| **Update Frequency** | Daily | Daily |
| **Escalation** | If no progress in 2 days | 3 days |

### 5.4 Response Requirements

| Requirement | Details |
|-------------|---------|
| **Ticket Priority** | High priority in queue |
| **Assignment** | Within 4 hours |
| **Workaround** | Document and communicate |
| **User Notification** | Update affected users |
| **PIR** | Optional (recommended if recurring) |

### 5.5 Communication Cadence

| Time | Communication |
|------|---------------|
| T+0 | Ticket created |
| T+4h | Acknowledgment to user |
| Daily | Status update to requester |
| Resolution | Resolution notification |

---

## 6. SEV-4 – Low

### 6.1 Definition

A SEV-4 incident represents **minor issues** with minimal business impact, including cosmetic defects, enhancement requests, or documentation gaps.

### 6.2 Qualifying Conditions

| Condition | Example |
|-----------|---------|
| **Cosmetic Issues** | Typos, alignment problems |
| **Minor UI Bugs** | Non-critical display issues |
| **Enhancement Requests** | Feature improvements |
| **Documentation Gaps** | Help text unclear |
| **Training Questions** | How-to requests |
| **Single User Non-Critical** | Individual preference issues |

### 6.3 SLA Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| **Response Time** | 1 business day | 2 business days |
| **Initial Assessment** | 3 business days | 5 business days |
| **Resolution Target** | Next release | Next release + 1 |
| **Update Frequency** | Weekly | Bi-weekly |
| **Escalation** | Not applicable | N/A |

### 6.4 Response Requirements

| Requirement | Details |
|-------------|---------|
| **Ticket Priority** | Standard priority |
| **Assignment** | Queue-based |
| **Backlog** | Added to product backlog if enhancement |
| **User Notification** | Acknowledgment only |
| **PIR** | Not required |

---

## 7. Severity Classification Matrix

### 7.1 Impact vs Urgency Matrix

|                    | **Urgency: Critical** | **Urgency: High** | **Urgency: Medium** | **Urgency: Low** |
|--------------------|----------------------|-------------------|---------------------|------------------|
| **Impact: Critical** | SEV-1 | SEV-1 | SEV-2 | SEV-2 |
| **Impact: High** | SEV-1 | SEV-2 | SEV-2 | SEV-3 |
| **Impact: Medium** | SEV-2 | SEV-2 | SEV-3 | SEV-3 |
| **Impact: Low** | SEV-2 | SEV-3 | SEV-3 | SEV-4 |

### 7.2 Impact Criteria

| Impact Level | Criteria |
|--------------|----------|
| **Critical** | All users affected, business stopped, data at risk |
| **High** | Large user group (>100), core process blocked |
| **Medium** | Department affected (10-100), workaround available |
| **Low** | Individual users (<10), cosmetic/enhancement |

### 7.3 Urgency Criteria

| Urgency Level | Criteria |
|---------------|----------|
| **Critical** | Immediate (payroll, compliance, security) |
| **High** | Today (time-sensitive business process) |
| **Medium** | This week (important but not time-critical) |
| **Low** | Next release (can wait, improvement) |

---

## 8. SLA Summary Table

### 8.1 Complete SLA Matrix

| Severity | Response | Assessment | Resolution | Updates | Escalation | PIR |
|----------|----------|------------|------------|---------|------------|-----|
| **SEV-1** | 15 min | 30 min | 4h (8h max) | 30 min | 1h | Required |
| **SEV-2** | 30 min | 1h | 8h (24h max) | 1h | 4h | Required |
| **SEV-3** | 4h | 8h | 3 days | Daily | 2 days | Optional |
| **SEV-4** | 1 day | 3 days | Next release | Weekly | N/A | No |

### 8.2 Business Hours Definition

| Term | Definition |
|------|------------|
| **Business Hours** | Monday-Friday, 08:00-18:00 local time |
| **Business Day** | Any day business hours apply |
| **24/7** | SEV-1 and SEV-2 are monitored 24/7 |
| **Holiday Coverage** | Reduced staff, on-call available |

---

## 9. Specific Scenario Classifications

### 9.1 Leave Processing Scenarios

| Scenario | Severity | Rationale |
|----------|----------|-----------|
| Cannot submit any leave request | SEV-1 | Core function unavailable |
| Specific leave type not working | SEV-2 | Partial function impact |
| Leave balance shows incorrectly | SEV-2 | Data accuracy issue |
| Calendar display wrong | SEV-3 | UI issue, workaround exists |
| Leave history slow to load | SEV-3 | Performance but functional |
| Minor date format issue | SEV-4 | Cosmetic |

### 9.2 Approval Workflow Scenarios

| Scenario | Severity | Rationale |
|----------|----------|-----------|
| No approvals processing | SEV-1 | Complete workflow failure |
| Wrong approver assigned | SEV-2 | Process integrity issue |
| Notification not sent | SEV-2 | User impact, process delay |
| Approval button slow | SEV-3 | Functional but degraded |
| Approval history formatting | SEV-4 | Cosmetic |

### 9.3 Integration Scenarios

| Scenario | Severity | Rationale |
|----------|----------|-----------|
| Payroll feed completely failed | SEV-1 | Business-critical integration |
| HRIS sync stopped | SEV-2 | Major integration issue |
| Partial sync failure | SEV-2 | Data accuracy impact |
| Sync delayed (< 4 hours) | SEV-3 | Acceptable delay |
| Audit log sync delay | SEV-3 | Non-critical delay |

### 9.4 Security Scenarios

| Scenario | Severity | Rationale |
|----------|----------|-----------|
| Confirmed data breach | SEV-1 | Security incident |
| Unauthorized access detected | SEV-1 | Security incident |
| Authentication failure (all) | SEV-1 | Complete outage |
| Permission error (subset) | SEV-2 | Access control issue |
| Session timeout too short | SEV-3 | User inconvenience |
| Password policy question | SEV-4 | Configuration request |

---

## 10. SLA Exceptions

### 10.1 Exception Conditions

| Condition | SLA Impact |
|-----------|------------|
| **Force Majeure** | SLA suspended |
| **Vendor Dependency** | SLA extended by vendor response time |
| **Change Freeze** | Resolution may be deferred |
| **Third-Party Outage** | SLA adjusted per dependency |

### 10.2 Exception Approval

| Exception Type | Approver |
|----------------|----------|
| SLA pause | Service Delivery Manager |
| Severity downgrade | Incident Manager |
| Resolution extension | IT Director |
| PIR waiver | IT Director |

---

## 11. SLA Reporting

### 11.1 Metrics Tracked

| Metric | Definition | Target |
|--------|------------|--------|
| **Response SLA %** | % incidents responded within SLA | > 95% |
| **Resolution SLA %** | % incidents resolved within SLA | > 90% |
| **MTTR** | Mean Time to Resolve | By severity |
| **Escalation Rate** | % incidents escalated | < 20% |
| **Reopen Rate** | % incidents reopened | < 5% |

### 11.2 Reporting Cadence

| Report | Frequency | Audience |
|--------|-----------|----------|
| SLA Dashboard | Real-time | Operations |
| Weekly Summary | Weekly | IT Management |
| Monthly Report | Monthly | IT Leadership |
| Quarterly Review | Quarterly | Executive |

---

## 12. Severity Change Process

### 12.1 Upgrade Criteria

| From | To | Criteria |
|------|----|----------|
| SEV-4 | SEV-3 | Impact increased, workaround failed |
| SEV-3 | SEV-2 | More users affected, business impact |
| SEV-2 | SEV-1 | Complete failure, security breach |

### 12.2 Downgrade Criteria

| From | To | Criteria |
|------|----|----------|
| SEV-1 | SEV-2 | Partial restoration, workaround in place |
| SEV-2 | SEV-3 | Impact reduced, most users restored |
| SEV-3 | SEV-4 | Minimal impact remains |

### 12.3 Change Authority

| Change | Authority |
|--------|-----------|
| Upgrade to SEV-1 | Any support tier |
| Downgrade from SEV-1 | Incident Manager |
| Any other change | Tier 2+ with documentation |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Operations Team | Initial version |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LMS INCIDENT SLA QUICK REFERENCE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SEV-1 CRITICAL         SEV-2 HIGH            SEV-3 MEDIUM    SEV-4 LOW   │
│  ══════════════         ════════════          ════════════    ═════════   │
│  Response: 15 min       Response: 30 min      Response: 4h    Response: 1d│
│  Resolve:  4 hours      Resolve:  8 hours     Resolve:  3 days Resolve: NR│
│  Updates:  30 min       Updates:  1 hour      Updates:  Daily  Updates: Wk│
│  PIR:      Required     PIR:      Required    PIR:      Opt    PIR:     No │
│                                                                             │
│  Examples:              Examples:             Examples:        Examples:   │
│  • System down          • Core feature broken • Partial issue  • Cosmetic  │
│  • Security breach      • Large group hit     • Workaround OK  • Minor bug │
│  • Payroll impact       • Integration fail    • Performance    • Enhance   │
│                                                                             │
│  Contact: 24/7          Contact: 24/7         Contact: Biz Hrs Contact: Tkt│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
