# Phase 30.5 – Post-Incident Review (PIR) Process

## Leave Management System (LMS) – Root Cause Analysis & Continuous Learning

| **Document ID** | LMS-PHASE30-PIR-001 |
|-----------------|----------------------|
| **Version**     | 1.0                  |
| **Last Updated**| December 20, 2025    |
| **Status**      | ACTIVE               |
| **Classification** | Internal          |

---

## 1. Purpose

Post-Incident Reviews (PIRs) are mandatory processes to understand what happened, why it happened, and how to prevent recurrence. This document establishes the PIR framework for the Leave Management System.

### 1.1 PIR Objectives

- **Understand** the complete incident timeline
- **Identify** root cause(s) – technical and process
- **Assess** impact accurately
- **Define** corrective and preventive actions
- **Share** learnings across the organization
- **Maintain** audit-ready documentation

---

## 2. PIR Requirements

### 2.1 When PIR is Required

| Severity | PIR Required | Timeline |
|----------|--------------|----------|
| SEV-1 | **MANDATORY** | Within 5 business days |
| SEV-2 | **MANDATORY** | Within 10 business days |
| SEV-3 | Recommended | Within 15 business days |
| SEV-4 | Optional | As needed |

### 2.2 Additional PIR Triggers

| Trigger | PIR Required |
|---------|--------------|
| Security incident (any severity) | MANDATORY |
| Data loss or corruption | MANDATORY |
| Compliance/audit impact | MANDATORY |
| Customer escalation | MANDATORY |
| Near-miss (narrowly avoided SEV-1) | Recommended |
| Recurring incident (3+ occurrences) | MANDATORY |

---

## 3. PIR Process

### 3.1 Process Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PIR PROCESS FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  Day 0-1              Day 1-3              Day 3-5              Day 5-7
     │                    │                    │                    │
     ▼                    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│ RESOLVE │────────▶│ COLLECT │────────▶│ ANALYZE │────────▶│ REVIEW  │
│ INCIDENT│         │ DATA    │         │ RCA     │         │ MEETING │
└─────────┘         └─────────┘         └─────────┘         └─────────┘
                                                                  │
                                                                  ▼
                                        ┌─────────┐         ┌─────────┐
                                        │ TRACK   │◀────────│ PUBLISH │
                                        │ ACTIONS │         │ PIR     │
                                        └─────────┘         └─────────┘
                                             │
                                             ▼
                                        ┌─────────┐
                                        │ CLOSE   │
                                        │ LOOP    │
                                        └─────────┘
```

### 3.2 PIR Phases

| Phase | Activities | Owner | Timeline |
|-------|------------|-------|----------|
| **1. Data Collection** | Gather logs, timeline, metrics | Incident Lead | Day 1-2 |
| **2. Timeline Construction** | Build detailed event timeline | Incident Lead | Day 2-3 |
| **3. Root Cause Analysis** | Apply RCA techniques | Technical Lead | Day 3-4 |
| **4. Impact Assessment** | Quantify business impact | Business Analyst | Day 3-4 |
| **5. PIR Meeting** | Review with stakeholders | Incident Lead | Day 4-5 |
| **6. Documentation** | Complete PIR report | Incident Lead | Day 5-7 |
| **7. Action Tracking** | Assign and track actions | Incident Lead | Ongoing |

---

## 4. Data Collection

### 4.1 Required Data

| Category | Data to Collect | Source |
|----------|-----------------|--------|
| **Timeline** | Chronological events | Logs, monitoring, chat |
| **Logs** | Application, system, audit logs | Log aggregator |
| **Metrics** | Performance, error rates, traffic | APM, monitoring |
| **Changes** | Recent deployments, configs | CI/CD, change log |
| **Communications** | Incident notifications, updates | Email, Teams |
| **Actions** | Commands run, decisions made | War room notes |
| **Impact** | Users affected, duration | Monitoring, reports |

### 4.2 Data Collection Checklist

| # | Item | Collected | Location |
|---|------|-----------|----------|
| 1 | Application logs (incident window ±2h) | ☐ | |
| 2 | Infrastructure logs | ☐ | |
| 3 | Monitoring alerts | ☐ | |
| 4 | APM traces/spans | ☐ | |
| 5 | Database query logs | ☐ | |
| 6 | Recent deployment records | ☐ | |
| 7 | Configuration changes | ☐ | |
| 8 | War room/bridge transcript | ☐ | |
| 9 | Incident communications | ☐ | |
| 10 | User reports/tickets | ☐ | |

---

## 5. Root Cause Analysis Techniques

### 5.1 5 Whys Analysis

**Template:**

```
PROBLEM: [State the problem]

Why 1: Why did [problem] occur?
Answer: [Answer]

Why 2: Why did [Answer 1] occur?
Answer: [Answer]

Why 3: Why did [Answer 2] occur?
Answer: [Answer]

Why 4: Why did [Answer 3] occur?
Answer: [Answer]

Why 5: Why did [Answer 4] occur?
Answer: [Answer] ← ROOT CAUSE

VERIFICATION: Does fixing [Root Cause] prevent [Problem]?
```

**Example:**

```
PROBLEM: LMS production outage for 2 hours

Why 1: Why did the outage occur?
Answer: Database connections exhausted

Why 2: Why were connections exhausted?
Answer: Connection leak in new code

Why 3: Why was there a connection leak?
Answer: Code didn't close connections in error path

Why 4: Why wasn't this caught?
Answer: Unit tests didn't cover error scenarios

Why 5: Why didn't tests cover error scenarios?
Answer: Test coverage requirements didn't mandate error paths

ROOT CAUSE: Insufficient test coverage requirements for error handling
```

### 5.2 Fishbone (Ishikawa) Diagram

```
                                    ┌─────────────┐
                                    │   OUTAGE    │
                                    └──────┬──────┘
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        │                                  │                                  │
   ┌────┴────┐                        ┌────┴────┐                        ┌────┴────┐
   │ PEOPLE  │                        │ PROCESS │                        │TECHNOLOGY│
   └────┬────┘                        └────┬────┘                        └────┬────┘
        │                                  │                                  │
    • Training gap                    • Review missed                     • Code defect
    • Fatigue                         • No runbook                        • Config error
    • Communication                   • Inadequate testing                • Infrastructure
        │                                  │                                  │
        └──────────────────────────────────┴──────────────────────────────────┘
```

### 5.3 Contributing Factors Analysis

| Category | Factor | Contribution |
|----------|--------|--------------|
| **Immediate Cause** | What directly caused the incident | [Description] |
| **Contributing Factors** | What allowed it to happen | [List] |
| **Root Cause** | Fundamental reason | [Description] |
| **Systemic Issues** | Organizational/process gaps | [List] |

---

## 6. PIR Meeting

### 6.1 Meeting Structure

| Segment | Duration | Content |
|---------|----------|---------|
| Opening | 5 min | Ground rules, blameless culture reminder |
| Timeline Review | 15 min | Walk through events chronologically |
| Root Cause Discussion | 20 min | Present and discuss RCA findings |
| Impact Review | 10 min | Business impact assessment |
| Action Items | 15 min | Define corrective/preventive actions |
| Lessons Learned | 10 min | Key takeaways, what went well |
| Wrap-up | 5 min | Action ownership, next steps |

### 6.2 Required Attendees

| Role | Responsibility |
|------|----------------|
| Incident Lead | Facilitate, present timeline |
| Technical Lead | Present RCA, technical details |
| Business Representative | Validate impact, business context |
| Operations Lead | Operational perspective |
| QA Representative | Testing/quality perspective |
| Management Sponsor | Ensure action commitment |

### 6.3 Ground Rules

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               PIR GROUND RULES - BLAMELESS CULTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DO:
• Focus on systems and processes, not individuals
• Assume everyone acted with best intentions
• Ask "what" and "how", not "who"
• Share openly and honestly
• Look for systemic improvements
• Document all learnings

❌ DON'T:
• Blame individuals
• Be defensive
• Hide information
• Interrupt others
• Focus only on technical fixes
• Leave without assigned actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. PIR Report Template

### 7.1 Full PIR Document Template

```markdown
═══════════════════════════════════════════════════════════════
              POST-INCIDENT REVIEW REPORT
═══════════════════════════════════════════════════════════════

INCIDENT ID:     INC-[NUMBER]
INCIDENT DATE:   [DATE]
PIR DATE:        [DATE]
SEVERITY:        SEV-[X]
PIR LEAD:        [Name]

═══════════════════════════════════════════════════════════════
                    EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════

[2-3 paragraph summary covering: what happened, impact, root 
cause, and key actions]

═══════════════════════════════════════════════════════════════
                      INCIDENT SUMMARY
═══════════════════════════════════════════════════════════════

Duration:           [X hours Y minutes]
Time to Detect:     [Time from start to detection]
Time to Resolve:    [Time from detection to resolution]
Users Affected:     [Number/scope]
Severity:           SEV-[X]

═══════════════════════════════════════════════════════════════
                         TIMELINE
═══════════════════════════════════════════════════════════════

| Time (UTC) | Event                                      |
|------------|-------------------------------------------|
| HH:MM      | [Event description]                       |
| HH:MM      | [Event description]                       |
| HH:MM      | Incident detected via [method]            |
| HH:MM      | On-call paged                             |
| HH:MM      | War room opened                           |
| HH:MM      | Root cause identified                     |
| HH:MM      | Fix implemented                           |
| HH:MM      | Service restored                          |
| HH:MM      | Incident declared resolved                |

═══════════════════════════════════════════════════════════════
                    ROOT CAUSE ANALYSIS
═══════════════════════════════════════════════════════════════

IMMEDIATE CAUSE:
[What directly caused the incident]

5 WHYS ANALYSIS:
[Include 5 Whys analysis]

ROOT CAUSE:
[Fundamental cause that, if fixed, prevents recurrence]

CONTRIBUTING FACTORS:
1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

═══════════════════════════════════════════════════════════════
                    IMPACT ASSESSMENT
═══════════════════════════════════════════════════════════════

USER IMPACT:
• Users affected: [Number]
• User experience: [Description]
• User actions required: [Any actions users needed to take]

BUSINESS IMPACT:
• Revenue impact: [If applicable]
• Productivity impact: [Hours lost, etc.]
• Compliance impact: [Any regulatory concerns]
• Reputation impact: [Customer satisfaction, etc.]

DATA IMPACT:
• Data loss: [None / Description]
• Data corruption: [None / Description]
• Data exposure: [None / Description]

═══════════════════════════════════════════════════════════════
                    RESPONSE ANALYSIS
═══════════════════════════════════════════════════════════════

WHAT WENT WELL:
• [Positive aspect of response]
• [Positive aspect of response]
• [Positive aspect of response]

WHAT COULD BE IMPROVED:
• [Area for improvement]
• [Area for improvement]
• [Area for improvement]

DETECTION:
• How was incident detected? [Method]
• Could we have detected earlier? [Yes/No - explanation]
• Detection improvement: [Recommendation]

RESPONSE:
• Response time vs SLA: [Met/Missed]
• Escalation effectiveness: [Assessment]
• Communication effectiveness: [Assessment]

═══════════════════════════════════════════════════════════════
                     ACTION ITEMS
═══════════════════════════════════════════════════════════════

IMMEDIATE (This Week):
| # | Action                     | Owner        | Due Date   |
|---|----------------------------|--------------|------------|
| 1 | [Action]                   | [Name]       | [Date]     |
| 2 | [Action]                   | [Name]       | [Date]     |

SHORT-TERM (This Month):
| # | Action                     | Owner        | Due Date   |
|---|----------------------------|--------------|------------|
| 3 | [Action]                   | [Name]       | [Date]     |
| 4 | [Action]                   | [Name]       | [Date]     |

LONG-TERM (This Quarter):
| # | Action                     | Owner        | Due Date   |
|---|----------------------------|--------------|------------|
| 5 | [Action]                   | [Name]       | [Date]     |
| 6 | [Action]                   | [Name]       | [Date]     |

═══════════════════════════════════════════════════════════════
                   LESSONS LEARNED
═══════════════════════════════════════════════════════════════

KEY LEARNINGS:
1. [Learning 1]
2. [Learning 2]
3. [Learning 3]

PROCESS GAPS IDENTIFIED:
1. [Gap 1]
2. [Gap 2]

RECOMMENDATIONS:
1. [Recommendation 1]
2. [Recommendation 2]

═══════════════════════════════════════════════════════════════
                      APPENDICES
═══════════════════════════════════════════════════════════════

APPENDIX A: Detailed Logs
[Link to logs or include relevant excerpts]

APPENDIX B: Monitoring Screenshots
[Include or link to screenshots]

APPENDIX C: Communication Log
[List of communications sent]

═══════════════════════════════════════════════════════════════
                      APPROVAL
═══════════════════════════════════════════════════════════════

Prepared By:     ____________________  Date: __________
Reviewed By:     ____________________  Date: __________
Approved By:     ____________________  Date: __________

═══════════════════════════════════════════════════════════════
```

---

## 8. Action Item Management

### 8.1 Action Item Classification

| Type | Definition | Priority |
|------|------------|----------|
| **Immediate** | Prevents recurrence now | P1 - This week |
| **Short-term** | Reduces likelihood/impact | P2 - This month |
| **Long-term** | Systemic improvement | P3 - This quarter |
| **Process** | Non-technical improvement | Per urgency |

### 8.2 Action Item Template

| Field | Value |
|-------|-------|
| ID | PIR-[INC#]-[Action#] |
| Description | [Clear, actionable description] |
| Category | Technical / Process / Training |
| Owner | [Name] |
| Due Date | [Date] |
| Status | Open / In Progress / Complete / Deferred |
| Verification | [How will completion be verified] |

### 8.3 Action Tracking

```
Action items must be:
• Entered in tracking system within 2 business days of PIR
• Assigned to specific individual (not team)
• Given realistic due date
• Verified upon completion
• Reported in monthly operations review
```

---

## 9. PIR Quality Standards

### 9.1 PIR Completeness Checklist

| # | Element | Required | Present |
|---|---------|----------|---------|
| 1 | Executive summary | ✅ | ☐ |
| 2 | Complete timeline | ✅ | ☐ |
| 3 | Root cause identified | ✅ | ☐ |
| 4 | 5 Whys or equivalent analysis | ✅ | ☐ |
| 5 | Impact quantified | ✅ | ☐ |
| 6 | Detection analysis | ✅ | ☐ |
| 7 | Response analysis | ✅ | ☐ |
| 8 | What went well | ✅ | ☐ |
| 9 | What could improve | ✅ | ☐ |
| 10 | Action items with owners | ✅ | ☐ |
| 11 | Lessons learned | ✅ | ☐ |
| 12 | Approval signatures | ✅ | ☐ |

### 9.2 PIR Review Criteria

| Criterion | Standard |
|-----------|----------|
| Objectivity | Facts-based, not opinion |
| Completeness | All sections filled |
| Actionability | Actions are specific and measurable |
| Blamelessness | No individual blame |
| Timeliness | Completed within deadline |

---

## 10. Audit & Retention

### 10.1 Retention Requirements

| Document | Retention Period | Storage |
|----------|------------------|---------|
| PIR Report | 7 years | Document management system |
| Supporting data | 3 years | Archive storage |
| Action tracking | Until closed + 2 years | Ticketing system |
| Meeting minutes | 7 years | Document management system |

### 10.2 Audit Access

| Requestor | Access Level |
|-----------|--------------|
| Internal Audit | Full access |
| External Audit | Per engagement scope |
| Compliance | Full access |
| Management | Full access |
| Team members | Redacted (no PII) |

---

## 11. Continuous Improvement

### 11.1 PIR Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PIR completion rate | 100% for SEV-1/2 | # completed / # required |
| PIR timeliness | 100% within deadline | # on-time / # total |
| Action completion rate | > 90% | # completed / # assigned |
| Recurrence rate | < 5% | # repeat incidents / # total |

### 11.2 Learning Distribution

| Learning Type | Distribution Method |
|---------------|---------------------|
| Critical lessons | All-hands, mandatory |
| Technical lessons | Engineering share-out |
| Process lessons | Operations review |
| Trends | Monthly report |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 20, 2025 | Operations Team | Initial version |
