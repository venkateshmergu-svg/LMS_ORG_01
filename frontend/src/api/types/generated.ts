/**
 * Generated API Types
 *
 * TODO: Generate these from backend OpenAPI spec using:
 * npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types/generated.ts
 *
 * For now, these are manual type definitions matching the backend API.
 */

// Common types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  [key: string]: unknown;
}

// Auth types
export interface User {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Leave types
// Status values: DRAFT, PENDING (pending_approval), APPROVED, REJECTED, WITHDRAWN (cancelled)
export type LeaveRequestStatus = 'DRAFT' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'WITHDRAWN';

export interface LeaveRequest {
  id: string;
  user_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason: string;
  status: LeaveRequestStatus;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequestCreate {
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
}

export interface LeaveBalance {
  employee_id: string;
  leave_type: string;
  total_balance: number;
  used: number;
  pending: number;
  available: number;
}

export interface LeavePolicy {
  leave_type: string;
  annual_allocation: number;
  accrual_frequency: string;
  carry_forward_allowed: boolean;
  max_carry_forward: number;
}

// Approval types
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface ApprovalRequest {
  id: string;
  step_id: string;
  leave_request_id: string;
  approver_id: string;
  approver_name: string;
  // Employee info (from leave request)
  employee_id: string;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason?: string;
  // Approval workflow info
  status: ApprovalStatus;
  sequence: number;
  comments?: string;
  created_at: string;
  updated_at: string;
}

export interface ApprovalAction {
  comment?: string;
}

// Workflow types
export interface WorkflowState {
  id: string;
  leave_request_id: string;
  current_state: string;
  previous_state: string;
  transition_at: string;
  triggered_by: string;
}

// Audit types
export interface AuditLog {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  performed_by: string;
  timestamp: string;
  ip_address?: string;
}

// Integration types
export interface SyncStatus {
  sync_type: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCESS' | 'FAILED';
  last_sync: string;
  error_message?: string;
}
