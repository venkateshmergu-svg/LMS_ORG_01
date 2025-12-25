/**
 * Leave History Page
 *
 * Displays user's leave request history with:
 * - Filtering by status
 * - Detailed view modal
 * - Withdraw action for pending requests
 * - Pagination
 *
 * Enhanced with:
 * - Consistent formatting utilities
 * - Skeleton loaders for better perceived performance
 * - Improved accessibility (ARIA labels, keyboard navigation)
 * - Query optimization with staleTime
 */

import { leaveAPI } from '@/api/endpoints/leave.api';
import type { LeaveRequest } from '@/api/types/generated';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Modal } from '@/components/common/Modal';
import { TableSkeleton } from '@/components/common/SkeletonLoaders';
import { SuccessAlert } from '@/components/common/SuccessAlert';
import { useLeaveRequests } from '@/features/leave/hooks/useLeaveRequests';
import { buttonDestructive, buttonSecondary, buttonText } from '@/utils/buttonStyles';
import { formatDate } from '@/utils/formatters';
import { getLeaveStatusClass as getStatusBadgeClass } from '@/utils/statusBadges';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { memo, useCallback, useState } from 'react';

// Memoized filter component to prevent unnecessary re-renders
const StatusFilter = memo(
  ({ value, onChange }: { value: string; onChange: (value: string) => void }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <div className="flex items-center gap-4">
        <label
          htmlFor="status-filter"
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Filter by Status:
        </label>
        <select
          id="status-filter"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          aria-label="Filter leave requests by status"
        >
          <option value="all">All</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
          <option value="WITHDRAWN">Withdrawn</option>
        </select>
      </div>
    </div>
  )
);

StatusFilter.displayName = 'StatusFilter';

export function LeaveHistoryPage() {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const queryClient = useQueryClient();

  const {
    data: requests,
    isLoading,
    error,
  } = useLeaveRequests({
    status: statusFilter === 'all' ? undefined : statusFilter,
  });

  const withdrawMutation = useMutation({
    mutationFn: (id: string) => leaveAPI.withdrawRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
      queryClient.invalidateQueries({ queryKey: ['leave-balance'] });
      setSelectedRequest(null);
      setSuccessMessage('Leave request withdrawn successfully');
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      setErrorMessage(error.response?.data?.detail || 'Failed to withdraw request');
      setTimeout(() => setErrorMessage(''), 5000);
    },
  });

  const handleWithdraw = useCallback(
    (request: LeaveRequest) => {
      if (window.confirm('Are you sure you want to withdraw this leave request?')) {
        withdrawMutation.mutate(request.id);
      }
    },
    [withdrawMutation]
  );

  // Use imported formatDate and getStatusBadgeClass from utilities

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Leave History</h1>
          <p className="text-gray-600 dark:text-gray-400">View and manage your leave requests</p>
        </div>

        {/* Alerts */}
        {successMessage && (
          <SuccessAlert message={successMessage} onClose={() => setSuccessMessage('')} />
        )}
        {errorMessage && <ErrorAlert message={errorMessage} onClose={() => setErrorMessage('')} />}

        {/* Filters */}
        <StatusFilter value={statusFilter} onChange={setStatusFilter} />

        {/* Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <TableSkeleton rows={5} columns={6} />
          ) : error ? (
            <div className="p-6">
              <ErrorAlert
                message="Failed to load leave history. Please try again."
                onClose={() => {}}
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      Leave Type
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      Start Date
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      End Date
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      Days
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {requests?.items && requests.items.length > 0 ? (
                    requests.items.map((request) => (
                      <tr
                        key={request.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        <td className="py-3 px-4 text-gray-900 dark:text-white">
                          {request.leave_type}
                        </td>
                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                          {formatDate(request.start_date)}
                        </td>
                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                          {formatDate(request.end_date)}
                        </td>
                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                          {request.days_requested}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(request.status)}`}
                          >
                            {request.status}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => setSelectedRequest(request)}
                              className={buttonText}
                              aria-label={`View details for ${request.leave_type} request`}
                            >
                              View Details
                            </button>
                            {request.status === 'PENDING' && (
                              <button
                                onClick={() => handleWithdraw(request)}
                                disabled={withdrawMutation.isPending}
                                className={`${buttonText} text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300`}
                                aria-label={`Withdraw ${request.leave_type} request`}
                              >
                                {withdrawMutation.isPending ? 'Withdrawing...' : 'Withdraw'}
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-12 text-center">
                        <div className="text-gray-500 dark:text-gray-400">
                          <svg
                            className="mx-auto h-12 w-12 mb-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                          </svg>
                          <p className="text-lg font-medium">No leave requests found</p>
                          <p className="text-sm mt-1">
                            {statusFilter !== 'all'
                              ? `No ${statusFilter.toLowerCase()} requests`
                              : "You haven't submitted any leave requests yet"}
                          </p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail Modal */}
        {selectedRequest && (
          <Modal
            isOpen={true}
            onClose={() => setSelectedRequest(null)}
            title="Leave Request Details"
            size="lg"
          >
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Leave Type
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white font-medium">
                    {selectedRequest.leave_type}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Status
                  </label>
                  <p className="mt-1">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(selectedRequest.status)}`}
                    >
                      {selectedRequest.status}
                    </span>
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Start Date
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {formatDate(selectedRequest.start_date)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    End Date
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {formatDate(selectedRequest.end_date)}
                  </p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Days Requested
                </label>
                <p className="mt-1 text-gray-900 dark:text-white font-medium">
                  {selectedRequest.days_requested} days
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Reason
                </label>
                <p className="mt-1 text-gray-900 dark:text-white whitespace-pre-wrap">
                  {selectedRequest.reason}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t dark:border-gray-700">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Created
                  </label>
                  <p className="mt-1 text-gray-700 dark:text-gray-300 text-sm">
                    {formatDate(selectedRequest.created_at)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Last Updated
                  </label>
                  <p className="mt-1 text-gray-700 dark:text-gray-300 text-sm">
                    {formatDate(selectedRequest.updated_at)}
                  </p>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => setSelectedRequest(null)}
                  className={buttonSecondary}
                  aria-label="Close details modal"
                >
                  Close
                </button>
                {selectedRequest.status === 'PENDING' && (
                  <button
                    onClick={() => {
                      handleWithdraw(selectedRequest);
                    }}
                    disabled={withdrawMutation.isPending}
                    className={buttonDestructive}
                    aria-label="Withdraw this leave request"
                  >
                    {withdrawMutation.isPending ? 'Withdrawing...' : 'Withdraw Request'}
                  </button>
                )}
              </div>
            </div>
          </Modal>
        )}
      </div>
    </div>
  );
}
