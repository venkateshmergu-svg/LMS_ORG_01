/**
 * Reports Page (HR Admin Only)
 *
 * Provides read-only reports and integration sync triggers
 * - Leave utilization reports
 * - Department statistics
 * - HRIS sync status and trigger
 * - Payroll sync status and trigger
 *
 * Enhanced with:
 * - Skeleton loaders for better perceived performance
 * - Consistent button styling
 * - Improved accessibility
 * - Query optimization
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { TableSkeleton } from '@/components/common/SkeletonLoaders';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { SuccessAlert } from '@/components/common/SuccessAlert';
import { getSyncStatusClass } from '@/utils/statusBadges';
import { buttonPrimary } from '@/utils/buttonStyles';
import type { SyncStatus } from '@/api/types/generated';

interface LeaveReport {
  department: string;
  total_employees: number;
  total_leave_taken: number;
  avg_leave_per_employee: number;
  most_common_leave_type: string;
}

interface LeaveUtilization {
  leave_type: string;
  total_days_allocated: number;
  total_days_used: number;
  total_days_pending: number;
  utilization_percentage: number;
}

export function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<'utilization' | 'department'>('utilization');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const queryClient = useQueryClient();

  // Fetch utilization report
  const { data: utilizationData, isLoading: isLoadingUtilization } = useQuery({
    queryKey: ['reports', 'utilization'],
    queryFn: async () => {
      const { data } = await apiClient.get<LeaveUtilization[]>('/api/v1/reports/utilization');
      return data;
    },
    enabled: selectedReport === 'utilization',
    staleTime: 10 * 60 * 1000, // 10 minutes - reports don't change frequently
  });

  // Fetch department report
  const { data: departmentData, isLoading: isLoadingDepartment } = useQuery({
    queryKey: ['reports', 'department'],
    queryFn: async () => {
      const { data } = await apiClient.get<LeaveReport[]>('/api/v1/reports/department');
      return data;
    },
    enabled: selectedReport === 'department',
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch sync statuses
  const { data: syncStatuses, isLoading: isLoadingSyncStatus } = useQuery({
    queryKey: ['sync-status'],
    queryFn: async () => {
      const { data } = await apiClient.get<SyncStatus[]>('/api/v1/integrations/sync/status');
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Trigger HRIS sync
  const hrisSyncMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/api/v1/integrations/hris/sync');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sync-status'] });
      setSuccessMessage('HRIS sync triggered successfully');
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      setErrorMessage(error.response?.data?.detail || 'Failed to trigger HRIS sync');
      setTimeout(() => setErrorMessage(''), 5000);
    },
  });

  // Trigger Payroll sync
  const payrollSyncMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/api/v1/integrations/payroll/sync');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sync-status'] });
      setSuccessMessage('Payroll sync triggered successfully');
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      setErrorMessage(error.response?.data?.detail || 'Failed to trigger payroll sync');
      setTimeout(() => setErrorMessage(''), 5000);
    },
  });

  const getSyncStatusBadge = (status: string) => {
    return getSyncStatusClass(status);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Reports & Integrations
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            View leave reports and manage system integrations
          </p>
        </div>

        {/* Alerts */}
        {successMessage && (
          <SuccessAlert message={successMessage} onClose={() => setSuccessMessage('')} />
        )}
        {errorMessage && <ErrorAlert message={errorMessage} onClose={() => setErrorMessage('')} />}

        {/* Reports Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Leave Reports</h2>

          {/* Report Tabs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setSelectedReport('utilization')}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    selectedReport === 'utilization'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Leave Utilization
                </button>
                <button
                  onClick={() => setSelectedReport('department')}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    selectedReport === 'department'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Department Statistics
                </button>
              </nav>
            </div>

            {/* Report Content */}
            <div className="p-6">
              {selectedReport === 'utilization' && (
                <>
                  {isLoadingUtilization ? (
                    <TableSkeleton rows={5} columns={5} />
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Leave Type
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Allocated
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Used
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Pending
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Utilization
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                          {utilizationData?.map((item, idx) => (
                            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                              <td className="py-3 px-4 text-gray-900 dark:text-white">
                                {item.leave_type}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.total_days_allocated}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.total_days_used}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.total_days_pending}
                              </td>
                              <td className="py-3 px-4 text-right">
                                <span
                                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                                    item.utilization_percentage >= 80
                                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                      : item.utilization_percentage >= 50
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                                        : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                  }`}
                                >
                                  {item.utilization_percentage.toFixed(1)}%
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}

              {selectedReport === 'department' && (
                <>
                  {isLoadingDepartment ? (
                    <TableSkeleton rows={5} columns={5} />
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Department
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Employees TableSkeleton rows={5} columns={5} / Total Leave Taken
                            </th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Avg per Employee
                            </th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                              Most Common Type
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                          {departmentData?.map((item, idx) => (
                            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                              <td className="py-3 px-4 text-gray-900 dark:text-white">
                                {item.department}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.total_employees}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.total_leave_taken}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                                {item.avg_leave_per_employee.toFixed(1)}
                              </td>
                              <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                                {item.most_common_leave_type}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Integration Sync Section */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            System Integrations
          </h2>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            {isLoadingSyncStatus ? (
              <div className="p-6">
                <TableSkeleton rows={2} columns={1} />
              </div>
            ) : (
              <div className="p-6 space-y-6">
                {syncStatuses?.map((sync, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {sync.sync_type} Sync
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Last sync:{' '}
                          {new Date(sync.last_sync).toLocaleString('en-US', {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getSyncStatusBadge(sync.status)}`}
                      >
                        {sync.status}
                      </span>
                    </div>

                    {sync.error_message && (
                      <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 rounded text-sm text-red-800 dark:text-red-200">
                        {sync.error_message}
                      </div>
                    )}

                    <button
                      onClick={() => {
                        if (sync.sync_type === 'HRIS') {
                          hrisSyncMutation.mutate();
                        } else if (sync.sync_type === 'PAYROLL') {
                          payrollSyncMutation.mutate();
                        }
                      }}
                      disabled={
                        sync.status === 'IN_PROGRESS' ||
                        hrisSyncMutation.isPending ||
                        payrollSyncMutation.isPending
                      }
                      className={buttonPrimary}
                      aria-label={`Trigger ${sync.sync_type} sync`}
                    >
                      {sync.status === 'IN_PROGRESS'
                        ? 'Sync in Progress...'
                        : hrisSyncMutation.isPending || payrollSyncMutation.isPending
                          ? 'Triggering...'
                          : 'Trigger Sync'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
