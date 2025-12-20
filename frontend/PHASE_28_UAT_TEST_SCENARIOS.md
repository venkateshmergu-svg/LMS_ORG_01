# LMS Frontend - Phase 28: UAT Test Scenarios

**Document Version:** 1.0  
**Date:** December 20, 2025  
**Status:** ACTIVE

---

## Table of Contents

1. [Overview](#overview)
2. [Employee Role Scenarios](#employee-role-scenarios)
3. [Manager Role Scenarios](#manager-role-scenarios)
4. [HR Administrator Role Scenarios](#hr-administrator-role-scenarios)
5. [Auditor Role Scenarios](#auditor-role-scenarios)
6. [Cross-Role Scenarios](#cross-role-scenarios)
7. [Test Data Requirements](#test-data-requirements)

---

## Overview

### Scenario Structure

Each scenario includes:
- **ID**: Unique identifier (ROLE-XXX)
- **Priority**: Critical / High / Medium / Low
- **Preconditions**: Setup required before test
- **Steps**: User actions in business language
- **Expected Outcome**: Business-observable result
- **Evidence Required**: What to capture for audit

### Priority Definitions

| Priority | Definition | Pass Requirement |
|----------|------------|------------------|
| Critical | Core business function, regulatory requirement | 100% must pass |
| High | Important business function | 100% must pass |
| Medium | Standard business function | 95% must pass |
| Low | Nice-to-have, cosmetic | Documented for review |

### Test Execution Key

| Status | Symbol | Meaning |
|--------|--------|---------|
| Not Started | ⬜ | Test not yet executed |
| Passed | ✅ | Test passed successfully |
| Failed | ❌ | Test failed, defect logged |
| Blocked | 🚫 | Cannot execute due to blocker |
| Deferred | ⏸️ | Postponed with approval |

---

## Employee Role Scenarios

### EMP-001: Submit Annual Leave Request (Happy Path)

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee logged in, sufficient annual leave balance (≥5 days) |

**Steps:**
1. Navigate to "Apply for Leave" page
2. Select leave type: "Annual Leave"
3. Select start date: [Future date, at least 7 days ahead]
4. Select end date: [Start date + 4 working days]
5. Enter reason: "Family vacation"
6. Click "Submit Request"

**Expected Outcome:**
- Confirmation message displayed: "Leave request submitted successfully"
- Request appears in "My Leave Requests" with status "Pending Approval"
- Leave balance shows pending deduction
- Manager receives notification (verify in manager account)

**Evidence Required:**
- Screenshot of confirmation message
- Screenshot of request in "My Leave Requests"
- Screenshot of updated balance display

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-002: Submit Sick Leave Request

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee logged in, sick leave balance available |

**Steps:**
1. Navigate to "Apply for Leave" page
2. Select leave type: "Sick Leave"
3. Select start date: [Today or past date within policy]
4. Select end date: [Same day or next day]
5. Enter reason: "Unwell, doctor's appointment"
6. Click "Submit Request"

**Expected Outcome:**
- Confirmation message displayed
- Request appears with status "Pending Approval"
- Sick leave balance reflects pending deduction

**Evidence Required:**
- Screenshot of submitted request
- Screenshot of balance before and after

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-003: Submit Half-Day Leave

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Employee logged in, leave balance ≥0.5 days |

**Steps:**
1. Navigate to "Apply for Leave"
2. Select leave type: "Annual Leave"
3. Select date: [Future date]
4. Select duration: "Half Day - Morning" or "Half Day - Afternoon"
5. Enter reason: "Personal appointment"
6. Submit request

**Expected Outcome:**
- Request submitted for 0.5 days
- Balance shows 0.5 day pending deduction
- Request status shows "Pending Approval"

**Evidence Required:**
- Screenshot showing half-day selection
- Screenshot of balance showing 0.5 day deduction

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-004: View Leave Balances

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee logged in with known balance values |

**Steps:**
1. Navigate to "My Leave Balances" or Dashboard
2. Review displayed balances for all leave types
3. Click on a leave type to view breakdown (if available)

**Expected Outcome:**
- All leave types displayed with current balance
- Balances match expected values (from test data)
- Breakdown shows: Entitled, Used, Pending, Available

**Evidence Required:**
- Screenshot of balance summary
- Screenshot of balance breakdown

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-005: View Leave History

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Employee has past leave requests (approved and rejected) |

**Steps:**
1. Navigate to "My Leave Requests" or "Leave History"
2. Filter by: All statuses
3. Review list of past requests
4. Click on a completed request to view details

**Expected Outcome:**
- All past requests displayed with status, dates, type
- Approved requests show approval date and approver
- Rejected requests show rejection reason
- Detail view shows complete request information

**Evidence Required:**
- Screenshot of leave history list
- Screenshot of request detail (approved)
- Screenshot of request detail (rejected)

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-006: Withdraw Pending Leave Request

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Employee has a pending leave request |

**Steps:**
1. Navigate to "My Leave Requests"
2. Locate a request with status "Pending Approval"
3. Click "Withdraw" or "Cancel" button
4. Confirm withdrawal when prompted

**Expected Outcome:**
- Request status changes to "Withdrawn"
- Leave balance is restored (pending deduction removed)
- Manager notification cleared (or notification sent about withdrawal)

**Evidence Required:**
- Screenshot of request before withdrawal
- Screenshot of withdrawal confirmation
- Screenshot of restored balance

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-007: Attempt Leave with Insufficient Balance (Negative)

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee logged in, annual leave balance < 2 days |

**Steps:**
1. Navigate to "Apply for Leave"
2. Select leave type: "Annual Leave"
3. Select dates spanning 5 working days (more than balance)
4. Attempt to submit request

**Expected Outcome:**
- System prevents submission
- Clear error message: "Insufficient leave balance"
- Balance information displayed showing available vs. requested
- Request is NOT created

**Evidence Required:**
- Screenshot of error message
- Screenshot showing request was not created

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-008: Attempt Overlapping Leave Request (Negative)

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Employee has approved leave on specific dates |

**Steps:**
1. Navigate to "Apply for Leave"
2. Select dates that overlap with existing approved leave
3. Attempt to submit request

**Expected Outcome:**
- System prevents submission
- Error message indicates overlapping dates
- Existing leave dates shown for reference

**Evidence Required:**
- Screenshot of error message
- Screenshot of existing leave causing overlap

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-009: Attempt Past-Date Leave (Policy Dependent)

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Preconditions** | System configured with backdating policy |

**Steps:**
1. Navigate to "Apply for Leave"
2. Select leave type: "Annual Leave"
3. Select start date: [Date more than allowed backdating period]
4. Attempt to submit

**Expected Outcome:**
- If backdating not allowed: Error message, submission blocked
- If backdating limited: Error if beyond limit
- Clear message explaining policy

**Evidence Required:**
- Screenshot of error/validation message

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### EMP-010: View Team Calendar

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Preconditions** | Employee has team members, some with approved leave |

**Steps:**
1. Navigate to "Team Calendar" or "Absence Calendar"
2. Select current month view
3. Navigate to next month
4. Click on a colleague's absence entry (if visible)

**Expected Outcome:**
- Calendar displays with absences marked
- Own absences clearly distinguished
- Team member absences visible (per policy)
- Navigation between months works smoothly

**Evidence Required:**
- Screenshot of calendar view
- Screenshot showing team absences

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

## Manager Role Scenarios

### MGR-001: View Pending Approval Queue

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Manager logged in, direct reports have pending requests |

**Steps:**
1. Navigate to "Approvals" or "Pending Requests"
2. Review list of pending leave requests
3. Verify all direct reports' requests are visible
4. Check that requests from non-reports are NOT visible

**Expected Outcome:**
- All pending requests from direct reports displayed
- Request details visible: Employee name, dates, type, duration
- No requests from employees outside reporting line
- Count matches expected pending requests

**Evidence Required:**
- Screenshot of approval queue
- Screenshot confirming expected employees visible

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-002: Approve Leave Request

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Manager has pending request to approve |

**Steps:**
1. Navigate to "Approvals"
2. Select a pending leave request
3. Review request details (dates, type, reason, balance impact)
4. Click "Approve"
5. (Optional) Add approval comment

**Expected Outcome:**
- Request status changes to "Approved"
- Request removed from pending queue
- Employee notified of approval
- Employee's balance updated (pending → used)
- Audit trail records approval action

**Evidence Required:**
- Screenshot of request before approval
- Screenshot of approval confirmation
- Screenshot of employee notification (from employee account)

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-003: Reject Leave Request

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Manager has pending request to reject |

**Steps:**
1. Navigate to "Approvals"
2. Select a pending leave request
3. Review request details
4. Click "Reject"
5. Enter rejection reason: "Team coverage required for project deadline"
6. Confirm rejection

**Expected Outcome:**
- Request status changes to "Rejected"
- Rejection reason stored with request
- Employee notified with rejection reason
- Employee's balance restored (pending removed)
- Audit trail records rejection

**Evidence Required:**
- Screenshot of rejection with reason
- Screenshot of employee receiving rejection notification

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-004: View Team Calendar

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Manager has direct reports with approved leave |

**Steps:**
1. Navigate to "Team Calendar"
2. View current month
3. Identify all team absences
4. Click on an absence to view details
5. Navigate to next month

**Expected Outcome:**
- All direct reports' approved absences displayed
- Absence type indicated (annual, sick, etc.)
- Click reveals employee name and leave details
- Public holidays marked (if configured)

**Evidence Required:**
- Screenshot of team calendar with absences
- Screenshot of absence detail popup

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-005: View Direct Report Leave Balance

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Manager with direct reports |

**Steps:**
1. Navigate to "Team" or "My Team"
2. Select a direct report
3. View their leave balances

**Expected Outcome:**
- All leave type balances visible
- Balances match employee's own view
- Can see: Entitled, Used, Pending, Available

**Evidence Required:**
- Screenshot of team member balance view
- Cross-reference with employee's own balance view

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-006: Bulk Approval (If Supported)

| Field | Value |
|-------|-------|
| **Priority** | Medium |
| **Preconditions** | Manager has multiple pending requests |

**Steps:**
1. Navigate to "Approvals"
2. Select multiple requests (checkbox)
3. Click "Approve Selected"
4. Confirm bulk approval

**Expected Outcome:**
- All selected requests approved
- Each employee notified individually
- Audit trail records each approval
- Approval queue updated

**Evidence Required:**
- Screenshot of multi-select
- Screenshot of bulk approval confirmation

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-007: Attempt to View Non-Report's Request (Negative)

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Manager knows ID of non-direct-report employee |

**Steps:**
1. Attempt to navigate directly to another employee's leave request
2. Try URL manipulation if possible: /requests/{other-employee-id}
3. Search for non-report in team views

**Expected Outcome:**
- Access denied for non-direct-report data
- Appropriate error message displayed
- No sensitive information exposed
- Audit log records access attempt (if configured)

**Evidence Required:**
- Screenshot of access denied message
- Document URL attempted

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### MGR-008: Manager Self Leave Request

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Manager logged in |

**Steps:**
1. Navigate to "Apply for Leave" (as employee function)
2. Submit a leave request for self
3. Verify request goes to manager's manager for approval

**Expected Outcome:**
- Request submitted successfully
- Request does NOT auto-approve
- Request appears in skip-level manager's queue
- Manager can see own request in "My Requests"

**Evidence Required:**
- Screenshot of manager's own leave request
- Screenshot showing request in skip-level manager's queue

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

## HR Administrator Role Scenarios

### HR-001: View All Leave Requests (Organization-Wide)

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | HR Admin logged in, requests exist across departments |

**Steps:**
1. Navigate to "Leave Administration" or "All Requests"
2. View unfiltered list of all requests
3. Filter by department
4. Filter by leave type
5. Filter by date range
6. Export list (if available)

**Expected Outcome:**
- All organization requests visible
- Filters work correctly
- Can see requests from all departments
- Export produces accurate data

**Evidence Required:**
- Screenshot of unfiltered request list
- Screenshot of filtered results
- Export file (if applicable)

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-002: Generate Leave Balance Report

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | HR Admin logged in |

**Steps:**
1. Navigate to "Reports"
2. Select "Leave Balance Report"
3. Set parameters: Department = All, As of Date = Today
4. Generate report
5. Export to Excel/CSV

**Expected Outcome:**
- Report displays all employees with balances
- Data is accurate and current
- Export file matches on-screen data
- Report includes: Employee, Department, Leave Type, Entitled, Used, Available

**Evidence Required:**
- Screenshot of report on screen
- Exported file
- Spot-check 3 employees against their actual balances

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-003: Generate Leave Utilization Report

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | HR Admin logged in, historical leave data exists |

**Steps:**
1. Navigate to "Reports"
2. Select "Leave Utilization Report"
3. Set date range: Last 12 months
4. Generate report
5. Review utilization metrics

**Expected Outcome:**
- Report shows leave usage trends
- Breakdown by leave type
- Comparison across departments (if available)
- Identifies high/low utilization

**Evidence Required:**
- Screenshot of utilization report
- Export file

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-004: Trigger HRIS Sync

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | HR Admin logged in, HRIS integration configured |

**Steps:**
1. Navigate to "Integrations" or "Admin"
2. Select "HRIS Sync"
3. Review last sync status
4. Trigger manual sync (if available)
5. Verify sync completion

**Expected Outcome:**
- Last sync timestamp displayed
- Manual sync triggers successfully (or shows scheduled time)
- Sync status updated
- No error messages (or errors clearly explained)

**Evidence Required:**
- Screenshot of sync status
- Screenshot of sync completion

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-005: Trigger Payroll Export

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | HR Admin logged in, payroll integration configured |

**Steps:**
1. Navigate to "Integrations" or "Payroll"
2. Select payroll period
3. Generate payroll export
4. Download export file
5. Verify export contents

**Expected Outcome:**
- Export generates without error
- File contains correct period data
- Format matches payroll system requirements
- All approved leave in period included

**Evidence Required:**
- Screenshot of export generation
- Export file
- Verification of sample entries

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-006: Adjust Employee Leave Balance

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | HR Admin logged in, adjustment permissions granted |

**Steps:**
1. Navigate to "Employee Management" or search for employee
2. Select employee
3. Navigate to "Balance Adjustment"
4. Select leave type: "Annual Leave"
5. Enter adjustment: +2 days
6. Enter reason: "Carry-over from previous year"
7. Submit adjustment

**Expected Outcome:**
- Adjustment applied immediately
- Employee balance updated
- Audit trail records: who, when, what, why
- Employee can see updated balance

**Evidence Required:**
- Screenshot of adjustment entry
- Screenshot of updated balance
- Screenshot of audit trail entry

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-007: View Employee Leave History (Cross-Organization)

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | HR Admin logged in |

**Steps:**
1. Search for any employee in organization
2. View their complete leave history
3. View their current balances
4. View pending requests

**Expected Outcome:**
- Full history visible regardless of department
- All leave types shown
- Status of all requests visible
- Can drill into request details

**Evidence Required:**
- Screenshot of employee search
- Screenshot of employee leave history

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### HR-008: Validate Data Accuracy

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Known test data set with calculated expected values |

**Steps:**
1. Select 5 employees from test data
2. For each employee:
   - Calculate expected balance manually
   - Compare with system balance
   - Verify all leave records present
3. Document any discrepancies

**Expected Outcome:**
- System balances match calculated values
- All leave records accurate
- No missing or duplicate entries

**Evidence Required:**
- Calculation worksheet
- Screenshots of each employee's balance
- Discrepancy report (if any)

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

## Auditor Role Scenarios

### AUD-001: View Audit Logs

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Auditor logged in, audit logs contain entries |

**Steps:**
1. Navigate to "Audit Logs" or "Audit Trail"
2. View recent entries (last 24 hours)
3. Filter by action type (e.g., "Leave Approved")
4. Filter by user
5. Filter by date range
6. Export audit log

**Expected Outcome:**
- Audit log displays chronological entries
- Each entry shows: Timestamp, User, Action, Details
- Filters work correctly
- Export captures filtered data

**Evidence Required:**
- Screenshot of audit log
- Screenshot of filtered results
- Export file

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### AUD-002: Verify Leave Request Audit Trail

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | A leave request has been submitted, approved |

**Steps:**
1. Navigate to Audit Logs
2. Search for specific leave request by ID or employee
3. Trace complete lifecycle:
   - Creation
   - Submission
   - Approval/Rejection
   - Any modifications
4. Verify each step has actor and timestamp

**Expected Outcome:**
- Complete request lifecycle traceable
- Each action attributed to specific user
- Timestamps accurate and sequential
- No gaps in audit trail

**Evidence Required:**
- Screenshot of audit entries for specific request
- Document showing complete lifecycle

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### AUD-003: Verify Balance Adjustment Audit Trail

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | HR Admin has made a balance adjustment |

**Steps:**
1. Navigate to Audit Logs
2. Filter for "Balance Adjustment" actions
3. Locate the specific adjustment
4. Verify logged details include:
   - Who made adjustment
   - When adjustment was made
   - What was changed (amount, type)
   - Why (reason provided)

**Expected Outcome:**
- Adjustment fully logged with all details
- Cannot be modified or deleted
- Searchable and filterable

**Evidence Required:**
- Screenshot of adjustment audit entry
- Comparison with actual adjustment made

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### AUD-004: Confirm Read-Only Access

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Auditor logged in |

**Steps:**
1. Navigate through all accessible screens
2. Attempt to submit a leave request
3. Attempt to approve a leave request
4. Attempt to modify any data
5. Verify no edit/create buttons available

**Expected Outcome:**
- Auditor can VIEW all audit-relevant data
- Auditor CANNOT create, modify, or delete data
- No action buttons available except view/export
- Clear "read-only" indication if available

**Evidence Required:**
- Screenshots showing read-only interface
- Document any edit capabilities found (defect)

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### AUD-005: Verify Login/Logout Audit

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | Multiple users have logged in/out |

**Steps:**
1. Navigate to Audit Logs
2. Filter for "Login" and "Logout" events
3. Verify entries exist for recent sessions
4. Check for failed login attempts (if available)

**Expected Outcome:**
- Login events logged with user and timestamp
- Logout events logged (or session end)
- Failed attempts logged (security feature)
- IP address recorded (if applicable)

**Evidence Required:**
- Screenshot of login/logout audit entries

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### AUD-006: Verify Data Cannot Be Tampered

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Auditor access only |

**Steps:**
1. View a historical leave request
2. Attempt to modify status via URL manipulation
3. Attempt to access admin functions
4. Attempt to delete audit entries

**Expected Outcome:**
- All modification attempts blocked
- Access denied for admin functions
- Audit logs immutable
- Security event logged (if applicable)

**Evidence Required:**
- Screenshots of blocked attempts
- Document any security concerns found

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

## Cross-Role Scenarios

### CROSS-001: End-to-End Leave Workflow

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee, Manager, HR Admin accounts ready |

**Steps:**
1. **Employee**: Submit leave request
2. **Employee**: Verify request appears as pending
3. **Manager**: Receive notification
4. **Manager**: View request in approval queue
5. **Manager**: Approve request
6. **Employee**: Receive approval notification
7. **Employee**: Verify balance updated
8. **HR Admin**: Verify request in reports
9. **Auditor**: Verify complete audit trail

**Expected Outcome:**
- Complete workflow executes without error
- All notifications delivered
- Balance correctly updated
- Full audit trail maintained

**Evidence Required:**
- Screenshot at each step
- Timeline document showing flow

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### CROSS-002: Rejection Workflow

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | Employee, Manager accounts ready |

**Steps:**
1. **Employee**: Submit leave request
2. **Manager**: Reject request with reason
3. **Employee**: Receive rejection notification
4. **Employee**: Verify balance NOT deducted
5. **Auditor**: Verify rejection audit trail

**Expected Outcome:**
- Rejection flows correctly
- Employee sees rejection reason
- Balance unaffected
- Audit complete

**Evidence Required:**
- Screenshots showing rejection flow
- Balance verification

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### CROSS-003: Balance Adjustment Visibility

| Field | Value |
|-------|-------|
| **Priority** | High |
| **Preconditions** | HR Admin has made adjustment |

**Steps:**
1. **HR Admin**: Make balance adjustment for employee
2. **Employee**: View updated balance
3. **Manager**: View employee's updated balance
4. **Auditor**: Verify adjustment audit trail

**Expected Outcome:**
- Adjustment visible to all relevant roles
- Consistency across views
- Audit trail complete

**Evidence Required:**
- Screenshots from each role view

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

### CROSS-004: RBAC Boundary Testing

| Field | Value |
|-------|-------|
| **Priority** | Critical |
| **Preconditions** | All role accounts available |

**Steps:**
1. **Employee**: Confirm cannot access manager approval queue
2. **Employee**: Confirm cannot access HR admin functions
3. **Employee**: Confirm cannot view other employees' data
4. **Manager**: Confirm cannot access HR admin functions
5. **Manager**: Confirm cannot view non-reports' data
6. **Auditor**: Confirm read-only everywhere

**Expected Outcome:**
- Each role restricted to authorized functions only
- No cross-role access violations
- Clear access denied messages

**Evidence Required:**
- Screenshot of each access attempt
- Document all RBAC validations

| Executed By | Date | Status | Defect ID |
|-------------|------|--------|-----------|
| | | ⬜ | |

---

## Test Data Requirements

### Required Test Accounts

| Role | Account | Department | Reporting To |
|------|---------|------------|--------------|
| Employee 1 | emp1@test.com | Engineering | Manager 1 |
| Employee 2 | emp2@test.com | Engineering | Manager 1 |
| Employee 3 | emp3@test.com | HR | Manager 2 |
| Manager 1 | mgr1@test.com | Engineering | Director |
| Manager 2 | mgr2@test.com | HR | Director |
| HR Admin | hradmin@test.com | HR | - |
| Auditor | auditor@test.com | Compliance | - |

### Required Leave Balances

| Employee | Annual Leave | Sick Leave | Personal Leave |
|----------|--------------|------------|----------------|
| Employee 1 | 15 days | 10 days | 3 days |
| Employee 2 | 2 days | 10 days | 3 days |
| Employee 3 | 20 days | 10 days | 3 days |

### Required Historical Data

- Employee 1: 3 approved requests (past 6 months)
- Employee 2: 1 approved, 1 rejected request
- Employee 3: 2 approved requests, 1 pending

---

## Test Summary Template

### Scenario Execution Summary

| Role | Total | Passed | Failed | Blocked | Not Run |
|------|-------|--------|--------|---------|---------|
| Employee | 10 | | | | 10 |
| Manager | 8 | | | | 8 |
| HR Admin | 8 | | | | 8 |
| Auditor | 6 | | | | 6 |
| Cross-Role | 4 | | | | 4 |
| **Total** | **36** | | | | **36** |

### Pass Rate by Priority

| Priority | Total | Passed | Pass Rate |
|----------|-------|--------|-----------|
| Critical | 18 | | % |
| High | 12 | | % |
| Medium | 6 | | % |
| **Overall** | **36** | | **%** |

---

*This document is part of the LMS Phase 28 UAT Program.*
