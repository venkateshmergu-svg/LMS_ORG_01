/**
 * Leave API Endpoints
 * 
 * All API calls go through this layer for type safety and consistency.
 */

import { apiClient } from '../client';
import type {
  LeaveRequest,
  LeaveRequestCreate,
  LeaveBalance,
  PaginatedResponse,
} from '../types/generated';

export const leaveAPI = {
  /**
   * GET /api/v1/leave/requests
   * Get user's leave requests
   */
  getMyRequests: async (params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<LeaveRequest>> => {
    const { data } = await apiClient.get('/api/v1/leave/requests', { params });
    return data;
  },

  /**
   * GET /api/v1/leave/requests/{id}
   * Get specific leave request
   */
  getRequest: async (id: string): Promise<LeaveRequest> => {
    const { data } = await apiClient.get(`/api/v1/leave/requests/${id}`);
    return data;
  },

  /**
   * POST /api/v1/leave/requests
   * Create new leave request
   */
  createRequest: async (payload: LeaveRequestCreate): Promise<LeaveRequest> => {
    const { data } = await apiClient.post('/api/v1/leave/requests', payload);
    return data;
  },

  /**
   * DELETE /api/v1/leave/requests/{id}
   * Withdraw pending leave request
   */
  withdrawRequest: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/leave/requests/${id}`);
  },

  /**
   * GET /api/v1/leave/balance
   * Get leave balance for current user
   */
  getBalance: async (): Promise<LeaveBalance> => {
    const { data } = await apiClient.get('/api/v1/leave/balance');
    return data;
  },
};
