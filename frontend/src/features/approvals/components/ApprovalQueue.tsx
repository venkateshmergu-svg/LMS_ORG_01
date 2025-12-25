/**
 * Approval Queue Component
 *
 * Displays pending approvals for managers to review and act on.
 */

import { RoleGate } from '@/auth/RoleGate';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { format } from 'date-fns';
import { useState } from 'react';
import { useApprovalsQuery, useApproveRequest, useRejectRequest } from '../hooks/useApprovalsQuery';

interface ApprovalQueueProps {
  pageSize?: number;
}

export function ApprovalQueue({ pageSize = 10 }: ApprovalQueueProps) {
  const [skip, setSkip] = useState(0);
  const { data, isLoading, error } = useApprovalsQuery({ skip, limit: pageSize });
  const approveMutation = useApproveRequest();
  const rejectMutation = useRejectRequest();
  const [rejectComment, setRejectComment] = useState<Record<string, string>>({});

  const handleApprove = (stepId: string) => {
    approveMutation.mutate({ stepId });
  };

  const handleReject = (stepId: string) => {
    const comment = rejectComment[stepId] || 'Rejected';
    rejectMutation.mutate({ stepId, comment });
  };

  return (
    <RoleGate requiredRoles={['MANAGER', 'HR_ADMIN', 'SYSTEM_ADMIN']}>
      <div className="card">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold">Pending Approvals</h2>
          {data && <p className="text-sm text-gray-500 mt-1">{data.total} pending request(s)</p>}
        </div>

        {isLoading && (
          <div className="p-8 text-center">
            <LoadingSpinner size="md" />
            <p className="mt-2 text-gray-500">Loading approvals...</p>
          </div>
        )}

        {error && (
          <div className="p-6 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300">
            Failed to load approvals. Please try again.
          </div>
        )}

        {data && data.items.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <p>No pending approvals</p>
            <p className="text-sm mt-1">You're all caught up! 🎉</p>
          </div>
        )}

        {data && data.items.length > 0 && (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.items.map((approval) => (
              <div key={approval.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{approval.employee_name}</span>
                      <span className="badge badge-info">{approval.leave_type}</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {format(new Date(approval.start_date), 'MMM dd, yyyy')} -{' '}
                      {format(new Date(approval.end_date), 'MMM dd, yyyy')}
                      <span className="mx-2">•</span>
                      {approval.days_requested} day(s)
                    </p>
                    {approval.reason && (
                      <p className="text-sm text-gray-500 mt-2 italic">"{approval.reason}"</p>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleApprove(approval.step_id)}
                      disabled={approveMutation.isPending}
                      className="btn btn-sm btn-success"
                    >
                      {approveMutation.isPending ? '...' : 'Approve'}
                    </button>
                    <button
                      onClick={() => handleReject(approval.step_id)}
                      disabled={rejectMutation.isPending}
                      className="btn btn-sm btn-error"
                    >
                      {rejectMutation.isPending ? '...' : 'Reject'}
                    </button>
                  </div>
                </div>
                <div className="mt-3">
                  <input
                    type="text"
                    placeholder="Rejection comment (required for reject)"
                    className="input input-sm w-full max-w-xs"
                    value={rejectComment[approval.step_id] || ''}
                    onChange={(e) => setRejectComment({ ...rejectComment, [approval.step_id]: e.target.value })}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {data && data.total > pageSize && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <button
              onClick={() => setSkip(Math.max(0, skip - pageSize))}
              disabled={skip === 0}
              className="btn btn-sm btn-secondary"
            >
              Previous
            </button>
            <span className="text-sm text-gray-500">
              Showing {skip + 1}-{Math.min(skip + pageSize, data.total)} of {data.total}
            </span>
            <button
              onClick={() => setSkip(skip + pageSize)}
              disabled={skip + pageSize >= data.total}
              className="btn btn-sm btn-secondary"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </RoleGate>
  );
}
