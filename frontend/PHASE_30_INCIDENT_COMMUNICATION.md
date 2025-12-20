# Phase 30.4 – Incident Communication Templates

## Leave Management System (LMS) – Stakeholder Communication Standards

| **Document ID** | LMS-PHASE30-COMMS-001 |
|-----------------|------------------------|
| **Version**     | 1.0                    |
| **Last Updated**| December 20, 2025      |
| **Status**      | ACTIVE                 |
| **Classification** | Internal            |

---

## 1. Communication Overview

### 1.1 Communication Principles

| Principle | Description |
|-----------|-------------|
| **Timely** | Communicate within SLA-defined windows |
| **Accurate** | Only communicate verified information |
| **Clear** | Use plain language, avoid jargon |
| **Consistent** | Same message across all channels |
| **Actionable** | Include what users should do |

### 1.2 Communication Channels

| Channel | Use Case | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|---------|----------|-------|-------|-------|-------|
| **Status Page** | Public status | ✅ | ✅ | ⚪ | ❌ |
| **Email** | Stakeholder notification | ✅ | ✅ | ✅ | ⚪ |
| **Teams/Slack** | Internal updates | ✅ | ✅ | ✅ | ✅ |
| **Bridge/Phone** | Real-time coordination | ✅ | ⚪ | ❌ | ❌ |
| **SMS** | Critical alerts | ✅ | ⚪ | ❌ | ❌ |
| **Ticket Update** | User updates | ✅ | ✅ | ✅ | ✅ |

---

## 2. Communication Ownership

### 2.1 RACI Matrix

| Communication | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|---------------|-------|-------|-------|-------|
| Initial notification | Incident Lead | Incident Lead | Support | Support |
| Status updates | Incident Lead | Tier 2/3 Lead | Assigned owner | Assigned owner |
| Executive communication | IT Director | Incident Lead | N/A | N/A |
| Resolution notification | Incident Lead | Incident Lead | Support | Support |
| Post-incident summary | Incident Lead | Incident Lead | N/A | N/A |

### 2.2 Approval Requirements

| Communication Type | Approval Required |
|-------------------|-------------------|
| Status page update | Incident Lead |
| External email | Incident Lead + Manager |
| Executive update | IT Director |
| Press/media | Communications + Legal |
| Regulatory notification | Compliance + Legal |

---

## 3. Communication Timing

### 3.1 Timing by Severity

| Severity | Initial Notice | Updates | Resolution |
|----------|---------------|---------|------------|
| SEV-1 | Within 15 min | Every 30 min | Immediately |
| SEV-2 | Within 30 min | Every 1 hour | Within 1 hour |
| SEV-3 | Within 4 hours | Daily | Within 4 hours |
| SEV-4 | Within 1 day | Weekly | Per ticket |

### 3.2 Update Schedule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SEV-1 COMMUNICATION TIMELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

T+0        T+15m      T+30m      T+1h       Every 30m    Resolution
 │           │          │          │           │            │
 ▼           ▼          ▼          ▼           ▼            ▼
┌────┐    ┌────┐    ┌────┐    ┌────┐     ┌────────┐    ┌────┐
│INC │    │Init│    │Upd │    │Exec│     │Ongoing │    │Res │
│DET │    │NOT │    │#1  │    │NOT │     │Updates │    │NOT │
└────┘    └────┘    └────┘    └────┘     └────────┘    └────┘
  │          │         │         │           │            │
  │          │         │         │           │            ▼
  │          │         │         │           │        ┌────────┐
  │          │         │         │           │        │PIR in  │
  │          │         │         │           │        │5 days  │
  │          │         │         │           │        └────────┘
```

---

## 4. Initial Notification Templates

### 4.1 SEV-1 Initial Notification

**Channel:** Email + Status Page + Teams + SMS (executives)

**Subject:** 🔴 [SEV-1] LMS Production Incident – [Brief Description]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 SEVERITY 1 INCIDENT NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         INVESTIGATING
SEVERITY:       SEV-1 (CRITICAL)
STARTED:        [DATE TIME TIMEZONE]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ISSUE:
[Clear, non-technical description of what is happening]

IMPACT:
• Who is affected: [All users / Specific groups]
• What is affected: [Specific functionality]
• Business impact: [Description]

CURRENT ACTIONS:
• Our team has been engaged and is actively investigating
• [Specific action being taken]

NEXT UPDATE:
[TIME] or within 30 minutes

INCIDENT BRIDGE:
[Dial-in / Teams link] (for internal responders only)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For urgent inquiries: [Emergency contact]
Track status: status.company.com/lms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4.2 SEV-2 Initial Notification

**Channel:** Email + Status Page + Teams

**Subject:** 🟠 [SEV-2] LMS Incident – [Brief Description]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠 SEVERITY 2 INCIDENT NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         INVESTIGATING
SEVERITY:       SEV-2 (HIGH)
STARTED:        [DATE TIME TIMEZONE]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ISSUE:
[Clear description of the issue]

IMPACT:
• Affected users: [Description of who is affected]
• Affected functionality: [What isn't working]

WORKAROUND:
[If available, describe workaround. If none: "No workaround currently available"]

CURRENT ACTIONS:
• Our team is investigating the issue
• [Specific actions]

NEXT UPDATE:
[TIME] or within 1 hour

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For questions: lms-support@company.com
Track status: status.company.com/lms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4.3 SEV-3 Initial Notification

**Channel:** Email + Ticket

**Subject:** 🟡 [SEV-3] LMS Issue Under Investigation – [Brief Description]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 SERVICE ISSUE NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TICKET ID:      [TICKET NUMBER]
STATUS:         UNDER INVESTIGATION
PRIORITY:       MEDIUM
REPORTED:       [DATE TIME]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ISSUE:
[Description of the issue]

IMPACT:
[Who and what is affected]

WORKAROUND:
[Describe workaround if available]

EXPECTED RESOLUTION:
Within [X] business days

NEXT UPDATE:
[DATE] or sooner if resolved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For questions: lms-support@company.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Status Update Templates

### 5.1 SEV-1 Status Update

**Subject:** 🔴 [SEV-1] LMS Incident Update #[N] – [Brief Status]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 INCIDENT STATUS UPDATE #[NUMBER]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         [INVESTIGATING / IDENTIFIED / MONITORING / RESOLVED]
SEVERITY:       SEV-1 (CRITICAL)
DURATION:       [X hours Y minutes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT STATUS:
[1-2 sentence summary of current state]

PROGRESS SINCE LAST UPDATE:
• [Action taken]
• [Finding or result]
• [Next step]

ROOT CAUSE:
[If identified: brief description]
[If not: "Under investigation"]

ESTIMATED RESOLUTION:
[Time estimate if available, or "Continuing to work toward resolution"]

NEXT UPDATE:
[TIME] or within 30 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Incident Bridge: [Details]
Status Page: status.company.com/lms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5.2 SEV-2 Status Update

**Subject:** 🟠 [SEV-2] LMS Incident Update #[N] – [Brief Status]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠 INCIDENT STATUS UPDATE #[NUMBER]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         [STATUS]
DURATION:       [X hours Y minutes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT STATUS:
[Summary of current state]

PROGRESS:
• [Actions taken]
• [Findings]

WORKAROUND:
[If now available]

NEXT STEPS:
• [What's being done next]

NEXT UPDATE:
[TIME] or within 1 hour

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Resolution Templates

### 6.1 SEV-1 Resolution Notification

**Subject:** ✅ [RESOLVED] LMS Incident INC-[NUMBER] – Service Restored

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ INCIDENT RESOLVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         RESOLVED
RESOLVED AT:    [DATE TIME TIMEZONE]
TOTAL DURATION: [X hours Y minutes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESOLUTION SUMMARY:
The Leave Management System has been restored to full operational 
status. All functionality is now available.

WHAT HAPPENED:
[Brief, user-friendly explanation of what occurred]

WHAT WE DID:
[Brief description of resolution steps]

ROOT CAUSE:
[Brief root cause - technical details in PIR]

IMPACT SUMMARY:
• Duration: [X hours Y minutes]
• Users affected: [Scope]
• Data impact: [None / Description]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:
• Post-Incident Review scheduled for [DATE]
• Full report will be shared within 5 business days
• Preventive measures will be implemented

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We apologize for any inconvenience this incident may have caused.
If you experience any issues, please contact lms-support@company.com.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6.2 SEV-2 Resolution Notification

**Subject:** ✅ [RESOLVED] LMS Issue INC-[NUMBER]

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ISSUE RESOLVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT ID:    INC-[NUMBER]
STATUS:         RESOLVED
RESOLVED AT:    [DATE TIME]
DURATION:       [X hours Y minutes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESOLUTION:
[Description of what was fixed]

ROOT CAUSE:
[Brief explanation]

IMPACT:
• Duration: [Time]
• Affected: [Scope]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:
• Monitoring for recurrence
• Post-Incident Review within 10 business days

For questions: lms-support@company.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Post-Incident Summary Templates

### 7.1 Executive Summary (24-48 hours post-incident)

**Subject:** [PIR] LMS Incident INC-[NUMBER] – Executive Summary

---

**EMAIL TEMPLATE:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST-INCIDENT EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT:       INC-[NUMBER]
DATE:           [DATE]
SEVERITY:       SEV-[X]
DURATION:       [X hours Y minutes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTIVE SUMMARY:
[2-3 sentence summary of what happened and resolution]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPACT:
┌────────────────────┬──────────────────────────────────────┐
│ Duration           │ [X hours Y minutes]                  │
│ Users Affected     │ [Number/scope]                       │
│ Business Impact    │ [Description]                        │
│ Data Impact        │ [None/Description]                   │
│ Financial Impact   │ [If applicable]                      │
└────────────────────┴──────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROOT CAUSE:
[One paragraph explaining the root cause in business terms]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY ACTIONS:
1. [Immediate fix applied]
2. [Short-term improvement planned]
3. [Long-term prevention measure]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:
• Full PIR review meeting: [DATE]
• Detailed report available: [DATE]
• Action items tracked in: [SYSTEM/TICKET]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 8. Internal Communication Templates

### 8.1 War Room Announcement

**Channel:** #lms-incidents or Bridge

```
🚨 WAR ROOM ACTIVATED - INC-[NUMBER]

Severity: SEV-[X]
Issue: [Brief description]

Bridge: [Dial-in / Teams link]
Incident Lead: [Name]

Required responders:
• DevOps: [Name]
• Engineering: [Name]
• DBA: [Name]

Please join immediately.
```

---

### 8.2 Status Page Updates

**Investigating:**
```
[Component]: Investigating Issue
We are investigating reports of [brief description]. 
More updates to follow.
```

**Identified:**
```
[Component]: Issue Identified
We have identified the cause of the issue affecting [description]. 
Our team is working on a fix.
```

**Monitoring:**
```
[Component]: Fix Implemented - Monitoring
A fix has been implemented. We are monitoring the results.
```

**Resolved:**
```
[Component]: Resolved
This incident has been resolved. All services are operating normally.
```

---

### 8.3 Handoff Communication

**Template for shift/tier handoff:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCIDENT HANDOFF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT:       INC-[NUMBER]
HANDING OFF:    [Name] → [Name]
TIME:           [TIMESTAMP]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT STATUS:
[Description of current state]

ACTIONS TAKEN:
• [Action 1]
• [Action 2]

PENDING ACTIONS:
• [What needs to happen next]

KEY CONTACTS:
• [Who has been involved]

NOTES:
[Any important context]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 9. Stakeholder-Specific Templates

### 9.1 HR Department Notification

**Subject:** LMS System Status – Action May Be Required

```
Dear HR Team,

This is to inform you of a current issue with the Leave Management System.

ISSUE: [Brief description]

IMPACT TO HR OPERATIONS:
• [Specific impact - e.g., leave approvals, reports]
• [What can/cannot be done]

RECOMMENDED ACTIONS:
• [What HR should do or avoid doing]

We will keep you updated on progress.

For urgent leave processing needs, contact: [Emergency contact]
```

---

### 9.2 Payroll Team Notification

**Subject:** 🔴 URGENT: LMS Payroll Feed Status

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAYROLL INTEGRATION ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS:         [Status]
FEED AFFECTED:  [Feed name]
PAYROLL CYCLE:  [Current/Next cycle]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ISSUE:
[Description of integration issue]

IMPACT TO PAYROLL:
• [Specific impact]
• [Data availability status]

CONTINGENCY:
[Manual process available / Alternative approach]

RESOLUTION ETA:
[Time estimate]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Contact for urgent issues: [Name] [Phone]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 10. Communication Don'ts

### 10.1 What NOT to Communicate

| ❌ Don't | ✅ Instead |
|----------|-----------|
| Speculate on cause | "We are investigating" |
| Blame individuals | Focus on facts and resolution |
| Use technical jargon | Plain language |
| Over-promise timeline | Realistic estimates |
| Communicate unverified info | Wait for confirmation |
| Different messages to different groups | Consistent messaging |
| Skip security review for breach comms | Always get approval |

### 10.2 Communication Review Checklist

Before sending any incident communication:

- [ ] Information is verified/confirmed
- [ ] Language is clear and professional
- [ ] No blame or finger-pointing
- [ ] Appropriate level of detail for audience
- [ ] Action items are clear (if any)
- [ ] Next update time is specified
- [ ] Contact information included
- [ ] Approved by appropriate authority

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Operations Team | Initial version |
