# LMS Frontend - Phase 28: Defect Management Process

**Document Version:** 1.0  
**Date:** December 20, 2025  
**Status:** ACTIVE

---

## Table of Contents

1. [Overview](#1-overview)
2. [Severity Classification](#2-severity-classification)
3. [Defect Lifecycle](#3-defect-lifecycle)
4. [Triage Process](#4-triage-process)
5. [SLAs and Timelines](#5-slas-and-timelines)
6. [Retest and Closure](#6-retest-and-closure)
7. [Reporting](#7-reporting)

---

## 1. Overview

### 1.1 Purpose

This document defines the defect management process for UAT, ensuring:
- Consistent defect classification
- Efficient triage and resolution
- Clear accountability
- Timely communication
- Proper closure verification

### 1.2 Scope

Applies to all defects discovered during UAT execution, including:
- Functional defects
- UI/UX issues
- Performance concerns
- Data accuracy problems
- Security/access issues
- Integration failures

### 1.3 Tools

| Purpose | Tool | Access |
|---------|------|--------|
| Defect Tracking | JIRA / Azure DevOps | [URL TBD] |
| Evidence Storage | SharePoint / Shared Drive | [Path TBD] |
| Communication | Microsoft Teams | UAT Channel |

---

## 2. Severity Classification

### 2.1 Severity Definitions

#### Critical (S1)

**Definition:** System unusable or major business function completely broken with no workaround available.

**Examples:**
- Cannot log in to application
- Cannot submit any leave request
- Complete data loss or corruption
- Security vulnerability (unauthorized access)
- System crash or unrecoverable error

**Business Impact:** Operations halted, immediate escalation required

**Sign-off Impact:** ❌ **BLOCKS SIGN-OFF** - Must be resolved

---

#### High (S2)

**Definition:** Major feature significantly impaired, but workaround exists or impacts limited user set.

**Examples:**
- Cannot approve leave requests (but can reject)
- Report generates with missing data
- Cannot withdraw pending leave
- Incorrect balance calculation
- Notification not delivered

**Business Impact:** Significant disruption to key workflows

**Sign-off Impact:** ❌ **BLOCKS SIGN-OFF** - Must be resolved

---

#### Medium (S3)

**Definition:** Feature partially working or minor workflow impediment with acceptable workaround.

**Examples:**
- Filter not working correctly (but manual search works)
- Calendar display issues (but dates visible)
- Export format issues (but data accurate)
- UI alignment problems affecting usability
- Slow performance (but functional)

**Business Impact:** Inconvenience, reduced efficiency

**Sign-off Impact:** ⚠️ **May proceed with business acceptance** - Workaround documented

---

#### Low (S4)

**Definition:** Cosmetic issue, minor inconvenience, or enhancement request with no workaround needed.

**Examples:**
- Typo in UI text
- Color/styling inconsistency
- Minor alignment issues
- Enhancement suggestions
- Documentation improvements

**Business Impact:** Minimal or none

**Sign-off Impact:** ✅ **Does not block sign-off** - Can defer to post-go-live

---

### 2.2 Severity Matrix

| Impact ↓ / Frequency → | Affects All Users | Affects Some Users | Affects Few Users |
|------------------------|-------------------|--------------------|--------------------|
| **Cannot perform task** | Critical | High | High |
| **Task difficult** | High | Medium | Medium |
| **Minor inconvenience** | Medium | Low | Low |

### 2.3 Priority vs. Severity

| Term | Definition | Who Assigns |
|------|------------|-------------|
| **Severity** | Technical impact of defect | UAT Coordinator / Triage |
| **Priority** | Order of fix based on business need | IT Owner / Business Owner |

Example: A typo on the home page (Low severity) might be High priority if it contains incorrect legal text.

---

## 3. Defect Lifecycle

### 3.1 Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DEFECT LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐              │
│  │  NEW   │───▶│TRIAGED │───▶│IN PROG │───▶│ FIXED  │              │
│  │        │    │        │    │        │    │        │              │
│  └────────┘    └────┬───┘    └────────┘    └────┬───┘              │
│       │             │                           │                   │
│       │        ┌────▼───┐                  ┌────▼───┐              │
│       │        │REJECTED│                  │RETEST  │              │
│       │        │        │                  │        │              │
│       │        └────────┘                  └────┬───┘              │
│       │                                         │                   │
│       │                          ┌──────────────┼──────────────┐   │
│       │                          │              │              │   │
│       │                     ┌────▼───┐    ┌────▼───┐    ┌─────▼──┐│
│       │                     │REOPENED│    │ CLOSED │    │DEFERRED││
│       │                     │        │    │        │    │        ││
│       │                     └────┬───┘    └────────┘    └────────┘│
│       │                          │                                 │
│       └──────────────────────────┘                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Status Definitions

| Status | Description | Owner |
|--------|-------------|-------|
| **NEW** | Defect logged, awaiting triage | Tester |
| **TRIAGED** | Severity confirmed, assigned to dev | UAT Coordinator |
| **IN PROGRESS** | Developer working on fix | Developer |
| **FIXED** | Fix complete, ready for retest | Developer |
| **RETEST** | Retest in progress | Tester |
| **CLOSED** | Verified fixed, defect resolved | Tester |
| **REOPENED** | Retest failed, issue persists | Tester |
| **REJECTED** | Not a defect, working as designed | UAT Coordinator |
| **DEFERRED** | Accepted for post-go-live | Business Owner |

### 3.3 Defect Template

```
══════════════════════════════════════════════════════════════
                    DEFECT REPORT
══════════════════════════════════════════════════════════════

DEFECT ID: DEF-XXXX
TITLE: [Brief descriptive title]

──────────────────────────────────────────────────────────────
CLASSIFICATION
──────────────────────────────────────────────────────────────
Severity: [Critical / High / Medium / Low]
Priority: [To be assigned at triage]
Category: [Functional / UI / Data / Performance / Security / Integration]

──────────────────────────────────────────────────────────────
CONTEXT
──────────────────────────────────────────────────────────────
UAT Scenario: [Scenario ID, e.g., EMP-001]
Environment: UAT (https://uat.lms.company.com)
Build Version: [From build-manifest.json]
Browser/Device: [e.g., Chrome 120 / Windows 11]
Test Account: [Account used]
Date/Time: [When defect occurred]
Reported By: [Tester name]

──────────────────────────────────────────────────────────────
DESCRIPTION
──────────────────────────────────────────────────────────────
Steps to Reproduce:
1. [Login as...]
2. [Navigate to...]
3. [Click on...]
4. [Enter...]
5. [Click Submit]

Expected Result:
[What should happen according to requirements/scenario]

Actual Result:
[What actually happened]

──────────────────────────────────────────────────────────────
EVIDENCE
──────────────────────────────────────────────────────────────
Screenshots: [Attached: screenshot1.png, screenshot2.png]
Video: [If applicable]
Logs: [Console errors, network logs if captured]
Export: [Any exported data showing issue]

──────────────────────────────────────────────────────────────
ADDITIONAL INFORMATION
──────────────────────────────────────────────────────────────
Workaround Available: [Yes/No - describe if yes]
Frequency: [Always / Intermittent / Once]
Related Defects: [Link to related issues if any]
Notes: [Any other relevant information]

══════════════════════════════════════════════════════════════
```

---

## 4. Triage Process

### 4.1 Triage Meeting

| Aspect | Detail |
|--------|--------|
| Frequency | Daily at 14:00 during execution phase |
| Duration | 60 minutes maximum |
| Attendees | UAT Coordinator, IT Owner, Dev Lead |
| Optional | Business Owner (for severity disputes) |

### 4.2 Triage Agenda

1. **Review NEW defects** (30 min)
   - Validate defect quality
   - Confirm/adjust severity
   - Assign to developer
   - Set target fix date

2. **Review FIXED defects** (15 min)
   - Confirm fix deployment to UAT
   - Assign retest to tester
   - Set retest deadline

3. **Review REOPENED defects** (10 min)
   - Understand retest failure
   - Re-prioritize if needed

4. **Discuss DEFERRED candidates** (5 min)
   - Business Owner approval required
   - Document workaround
   - Schedule post-go-live

### 4.3 Triage Decisions

| Decision | Authority | Criteria |
|----------|-----------|----------|
| Confirm severity | UAT Coordinator | Based on definitions |
| Change severity | IT Owner + Business Owner | Business impact assessment |
| Assign developer | IT Owner | Technical expertise |
| Defer defect | Business Owner | Risk acceptance |
| Reject defect | UAT Coordinator + IT Owner | Working as designed |

### 4.4 Triage Outcomes

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIAGE DECISION TREE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Is it a valid defect?                                       │
│        │                                                     │
│        ├── NO ──▶ REJECTED (document reason)                │
│        │                                                     │
│        └── YES                                               │
│             │                                                │
│             ▼                                                │
│  What is the severity?                                       │
│        │                                                     │
│        ├── Critical ──▶ Immediate fix, daily retest         │
│        │                                                     │
│        ├── High ──▶ Fix within 24 hours                     │
│        │                                                     │
│        ├── Medium ──▶ Fix if time permits OR                │
│        │              Defer with workaround                  │
│        │                                                     │
│        └── Low ──▶ Defer to post-go-live                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. SLAs and Timelines

### 5.1 Fix SLAs by Severity

| Severity | Target Fix Time | Escalation Trigger |
|----------|-----------------|-------------------|
| Critical | 4 hours | 2 hours without progress |
| High | 24 hours | 12 hours without progress |
| Medium | 48 hours | 24 hours without progress |
| Low | Best effort / Defer | N/A |

### 5.2 Response SLAs

| Action | SLA |
|--------|-----|
| Defect acknowledgment | 2 hours |
| Triage completion | Next triage meeting (≤24 hours) |
| Developer assignment | At triage |
| Fix deployment to UAT | Within 2 hours of fix complete |
| Retest assignment | At next triage after fix |
| Retest completion | 4 hours for Critical, 8 hours for others |

### 5.3 Timeline Example

```
Critical Defect Timeline:
──────────────────────────────────────────────────────────────
Hour 0:   Defect logged by tester
Hour 1:   Acknowledged by UAT Coordinator
Hour 2:   Emergency triage (severity confirmed Critical)
Hour 2:   Assigned to developer
Hour 4-6: Fix developed and tested
Hour 7:   Fix deployed to UAT
Hour 8:   Retest by original tester
Hour 9:   CLOSED (or REOPENED if failed)
──────────────────────────────────────────────────────────────

High Defect Timeline:
──────────────────────────────────────────────────────────────
Day 1 AM: Defect logged
Day 1 PM: Triage (14:00) - severity confirmed, assigned
Day 1-2:  Fix developed
Day 2 PM: Fix deployed to UAT
Day 2 PM: Retest assigned at triage
Day 3:    Retest completed, CLOSED
──────────────────────────────────────────────────────────────
```

### 5.4 Escalation Path

| Level | Trigger | Escalate To | Action |
|-------|---------|-------------|--------|
| 1 | SLA at 50% | IT Owner | Awareness |
| 2 | SLA at 75% | IT Owner + Business Owner | Resource review |
| 3 | SLA breached | Business Owner + Executive | Mitigation decision |

---

## 6. Retest and Closure

### 6.1 Retest Prerequisites

Before a defect can be retested:

| Prerequisite | Verified By |
|--------------|-------------|
| Fix deployed to UAT | Developer confirms |
| Build version updated | UAT Coordinator verifies |
| Deployment notification sent | Developer |
| Original data conditions available | Tester confirms |

### 6.2 Retest Procedure

1. **Receive retest assignment**
   - Check defect for fix details
   - Note build version with fix

2. **Verify UAT environment**
   - Confirm build version matches
   - Clear browser cache if needed

3. **Execute original steps**
   - Follow exact reproduction steps
   - Use same test data conditions

4. **Verify fix**
   - Does expected behavior now occur?
   - Any regression in related areas?

5. **Document retest result**
   - Screenshots of successful outcome
   - Or evidence of continued failure

6. **Update defect status**
   - CLOSED if verified fixed
   - REOPENED if issue persists (with new evidence)

### 6.3 Retest Outcomes

| Outcome | Action | Next Step |
|---------|--------|-----------|
| **Verified Fixed** | Status → CLOSED | Close with evidence |
| **Partially Fixed** | Status → REOPENED | Document remaining issue |
| **Not Fixed** | Status → REOPENED | Return to developer |
| **New Issue Found** | Log NEW defect | Link to original |

### 6.4 Closure Criteria

A defect can be closed when:

| Criteria | Verification |
|----------|--------------|
| Retest passed | Tester confirms expected behavior |
| Evidence captured | Screenshot of correct behavior |
| No regression | Related functionality unaffected |
| Original scenario passes | UAT scenario now passes |

### 6.5 Closure Documentation

```
DEFECT CLOSURE RECORD
══════════════════════════════════════════════════════════════

Defect ID: DEF-XXXX
Closure Date: YYYY-MM-DD
Closed By: [Tester name]

Fix Build Version: [Build containing fix]
Retest Date: YYYY-MM-DD

Retest Result: PASSED

Evidence:
- Screenshot: retest_passed.png
- Related scenario now passes: [Scenario ID]

Notes:
[Any additional observations]

══════════════════════════════════════════════════════════════
```

---

## 7. Reporting

### 7.1 Daily Defect Summary

Included in daily UAT status report:

```
╔══════════════════════════════════════════════════════════════╗
║                    DEFECT STATUS SUMMARY                      ║
║                       Date: YYYY-MM-DD                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  NEW TODAY         │  CLOSED TODAY     │  TOTAL OPEN         ║
║  Critical: 0       │  Critical: 1      │  Critical: 0        ║
║  High:     1       │  High:     2      │  High:     1        ║
║  Medium:   2       │  Medium:   1      │  Medium:   4        ║
║  Low:      1       │  Low:      0      │  Low:      3        ║
║  ──────────        │  ──────────       │  ──────────         ║
║  Total:    4       │  Total:    4      │  Total:    8        ║
║                                                               ║
╠══════════════════════════════════════════════════════════════╣
║  DEFECTS BY STATUS                                            ║
║  ─────────────────                                            ║
║  New:         2  ▓▓                                           ║
║  Triaged:     1  ▓                                            ║
║  In Progress: 3  ▓▓▓                                          ║
║  Fixed:       2  ▓▓                                           ║
║  Retest:      2  ▓▓                                           ║
║  Closed:     12  ▓▓▓▓▓▓▓▓▓▓▓▓                                ║
║  Deferred:    1  ▓                                            ║
║                                                               ║
╠══════════════════════════════════════════════════════════════╣
║  SIGN-OFF BLOCKERS                                            ║
║  ─────────────────                                            ║
║  Open Critical/High: 1                                        ║
║                                                               ║
║  DEF-0015 (High): Manager cannot view team calendar           ║
║    Status: In Progress | ETA: Tomorrow AM                     ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

### 7.2 Defect Aging Report

| Age | Critical | High | Medium | Low |
|-----|----------|------|--------|-----|
| < 1 day | 0 | 1 | 2 | 1 |
| 1-2 days | 0 | 0 | 2 | 2 |
| 3-5 days | 0 | 0 | 0 | 0 |
| > 5 days | 0 | 0 | 0 | 0 |

### 7.3 Final Defect Report

Prepared for sign-off meeting:

```
══════════════════════════════════════════════════════════════
              UAT FINAL DEFECT REPORT
              Date: YYYY-MM-DD
══════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY
─────────────────
Total Defects Found:    XX
Total Defects Closed:   XX
Open Defects:           XX
Deferred Defects:       XX

DEFECT RESOLUTION BY SEVERITY
─────────────────────────────
                Found    Closed    Open    Deferred
Critical:         X        X        0         0
High:             X        X        0         0
Medium:           X        X        X         X
Low:              X        X        X         X

SIGN-OFF READINESS
──────────────────
☑ Critical defects: 0 open (PASS)
☑ High defects:     0 open (PASS)
☑ Medium defects:   X open with workaround (ACCEPTABLE)
☑ Low defects:      X deferred (ACCEPTABLE)

DEFERRED DEFECTS (Require Business Approval)
────────────────────────────────────────────
ID        Severity    Description                Workaround
DEF-XXX   Medium      [Brief description]        [Workaround]
DEF-XXX   Low         [Brief description]        N/A

RECOMMENDATION
──────────────
☑ System is ready for production deployment
☐ System requires additional defect resolution

══════════════════════════════════════════════════════════════
```

---

## Appendix: Quick Reference

### Defect Severity at a Glance

| Severity | Icon | Blocks Sign-off? | Fix SLA |
|----------|------|------------------|---------|
| Critical | 🔴 | YES | 4 hours |
| High | 🟠 | YES | 24 hours |
| Medium | 🟡 | With acceptance | 48 hours |
| Low | 🟢 | NO | Best effort |

### Status Flow Quick Reference

```
NEW → TRIAGED → IN PROGRESS → FIXED → RETEST → CLOSED
                    ↓                     ↓
                REJECTED               REOPENED
                    ↓                     ↓
                 (end)              (back to dev)
```

---

*This document is part of the LMS Phase 28 UAT Program.*
