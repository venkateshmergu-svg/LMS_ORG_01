/**
 * Approval Queue Component
 *
 * Displays a table of pending leave approvals for managers.
 * Managers can approve or reject requests, and view details.
 */

import { useState } from 'react';
import { format, differenceInCalendarDays } from 'date-fns';
import { useApprovalsQuery, useApproveRequest, useRejectRequest } from '@/features/approvals/hooks/useApprovalsQuery';
import { RoleGate } from '@/auth/RoleGate';
import { ApprovalDetailModal } from './ApprovalDetailModal';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { SuccessAlert } from '@/components/common/SuccessAlert';

interface ApprovalQueuesProps {
  pageSize?: number;
}

interface SelectedApproval {
  id: string;
  employeeName: string;
  startDate: string;
  endDate: string;
  days: number;
  reason: string;
}

export function ApprovalQueue({ pageSize = 10 }: ApprovalQueuesProps) {
  const [page, setPage] = useState(1);
  const [selectedApproval, setSelectedApproval] = useState<SelectedApproval | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Fetch pending approvals
  const { data, isLoading, error, isFetching } = useApprovalsQuery({
    skip: (page - 1) * pageSize,
    limit: pageSize,
    status: 'pending',
  });

  // Mutations
  const { mutate: approve, isPending: isApproving } = useApproveRequest();
  const { mutate: reject, isPending: isRejecting } = useRejectRequest();

  const handleApproveClick = (approval: any) => {
    setSelectedApproval({
      id: approval.id,
      employeeName: approval.employee_name,
      startDate: approval.start_date,
      endDate: approval.end_date,
      days: differenceInCalendarDays(new Date(approval.end_date), new Date(approval.start_date)) + 1,
      reason: approval.reason,
    });
    setShowDetailModal(true);
  };

  const handleApproveConfirm = (comments?: string) => {
    if (!selectedApproval) return;

    approve(
      { id: selectedApproval.id, comments },
      {
        onSuccess: () => {
          setSuccessMessage(`Approved leave request from ${selectedApproval.employeeName}`);
          setShowDetailModal(false);
          setSelectedApproval(null);
          // Clear success message after 5 seconds
          setTimeout(() => setSuccessMessage(''), 5000);
        },
        onError: (err) => {
          setErrorMessage('Failed to approve request. Please try again.');
          console.error(err);
        },
      }
    );
  };

  const handleRejectClick = (approval: any) => {
    setSelectedApproval({
      id: approval.id,
      employeeName: approval.employee_name,
      startDate: approval.start_date,
      endDate: approval.end_date,
      days: differenceInCalendarDays(new Date(approval.end_date), new Date(approval.start_date)) + 1,
      reason: approval.reason,
    });
    setShowDetailModal(true);
  };

  const handleRejectConfirm = (comments: string) => {
    if (!selectedApproval || !comments) {
      setErrorMessage('Rejection reason is required');
      return;
    }

    reject(
      { id: selectedApproval.id, comments },
      {
        onSuccess: () => {
          setSuccessMessage(`Rejected leave request from ${selectedApproval.employeeName}`);
          setShowDetailModal(false);
          setSelectedApproval(null);
          // Clear success message after 5 seconds
          setTimeout(() => setSuccessMessage(''), 5000);
        },
        onError: (err) => {
          setErrorMessage('Failed to reject request. Please try again.');
          console.error(err);
        },
      }
    );
  };

  return (
    <RoleGate requiredRoles={['manager', 'hr_admin', 'auditor']}>
      <div className="space-y-4">
        {/* Success Alert */}
        {successMessage && <SuccessAlert message={successMessage} onClose={() => setSuccessMessage('')} />}

        {/* Error Alert */}
        {errorMessage && <ErrorAlert message={errorMessage} onClose={() => setErrorMessage('')} />}
        {error && <ErrorAlert message="Failed to load approvals" onClose={() => {}} />}

        {/* Table Container */}
        <div className="card overflow-hidden">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">
              <p>Loading approvals...</p>
            </div>
          ) : data?.items && data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold">Employee</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold">Leave Type</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold">Dates</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold">Days</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold">Submitted</th>
                      <th className="px-6 py-3 text-right text-sm font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {data.items.map((approval) => {
                      const daysRequested = differenceInCalendarDays(
                        new Date(approval.end_date),
                        new Date(approval.start_date)
                      ) + 1;

                      return (
                        <tr
                          key={approval.id}
                          className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition"
                        >
                          {/* Employee Name */}
                          <td className="px-6 py-4">
                            <p className="font-medium">{approval.employee_name}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{approval.employee_id}</p>
                          </td>

                          {/* Leave Type */}
                          <td className="px-6 py-4">
                            <span className="badge badge-info">{approval.leave_type}</span>
                          </td>

                          {/* Dates */}
                          <td className="px-6 py-4 text-sm">
                            <p>{format(new Date(approval.start_date), 'MMM dd, yyyy')}</p>
                            <p className="text-gray-500 dark:text-gray-400">
                              to {format(new Date(approval.end_date), 'MMM dd, yyyy')}
                            </p>
                          </td>

                          {/* Days Count */}
                          <td className="px-6 py-4 text-center">
                            <span className="font-semibold">{daysRequested}</span>
                          </td>

                          {/* Submitted Date */}
                          <td className="px-6 py-4 text-sm">
                            <p>{format(new Date(approval.created_at), 'MMM dd, yyyy')}</p>
                            <p className="text-gray-500 dark:text-gray-400">
                              {new Date(approval.created_at).toLocaleTimeString()}
                            </p>
                          </td>

                          {/* Actions */}
                          <td className="px-6 py-4 text-right">
                            <div className="flex gap-2 justify-end">
                              <button
                                onClick={() => handleApproveClick(approval)}
                                disabled={isApproving}
                                className="btn btn-sm btn-success"
                                title="Approve this request"
                              >
                                {isApproving ? 'Approving...' : 'Approve'}
                              </button>
                              <button
                                onClick={() => handleRejectClick(approval)}
                                disabled={isRejecting}
                                className="btn btn-sm btn-error"
                                title="Reject this request"
                              >
                                {isRejecting ? 'Rejecting...' : 'Reject'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {data && data.total > pageSize && (
                <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, data.total)} of{' '}
                    {data.total} approvals
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1 || isFetching}
                      className="btn btn-sm btn-secondary"
                    >
                      Previous
                    </button>
                    <span className="flex items-center px-4 text-sm">
                      Page {page} of {Math.ceil(data.total / pageSize)}
                    </span>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page >= Math.ceil(data.total / pageSize) || isFetching}
                      className="btn btn-sm btn-secondary"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              <p>No pending approvals</p>
              <p className="text-sm mt-2">All leave requests have been processed.</p>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedApproval && (
        <ApprovalDetailModal
          isOpen={showDetailModal}
          approval={selectedApproval}
          onApprove={handleApproveConfirm}
          onReject={handleRejectConfirm}
          isLoading={isApproving || isRejecting}
          onClose={() => {
            setShowDetailModal(false);
            setSelectedApproval(null);
          }}
        />
      )}
    </RoleGate>
  );
}
