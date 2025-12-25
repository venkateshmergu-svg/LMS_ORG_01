/**
 * Approvals API Endpoints
 * 
 * Uses step-based approval workflow from backend.
 */

import { apiClient } from '../client';
import type { ApprovalAction, ApprovalRequest, PaginatedResponse } from '../types/generated';

export const approvalsAPI = {
  /**
   * GET /api/v1/approvals/pending
   * Get pending approvals for current manager
   */
  getPending: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<ApprovalRequest>> => {
    const { data } = await apiClient.get('/api/v1/approvals/pending', { params });
    return data;
  },

  /**
   * GET /api/v1/approvals/{step_id}
   * Get specific approval step details
   */
  getApproval: async (stepId: string): Promise<ApprovalRequest> => {
    const { data } = await apiClient.get(`/api/v1/approvals/${stepId}`);
    return data;
  },

  /**
   * POST /api/v1/leave-requests/steps/{step_id}/approve
   * Approve a workflow step (actor ID comes from JWT on backend)
   */
  approve: async (stepId: string, action: ApprovalAction): Promise<{ leave_request_id: string; status: string; is_final: boolean }> => {
    const { data } = await apiClient.post(`/api/v1/leave-requests/steps/${stepId}/approve`, action);
    return data;
  },

  /**
   * POST /api/v1/leave-requests/steps/{step_id}/reject
   * Reject a workflow step (actor ID comes from JWT on backend)
   */
  reject: async (stepId: string, action: ApprovalAction): Promise<{ leave_request_id: string; status: string; is_final: boolean }> => {
    const { data } = await apiClient.post(`/api/v1/leave-requests/steps/${stepId}/reject`, action);
    return data;
  },
};
