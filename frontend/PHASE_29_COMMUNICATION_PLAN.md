# Phase 29.4 – Communication Plan

## Leave Management System (LMS) – Go-Live Communications

| **Document ID** | LMS-PHASE29-COMMS-001 |
|-----------------|------------------------|
| **Version**     | 1.0                    |
| **Last Updated**| December 20, 2025      |
| **Status**      | ACTIVE                 |
| **Classification** | Internal           |

---

## 1. Communication Strategy Overview

### 1.1 Objectives

- Ensure all stakeholders are informed at appropriate times
- Minimize confusion and support requests
- Maintain transparency throughout the deployment
- Enable rapid response to issues
- Document all communications for audit trail

### 1.2 Communication Principles

| Principle | Description |
|-----------|-------------|
| **Proactive** | Communicate before stakeholders need to ask |
| **Clear** | Use simple, jargon-free language |
| **Timely** | Right information at the right time |
| **Accurate** | Only communicate verified information |
| **Consistent** | Same message across all channels |

---

## 2. Stakeholder Groups

### 2.1 Stakeholder Matrix

| Group | Description | Communication Need | Priority |
|-------|-------------|-------------------|----------|
| **Executive** | C-suite, VP-level | High-level status, risks | High |
| **Business Owners** | HR, Department heads | Functional updates, impact | High |
| **IT Operations** | Infrastructure, Support | Technical details, procedures | Critical |
| **End Users** | All LMS users | What's changing, when, how | High |
| **Support Team** | Help desk, Support analysts | Detailed changes, FAQs | Critical |
| **Vendors/Partners** | Integration partners | Integration changes | Medium |

### 2.2 Contact Lists

#### Executive Stakeholders
| Name | Title | Email | Phone |
|------|-------|-------|-------|
| [Name] | CIO | | |
| [Name] | VP HR | | |
| [Name] | VP IT | | |

#### Business Owners
| Name | Department | Email | Phone |
|------|------------|-------|-------|
| [Name] | Human Resources | | |
| [Name] | Finance | | |
| [Name] | Operations | | |

#### IT Operations
| Name | Role | Email | Phone |
|------|------|-------|-------|
| [Name] | IT Director | | |
| [Name] | Infrastructure Lead | | |
| [Name] | Support Manager | | |

---

## 3. Communication Channels

### 3.1 Channel Matrix

| Channel | Use Case | Audience | Response Time |
|---------|----------|----------|---------------|
| **Email** | Formal announcements, documentation | All stakeholders | N/A |
| **Teams/Slack** | Real-time updates, war room | IT, Project team | Immediate |
| **Status Page** | Public status updates | All users | Automatic |
| **Phone/Bridge** | Critical escalations, war room | Leadership, IT | Immediate |
| **Ticketing System** | Issue tracking, support | Support, IT | Per SLA |
| **Intranet** | User guides, FAQs | End users | N/A |

### 3.2 Channel Details

| Channel | Platform | Access |
|---------|----------|--------|
| War Room | Microsoft Teams | #lms-golive-war-room |
| Incident Channel | Microsoft Teams | #lms-incidents |
| Status Page | StatusPage.io | status.company.com |
| Email Distribution | Exchange | lms-stakeholders@company.com |
| Bridge Line | Conference | [Dial-in details] |

---

## 4. Communication Timeline

### 4.1 Pre-Go-Live Communications

| Timing | Communication | Audience | Channel | Owner |
|--------|---------------|----------|---------|-------|
| T-14 days | Go-live schedule announcement | All stakeholders | Email | PM |
| T-7 days | User preparation guide | End users | Email, Intranet | Training |
| T-5 days | Technical freeze notification | IT teams | Email, Teams | DevOps |
| T-3 days | Support team briefing | Support | Meeting | Support Lead |
| T-2 days | Final reminder | All stakeholders | Email | PM |
| T-1 day | Go/No-Go decision announcement | All stakeholders | Email | Release Mgr |
| T-4 hours | Deployment starting notification | IT teams | Teams, Email | Release Mgr |

### 4.2 During Go-Live Communications

| Timing | Communication | Audience | Channel | Owner |
|--------|---------------|----------|---------|-------|
| T+0 | Deployment started | IT teams | Teams | Release Mgr |
| Every 15 min | Status update | War room | Teams | DevOps |
| On completion | Deployment complete | All | Email, Teams | Release Mgr |
| If issues | Issue notification | IT, Business | Teams, Phone | Release Mgr |
| If rollback | Rollback notification | All | Email, Teams | Release Mgr |

### 4.3 Post-Go-Live Communications

| Timing | Communication | Audience | Channel | Owner |
|--------|---------------|----------|---------|-------|
| T+1 hour | Go-live confirmation | All stakeholders | Email | PM |
| T+1 day | Day-1 status report | Leadership | Email | Release Mgr |
| T+7 days | Week-1 summary | All stakeholders | Email | PM |
| T+14 days | Hypercare exit report | Leadership | Email | PM |

---

## 5. Communication Templates

### 5.1 Template: Go-Live Announcement (T-14 days)

**Subject:** [LMS] Production Go-Live Scheduled – [DATE]

---

Dear Team,

We are pleased to announce that the Leave Management System (LMS) will go live on **[DATE]**.

**What's Happening:**
- The new Leave Management System will be deployed to production
- This replaces [previous system/process]
- New features include: [brief list]

**Timeline:**
- **Go-Live Date:** [DATE]
- **Deployment Window:** [TIME] - [TIME] [TIMEZONE]
- **Expected Impact:** Minimal (deployment during off-peak hours)

**What You Need to Do:**
1. Review the updated user guide: [LINK]
2. Complete the training module by [DATE]: [LINK]
3. Save any in-progress work before [DATE/TIME]

**Support:**
- For questions before go-live: [email/channel]
- For issues after go-live: [support contact]

**More Information:**
- User Guide: [LINK]
- FAQ: [LINK]
- Training Materials: [LINK]

Thank you for your cooperation during this transition.

Best regards,
[Project Manager Name]
LMS Project Team

---

### 5.2 Template: Deployment Start Notification

**Subject:** [LMS] 🚀 Production Deployment Starting NOW

---

**DEPLOYMENT NOTIFICATION**

**Status:** DEPLOYMENT IN PROGRESS
**Start Time:** [TIMESTAMP]
**Expected Duration:** [X] hours

**What's Happening:**
The LMS production deployment has begun. Our team is executing the planned cutover.

**Current Phase:** [Phase name]

**Impact:**
- [Expected user impact, if any]
- [Any features temporarily unavailable]

**Next Update:** [TIME]

**War Room:** [Teams channel / Bridge line]

**Do NOT:**
- Attempt to use the system during deployment
- Create support tickets for known deployment activities

We will notify you when deployment is complete.

---
Release Management Team

---

### 5.3 Template: Deployment Complete – Success

**Subject:** [LMS] ✅ Production Go-Live SUCCESSFUL

---

Dear Team,

**GREAT NEWS!** The Leave Management System has been successfully deployed to production.

**Deployment Summary:**
- **Status:** ✅ SUCCESSFUL
- **Completion Time:** [TIMESTAMP]
- **Version:** [VERSION NUMBER]
- **Duration:** [X hours Y minutes]

**What This Means:**
- The new LMS is now live and operational
- All features are available for use
- You can access the system at: [URL]

**What You Can Do Now:**
1. Log in to the new system: [URL]
2. Verify your leave balances
3. Report any issues to: [support contact]

**Known Limitations:**
- [Any known issues/limitations]

**Support:**
- Help Desk: [phone/email]
- Self-Service FAQ: [LINK]
- Support Hours: [extended hours if applicable]

**Hypercare Period:**
Enhanced support will be available for the next [X] days. Our team is actively monitoring the system.

Thank you for your patience during this deployment!

Best regards,
[Project Manager Name]
LMS Project Team

---

### 5.4 Template: Rollback Notification

**Subject:** [LMS] ⚠️ Production Deployment Rolled Back

---

**IMPORTANT NOTIFICATION**

**Status:** DEPLOYMENT ROLLED BACK
**Time:** [TIMESTAMP]

**What Happened:**
During the LMS production deployment, [brief non-technical explanation] was detected. As a precautionary measure, we have reverted to the previous system version.

**Current Status:**
- The system is **OPERATIONAL** on the previous version
- All your data is **SAFE**
- Normal functionality is **AVAILABLE**

**Impact:**
- New features are not yet available
- [Any other relevant impact]

**What You Need to Do:**
- No action required
- Continue using the system normally
- Report any issues to [support]

**Next Steps:**
- Our team is investigating the issue
- A revised deployment schedule will be communicated
- Expected update by: [DATE/TIME]

**Support:**
If you experience any issues, please contact:
- Help Desk: [phone/email]
- Emergency: [phone]

We apologize for any inconvenience and thank you for your understanding.

Best regards,
[Release Manager Name]
Release Management Team

---

### 5.5 Template: Incident Notification

**Subject:** [LMS] 🔴 Service Incident – [SEVERITY]

---

**INCIDENT NOTIFICATION**

**Incident ID:** [INC-XXXX]
**Severity:** [P1/P2/P3]
**Status:** [INVESTIGATING/IDENTIFIED/MONITORING/RESOLVED]
**Start Time:** [TIMESTAMP]

**Issue:**
[Brief description of the issue]

**Impact:**
- Affected functionality: [description]
- Affected users: [scope]
- Business impact: [description]

**Current Actions:**
- [What the team is doing]
- [Expected resolution time if known]

**Workaround:**
[If available, describe workaround]

**Next Update:** [TIME]

**Incident Bridge:** [Bridge details if P1]

**Do NOT:**
- Flood the help desk with duplicate tickets
- Attempt workarounds not provided in this communication

---
Incident Management Team

---

### 5.6 Template: Incident Resolved

**Subject:** [LMS] ✅ Service Incident RESOLVED – [INC-XXXX]

---

**INCIDENT RESOLVED**

**Incident ID:** [INC-XXXX]
**Resolution Time:** [TIMESTAMP]
**Total Duration:** [X hours Y minutes]

**Issue:**
[Brief description]

**Resolution:**
[What was done to fix it]

**Root Cause:**
[Brief root cause - if known]

**Impact Summary:**
- Duration: [time]
- Users affected: [count/scope]
- [Any data impact]

**Preventive Measures:**
[What will be done to prevent recurrence]

**Post-Incident Review:**
A full review will be conducted and shared by [DATE].

Thank you for your patience during this incident.

---
Incident Management Team

---

### 5.7 Template: War Room Status Update

**Posted to:** #lms-golive-war-room

---

```
📊 STATUS UPDATE - [TIME]

Phase: [Current phase]
Progress: [X of Y steps complete]

✅ Completed:
- [Step 1]
- [Step 2]

🔄 In Progress:
- [Current step] - ETA: [time]

⏳ Upcoming:
- [Next step]

📈 Metrics:
- Error rate: [X]%
- Response time: [X]ms
- Active users: [X]

🚦 Status: [GREEN/YELLOW/RED]

Next update: [TIME]
```

---

### 5.8 Template: Daily Hypercare Status

**Subject:** [LMS] Daily Hypercare Status – Day [X]

---

**HYPERCARE STATUS REPORT**

**Date:** [DATE]
**Day:** [X] of [Y] Hypercare Period

**System Status:** 🟢 OPERATIONAL

**Key Metrics (24h):**
| Metric | Value | Trend |
|--------|-------|-------|
| Uptime | 99.9% | ✅ |
| Avg Response Time | 120ms | ✅ |
| Error Rate | 0.1% | ✅ |
| Active Users | 1,234 | ↑ |
| Support Tickets | 15 | ↓ |

**Issues Today:**
| Ticket | Issue | Status |
|--------|-------|--------|
| [#] | [Brief] | [Status] |

**Resolved Issues:**
- [List of resolved issues]

**User Feedback:**
- [Summary of feedback received]

**Tomorrow's Focus:**
- [Key activities planned]

**Escalations:**
- [Any escalated items]

---
Hypercare Team

---

## 6. Communication Ownership

### 6.1 RACI Matrix

| Communication | Responsible | Accountable | Consulted | Informed |
|---------------|-------------|-------------|-----------|----------|
| Go-live announcement | PM | Release Mgr | Business Owner | All |
| Technical updates | DevOps | Release Mgr | Dev Lead | IT Teams |
| User communications | Training | PM | HR | Users |
| Incident notifications | Incident Mgr | Release Mgr | DevOps | All |
| Executive updates | PM | Release Mgr | CIO | Executives |
| Support briefings | Support Lead | PM | QA | Support Team |

### 6.2 Approval Requirements

| Communication Type | Approver | Lead Time |
|-------------------|----------|-----------|
| User-facing announcements | Business Owner | 2 days |
| Technical notifications | Release Manager | 1 day |
| Incident communications | Incident Manager | Immediate |
| Executive communications | PM + Release Manager | 1 day |
| Press/External | Communications + Legal | 5 days |

---

## 7. Escalation Communication

### 7.1 Escalation Triggers

| Trigger | Communication Action |
|---------|---------------------|
| P1 Incident | Immediate phone + Teams to all stakeholders |
| Deployment delay > 1 hour | Email to business owners |
| Rollback initiated | Immediate notification to all |
| Data issue suspected | Escalate to executive level |
| Security incident | Security team + Legal notification |

### 7.2 Escalation Contact Matrix

| Severity | First Contact | Escalation 1 | Escalation 2 |
|----------|---------------|--------------|--------------|
| P1 - Critical | Release Manager | CIO | CEO |
| P2 - High | DevOps Lead | IT Director | CIO |
| P3 - Medium | Support Lead | Release Manager | IT Director |
| P4 - Low | Help Desk | Support Lead | - |

---

## 8. Communication Don'ts

### 8.1 What NOT to Communicate

| ❌ Don't | ✅ Instead |
|----------|-----------|
| Speculate on root cause | State facts, promise investigation |
| Blame individuals/teams | Focus on resolution |
| Over-promise timelines | Give realistic estimates with buffer |
| Use technical jargon with users | Use clear, simple language |
| Send conflicting messages | Coordinate through single source |
| Communicate unverified info | Verify before sending |

### 8.2 Communication Blackout

During active deployment (war room open):
- All external communications go through Release Manager
- No individual updates to stakeholders
- Status page is single source of truth for users
- War room is single source for IT

---

## 9. Post-Communication Audit

### 9.1 Communication Log

All communications must be logged:

| Field | Required |
|-------|----------|
| Timestamp | ✅ |
| Communication type | ✅ |
| Sender | ✅ |
| Recipients | ✅ |
| Channel | ✅ |
| Content summary | ✅ |
| Attachments | If applicable |

### 9.2 Communication Archive

All go-live communications must be archived in:
- SharePoint: [location]
- Ticketing system: Linked to deployment ticket
- Email archive: Retained per policy

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Release Team | Initial version |
