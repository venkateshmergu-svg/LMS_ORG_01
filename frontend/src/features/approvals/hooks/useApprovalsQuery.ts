/**
 * Approval Request Hooks
 *
 * React Query hooks for manager approval operations.
 * Uses step-based workflow from backend.
 */

import { approvalsAPI } from '@/api/endpoints/approvals.api';
import { mapAPIError } from '@/api/errors';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

const QUERY_KEYS = {
  approvalsPending: ['approvals', 'pending'] as const,
  approvalDetail: (stepId: string) => ['approvals', 'detail', stepId] as const,
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
 * Fetch specific approval step details
 */
export function useApprovalDetail(stepId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.approvalDetail(stepId),
    queryFn: () => approvalsAPI.getApproval(stepId),
    enabled: !!stepId,
  });
}

/**
 * Approve a workflow step
 */
export function useApproveRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ stepId, comment }: { stepId: string; comment?: string }) =>
      approvalsAPI.approve(stepId, { comment }),
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
 * Reject a workflow step
 */
export function useRejectRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ stepId, comment }: { stepId: string; comment: string }) =>
      approvalsAPI.reject(stepId, { comment }),
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
