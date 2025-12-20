/**
 * Approvals API Endpoints
 */

import { apiClient } from '../client';
import type { ApprovalRequest, ApprovalAction, PaginatedResponse } from '../types/generated';

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
   * GET /api/v1/approvals/{id}
   * Get specific approval request details
   */
  getApproval: async (id: string): Promise<ApprovalRequest> => {
    const { data } = await apiClient.get(`/api/v1/approvals/${id}`);
    return data;
  },

  /**
   * POST /api/v1/approvals/{id}/approve
   * Approve a leave request
   */
  approve: async (id: string, action: ApprovalAction): Promise<ApprovalRequest> => {
    const { data } = await apiClient.post(`/api/v1/approvals/${id}/approve`, action);
    return data;
  },

  /**
   * POST /api/v1/approvals/{id}/reject
   * Reject a leave request
   */
  reject: async (id: string, action: ApprovalAction): Promise<ApprovalRequest> => {
    const { data } = await apiClient.post(`/api/v1/approvals/${id}/reject`, action);
    return data;
  },
};
