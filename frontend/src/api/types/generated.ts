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
  [key: string]: any;
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
export interface LeaveRequest {
  id: string;
  user_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'WITHDRAWN';
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
export interface ApprovalRequest {
  id: string;
  leave_request_id: string;
  approver_id: string;
  approver_name: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  sequence: number;
  comments?: string;
  created_at: string;
  updated_at: string;
}

export interface ApprovalAction {
  status: 'APPROVED' | 'REJECTED';
  comments?: string;
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
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
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
