/**
 * Approval Request Hooks
 *
 * React Query hooks for manager approval operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { approvalsAPI } from '@/api/endpoints/approvals.api';
import { mapAPIError } from '@/api/errors';

const QUERY_KEYS = {
  approvalsPending: ['approvals', 'pending'] as const,
  approvalsAll: ['approvals', 'all'] as const,
};

/**
 * Fetch pending approvals for current manager
 */
export function useApprovalsQuery(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...QUERY_KEYS.approvalsPending, params],
    queryFn: () => approvalsAPI.getPending(params),
  });
}

/**
 * Approve a leave request mutation
 */
export function useApproveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, comments }: { id: string; comments?: string }) =>
      approvalsAPI.approve(id, { status: 'APPROVED', comments }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.approvalsPending });
      queryClient.invalidateQueries({ queryKey: ['leave', 'requests'] });
    },
    onError: (error) => {
      const mappedError = mapAPIError(error);
      console.error('Failed to approve request:', mappedError);
    },
  });
}

/**
 * Reject a leave request mutation
 */
export function useRejectRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, comments }: { id: string; comments: string }) =>
      approvalsAPI.reject(id, { status: 'REJECTED', comments }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.approvalsPending });
      queryClient.invalidateQueries({ queryKey: ['leave', 'requests'] });
    },
    onError: (error) => {
      const mappedError = mapAPIError(error);
      console.error('Failed to reject request:', mappedError);
    },
  });
}
