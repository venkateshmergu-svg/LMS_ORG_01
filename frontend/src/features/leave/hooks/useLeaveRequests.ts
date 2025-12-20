/**
 * Leave Request Hooks
 * 
 * Custom React Query hooks for leave management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leaveAPI } from '@/api/endpoints/leave.api';
import { mapAPIError } from '@/api/errors';

const QUERY_KEYS = {
  leaveRequests: ['leave', 'requests'] as const,
  leaveRequest: (id: string) => ['leave', 'requests', id] as const,
  leaveBalance: ['leave', 'balance'] as const,
};

/**
 * Fetch user's leave requests with optional filtering
 */
export function useLeaveRequests(params?: { status?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...QUERY_KEYS.leaveRequests, params],
    queryFn: () => leaveAPI.getMyRequests(params),
  });
}

/**
 * Fetch specific leave request
 */
export function useLeaveRequest(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.leaveRequest(id),
    queryFn: () => leaveAPI.getRequest(id),
  });
}

/**
 * Fetch user's leave balance
 */
export function useLeaveBalance() {
  return useQuery({
    queryKey: QUERY_KEYS.leaveBalance,
    queryFn: () => leaveAPI.getBalance(),
  });
}

/**
 * Create new leave request mutation
 */
export function useCreateLeaveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: leaveAPI.createRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveRequests });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveBalance });
    },
    onError: (error) => {
      const mappedError = mapAPIError(error);
      console.error('Failed to create leave request:', mappedError);
    },
  });
}

/**
 * Withdraw pending leave request mutation
 */
export function useWithdrawLeaveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => leaveAPI.withdrawRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveRequests });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.leaveBalance });
    },
  });
}
