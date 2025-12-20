# Phase 30.1 – Support Model & Ownership

## Leave Management System (LMS) – Production Support Structure

| **Document ID** | LMS-PHASE30-SUPPORT-001 |
|-----------------|--------------------------|
| **Version**     | 1.0                      |
| **Last Updated**| December 20, 2025        |
| **Status**      | ACTIVE                   |
| **Classification** | Internal              |

---

## 1. Executive Summary

This document defines the tiered support model for the Leave Management System (LMS) in production. It establishes clear ownership, responsibilities, handoff criteria, and escalation paths to ensure predictable, auditable, and effective production support.

---

## 2. Support Model Overview

### 2.1 Tiered Support Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LMS SUPPORT MODEL                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   END USERS     │
                              └────────┬────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1 - SERVICE DESK                                                      │
│  First Contact | Triage | FAQs | Ticket Creation                           │
│  Response: < 15 min | Owner: Service Desk Team                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                          (Functional/Data Issues)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2 - APPLICATION SUPPORT                                               │
│  Functional Issues | Data Validation | Configuration                        │
│  Response: < 1 hour | Owner: Application Support Team                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                          (Code/Infrastructure Issues)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3 - ENGINEERING                                                       │
│  Code Defects | Performance | Security | Infrastructure                     │
│  Response: Per Severity | Owner: Engineering Team                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                              (Critical/Executive)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 4 - EXECUTIVE / VENDOR                                                │
│  Major Incidents | Strategic Decisions | Vendor Escalation                  │
│  Response: Immediate | Owner: IT Leadership / Vendors                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tier 1 – Service Desk

### 3.1 Overview

| Attribute | Details |
|-----------|---------|
| **Team** | IT Service Desk |
| **Hours** | 24/7 (follow-the-sun) or Business Hours |
| **Primary Contact** | Help Desk Portal / Phone / Email |
| **Response Target** | < 15 minutes |

### 3.2 Responsibilities

| # | Responsibility | Description |
|---|----------------|-------------|
| 1 | **First Contact** | Receive all incoming user requests and issues |
| 2 | **Ticket Creation** | Log all issues in ticketing system with required fields |
| 3 | **Initial Triage** | Categorize and prioritize based on impact/urgency |
| 4 | **FAQ Resolution** | Resolve common issues using knowledge base |
| 5 | **Password/Access** | Handle password resets, basic access issues |
| 6 | **Status Updates** | Keep users informed of ticket progress |
| 7 | **Escalation** | Escalate unresolved issues to Tier 2 |

### 3.3 Scope – What Tier 1 Handles

| ✅ In Scope | ❌ Out of Scope |
|-------------|-----------------|
| Password resets | Code changes |
| Account unlocks | Database modifications |
| Navigation assistance | Configuration changes |
| FAQ/Known issue guidance | Performance tuning |
| Basic leave request help | Security incidents |
| Ticket logging & routing | Integration troubleshooting |

### 3.4 Resolution Targets

| Issue Type | Target Resolution | Escalate If |
|------------|-------------------|-------------|
| Password reset | 15 minutes | System-level issue |
| Navigation help | 15 minutes | Application defect |
| Known issue (documented) | 30 minutes | No workaround |
| General inquiry | 4 hours | Requires investigation |

### 3.5 Required Ticket Information

| Field | Required | Description |
|-------|----------|-------------|
| User ID | ✅ | Affected user's employee ID |
| Contact Info | ✅ | Email and phone |
| Issue Description | ✅ | Detailed description |
| Steps to Reproduce | ✅ | How to replicate |
| Error Message | ✅ | Exact error text/screenshot |
| Impact | ✅ | Who/what is affected |
| Urgency | ✅ | Business urgency |
| Browser/Device | ⚪ | If UI-related |
| Timestamp | ✅ | When issue occurred |

### 3.6 Team Structure

| Role | Name | Contact | Shift |
|------|------|---------|-------|
| Service Desk Manager | [TBD] | [Email/Phone] | Business Hours |
| Service Desk Analyst | [TBD] | [Email/Phone] | Morning Shift |
| Service Desk Analyst | [TBD] | [Email/Phone] | Afternoon Shift |
| Service Desk Analyst | [TBD] | [Email/Phone] | Evening Shift |

---

## 4. Tier 2 – Application Support

### 4.1 Overview

| Attribute | Details |
|-----------|---------|
| **Team** | LMS Application Support |
| **Hours** | Business Hours + On-Call |
| **Primary Contact** | Escalation from Tier 1 |
| **Response Target** | < 1 hour (business hours) |

### 4.2 Responsibilities

| # | Responsibility | Description |
|---|----------------|-------------|
| 1 | **Functional Analysis** | Investigate functional issues in depth |
| 2 | **Data Validation** | Verify data integrity, reconciliation |
| 3 | **Configuration** | Adjust non-code configurations |
| 4 | **Workflow Issues** | Resolve approval/workflow problems |
| 5 | **Report Issues** | Address reporting discrepancies |
| 6 | **User Training** | Provide advanced user guidance |
| 7 | **Integration Monitoring** | Monitor HRIS/Payroll sync status |
| 8 | **Escalation** | Escalate code/infrastructure issues to Tier 3 |

### 4.3 Scope – What Tier 2 Handles

| ✅ In Scope | ❌ Out of Scope |
|-------------|-----------------|
| Leave balance discrepancies | Code bug fixes |
| Workflow routing issues | Database schema changes |
| Report generation problems | Infrastructure changes |
| User permission adjustments | Security vulnerability fixes |
| Configuration parameter changes | Performance optimization |
| Data correction (with approval) | Third-party vendor issues |
| Integration status checks | Architectural changes |

### 4.4 Resolution Targets

| Issue Type | Target Resolution | Escalate If |
|------------|-------------------|-------------|
| Balance discrepancy | 4 hours | Data corruption suspected |
| Workflow issue | 4 hours | Code defect identified |
| Configuration change | 8 hours | Requires code change |
| Report issue | 1 business day | Requires development |
| Integration status | 2 hours | System connectivity issue |

### 4.5 Data Correction Authority

| Correction Type | Authority | Approval Required |
|-----------------|-----------|-------------------|
| Single user balance | Tier 2 | Manager approval |
| Bulk balance adjustment | Tier 2 Lead | Director approval |
| Historical data | Tier 3 | Compliance approval |
| Audit-sensitive data | Prohibited | Never at Tier 2 |

### 4.6 Team Structure

| Role | Name | Contact | Responsibilities |
|------|------|---------|------------------|
| Application Support Lead | [TBD] | [Email/Phone] | Team coordination, escalations |
| Application Support Analyst | [TBD] | [Email/Phone] | Functional issues |
| Application Support Analyst | [TBD] | [Email/Phone] | Data/reporting issues |
| Business Analyst | [TBD] | [Email/Phone] | Business rule clarification |

### 4.7 On-Call Rotation

| Week | Primary | Secondary | Contact |
|------|---------|-----------|---------|
| Week 1 | [Name] | [Name] | [Phone] |
| Week 2 | [Name] | [Name] | [Phone] |
| Week 3 | [Name] | [Name] | [Phone] |
| Week 4 | [Name] | [Name] | [Phone] |

---

## 5. Tier 3 – Engineering

### 5.1 Overview

| Attribute | Details |
|-----------|---------|
| **Team** | LMS Engineering Team |
| **Hours** | Business Hours + On-Call |
| **Primary Contact** | Escalation from Tier 2 or Direct (SEV-1) |
| **Response Target** | Per severity (see SLA matrix) |

### 5.2 Responsibilities

| # | Responsibility | Description |
|---|----------------|-------------|
| 1 | **Code Defect Resolution** | Fix application bugs |
| 2 | **Performance Issues** | Diagnose and resolve performance problems |
| 3 | **Security Incidents** | Respond to security vulnerabilities |
| 4 | **Infrastructure Issues** | Address infrastructure-related problems |
| 5 | **Integration Failures** | Fix HRIS/Payroll integration issues |
| 6 | **Database Issues** | Resolve database corruption/performance |
| 7 | **Hotfix Deployment** | Deploy emergency fixes |
| 8 | **Root Cause Analysis** | Perform technical RCA |

### 5.3 Sub-Teams

| Sub-Team | Focus Area | Lead |
|----------|------------|------|
| **Backend Engineering** | API, business logic, database | [TBD] |
| **Frontend Engineering** | UI, UX, browser issues | [TBD] |
| **DevOps/SRE** | Infrastructure, deployment, monitoring | [TBD] |
| **Security** | Security incidents, vulnerability management | [TBD] |
| **DBA** | Database performance, data integrity | [TBD] |

### 5.4 Scope – What Tier 3 Handles

| ✅ In Scope | ❌ Out of Scope |
|-------------|-----------------|
| Application code defects | Business process decisions |
| API/Integration failures | Policy/rule clarifications |
| Database issues | User training |
| Performance optimization | Configuration changes (Tier 2) |
| Security vulnerabilities | Vendor product issues |
| Infrastructure problems | Feature enhancements (backlog) |
| Emergency deployments | |

### 5.5 Resolution Targets (by Severity)

| Severity | Response | Resolution Target | Update Frequency |
|----------|----------|-------------------|------------------|
| SEV-1 | 15 min | 4 hours | Every 30 min |
| SEV-2 | 30 min | 8 hours | Every 1 hour |
| SEV-3 | 4 hours | 3 business days | Daily |
| SEV-4 | 1 business day | Next release | Weekly |

### 5.6 Team Structure

| Role | Name | Contact | Focus |
|------|------|---------|-------|
| Engineering Manager | [TBD] | [Email/Phone] | Overall coordination |
| Senior Backend Engineer | [TBD] | [Email/Phone] | API/Backend issues |
| Senior Frontend Engineer | [TBD] | [Email/Phone] | UI issues |
| DevOps/SRE Lead | [TBD] | [Email/Phone] | Infrastructure |
| DBA | [TBD] | [Email/Phone] | Database |
| Security Engineer | [TBD] | [Email/Phone] | Security incidents |

### 5.7 On-Call Rotation

| Role | Week 1 | Week 2 | Week 3 | Week 4 |
|------|--------|--------|--------|--------|
| Primary Engineer | [Name] | [Name] | [Name] | [Name] |
| Secondary Engineer | [Name] | [Name] | [Name] | [Name] |
| DevOps On-Call | [Name] | [Name] | [Name] | [Name] |
| DBA On-Call | [Name] | [Name] | [Name] | [Name] |

---

## 6. Tier 4 – Executive / Vendor

### 6.1 Overview

| Attribute | Details |
|-----------|---------|
| **Engagement** | SEV-1 incidents, major decisions, vendor issues |
| **Authority** | Executive decision-making, budget, vendor SLAs |
| **Response** | Immediate for SEV-1 |

### 6.2 When to Engage

| Scenario | Contact |
|----------|---------|
| SEV-1 incident > 1 hour unresolved | IT Director |
| Business-critical decision needed | Business Owner |
| Vendor escalation required | Vendor Manager |
| Security breach | CISO |
| Compliance/legal issue | Compliance Officer |
| Budget approval for emergency | IT Director / CFO |

### 6.3 Executive Contacts

| Role | Name | Contact | When to Engage |
|------|------|---------|----------------|
| IT Director | [TBD] | [Phone] | Major incidents, escalations |
| Business Owner | [TBD] | [Phone] | Business decisions |
| CISO | [TBD] | [Phone] | Security incidents |
| Compliance Officer | [TBD] | [Phone] | Audit/compliance issues |
| Vendor Manager | [TBD] | [Phone] | Third-party issues |

---

## 7. Escalation Matrix

### 7.1 Escalation Criteria

| From | To | Criteria |
|------|----|----------|
| Tier 1 → Tier 2 | Functional issue, data problem, configuration needed |
| Tier 2 → Tier 3 | Code defect, infrastructure issue, security concern |
| Tier 3 → Tier 4 | SEV-1 unresolved, executive decision needed, vendor issue |
| Any → Tier 4 | SEV-1 immediate, security breach, compliance risk |

### 7.2 Escalation Time Limits

| Tier | Max Time Before Escalation | Condition |
|------|----------------------------|-----------|
| Tier 1 | 30 minutes | Cannot resolve, functional issue |
| Tier 2 | 2 hours | Code/infrastructure suspected |
| Tier 3 (SEV-1) | 1 hour | No progress, need executive |
| Tier 3 (SEV-2) | 4 hours | No progress |

### 7.3 Escalation Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ESCALATION DECISION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │ Issue Reported  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Tier 1 Triage   │
                    │ (< 15 min)      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Resolved │  │ Tier 2   │  │ SEV-1    │
        │ (FAQ)    │  │ Needed   │  │ Direct   │
        └──────────┘  └────┬─────┘  └────┬─────┘
                           │             │
                           ▼             │
                    ┌──────────────┐     │
                    │ Tier 2       │     │
                    │ Investigation│     │
                    │ (< 2 hours)  │     │
                    └──────┬───────┘     │
                           │             │
              ┌────────────┼─────────────┤
              │            │             │
              ▼            ▼             ▼
        ┌──────────┐ ┌──────────┐  ┌──────────┐
        │ Resolved │ │ Tier 3   │  │ Tier 3   │
        │          │ │ Needed   │  │ URGENT   │
        └──────────┘ └────┬─────┘  └────┬─────┘
                          │             │
                          ▼             ▼
                    ┌───────────────────────┐
                    │ Tier 3 Engineering    │
                    │ (Per SLA)             │
                    └───────────┬───────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Resolved │ │ Ongoing  │ │ Tier 4   │
              │          │ │ Work     │ │ Escalate │
              └──────────┘ └──────────┘ └──────────┘
```

---

## 8. Handoff Procedures

### 8.1 Tier 1 → Tier 2 Handoff

**Trigger:** Issue requires functional investigation or configuration change

**Handoff Checklist:**
| # | Item | Required |
|---|------|----------|
| 1 | Ticket fully documented | ✅ |
| 2 | User impact stated | ✅ |
| 3 | Steps to reproduce | ✅ |
| 4 | Screenshots/error messages | ✅ |
| 5 | Initial troubleshooting done | ✅ |
| 6 | User notified of escalation | ✅ |

### 8.2 Tier 2 → Tier 3 Handoff

**Trigger:** Code defect, infrastructure issue, or security concern identified

**Handoff Checklist:**
| # | Item | Required |
|---|------|----------|
| 1 | Root cause hypothesis | ✅ |
| 2 | Technical evidence (logs, traces) | ✅ |
| 3 | Business impact quantified | ✅ |
| 4 | Workaround status | ✅ |
| 5 | Severity confirmed | ✅ |
| 6 | Stakeholders informed | ✅ |

### 8.3 Shift Handoff

**Required for 24/7 Coverage:**

| Item | Description |
|------|-------------|
| Open tickets | List of all open issues with status |
| Active incidents | Any ongoing SEV-1/SEV-2 |
| Pending actions | What needs follow-up |
| Escalations | Any pending escalations |
| Key contacts | Who to reach for ongoing issues |

---

## 9. Support Tools & Access

### 9.1 Required Tools

| Tool | Purpose | Tier Access |
|------|---------|-------------|
| ServiceNow/Jira | Ticketing | All tiers |
| Knowledge Base | FAQ/Troubleshooting | All tiers |
| LMS Admin Console | User management | Tier 1, 2 |
| Application Logs | Log analysis | Tier 2, 3 |
| APM (Datadog/etc.) | Performance monitoring | Tier 2, 3 |
| Database Client | Data queries | Tier 2 (read), Tier 3 |
| CI/CD Pipeline | Deployment | Tier 3 |
| Source Code | Code review | Tier 3 |
| PagerDuty | On-call alerts | Tier 2, 3 |

### 9.2 Access Provisioning

| Role | Access Request | Approval |
|------|----------------|----------|
| Tier 1 | ServiceNow, KB, LMS Admin (limited) | Service Desk Manager |
| Tier 2 | + Logs, APM, Database (read) | App Support Lead |
| Tier 3 | + Full database, CI/CD, Code | Engineering Manager |

---

## 10. Performance Expectations

### 10.1 Tier Metrics

| Tier | Metric | Target |
|------|--------|--------|
| **Tier 1** | First Response Time | < 15 min |
| **Tier 1** | First Contact Resolution | > 40% |
| **Tier 1** | Escalation Accuracy | > 95% |
| **Tier 2** | Response Time | < 1 hour |
| **Tier 2** | Resolution Rate | > 70% |
| **Tier 2** | Escalation Accuracy | > 98% |
| **Tier 3** | SEV-1 Response | < 15 min |
| **Tier 3** | SEV-1 Resolution | < 4 hours |
| **Tier 3** | Change Success Rate | > 99% |

### 10.2 Quality Standards

| Standard | Requirement |
|----------|-------------|
| Ticket documentation | Complete per checklist |
| Knowledge updates | Document new issues within 24h |
| Handoff quality | No ping-pong escalations |
| User communication | Updates per SLA |
| PIR participation | Mandatory for SEV-1/2 |

---

## 11. Training Requirements

### 11.1 Tier 1 Training

| Topic | Duration | Frequency |
|-------|----------|-----------|
| LMS Application Overview | 4 hours | Onboarding |
| Ticketing System | 2 hours | Onboarding |
| Common Issues & FAQ | 4 hours | Onboarding |
| Escalation Procedures | 2 hours | Onboarding |
| Refresher Training | 2 hours | Quarterly |

### 11.2 Tier 2 Training

| Topic | Duration | Frequency |
|-------|----------|-----------|
| LMS Deep Dive | 8 hours | Onboarding |
| Data Model & Workflows | 4 hours | Onboarding |
| Configuration Management | 4 hours | Onboarding |
| Troubleshooting Techniques | 4 hours | Onboarding |
| Integration Overview | 4 hours | Onboarding |
| Advanced Training | 4 hours | Quarterly |

### 11.3 Tier 3 Training

| Topic | Duration | Frequency |
|-------|----------|-----------|
| Architecture Deep Dive | 8 hours | Onboarding |
| Codebase Walkthrough | 8 hours | Onboarding |
| Incident Response | 4 hours | Onboarding |
| Security Training | 4 hours | Annual |
| On-Call Procedures | 2 hours | Onboarding |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Operations Team | Initial version |

---

## Appendix A: Contact Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│              LMS SUPPORT CONTACT CARD                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📞 SERVICE DESK (Tier 1)                                       │
│     Phone: [NUMBER]                                             │
│     Email: lms-support@company.com                              │
│     Portal: support.company.com                                 │
│                                                                 │
│  🔧 APP SUPPORT ON-CALL (Tier 2)                               │
│     Phone: [NUMBER]                                             │
│     PagerDuty: lms-appsupport                                   │
│                                                                 │
│  ⚙️ ENGINEERING ON-CALL (Tier 3)                               │
│     Phone: [NUMBER]                                             │
│     PagerDuty: lms-engineering                                  │
│                                                                 │
│  🚨 SEV-1 BRIDGE                                                │
│     Dial-in: [NUMBER]                                           │
│     Teams: #lms-incidents                                       │
│                                                                 │
│  📊 STATUS PAGE                                                 │
│     status.company.com/lms                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
