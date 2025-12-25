/**
 * Audit Log Page
 * 
 * Read-only audit log viewer with:
 * - Filtering by entity type and action
 * - Search by entity ID or user
 * - Pagination
 * - Detailed view modal
 * 
 * Enhanced with:
 * - Skeleton loaders for better perceived performance
 * - Improved filter accessibility
 * - Consistent formatting utilities
 * - Query optimization
 */

import { apiClient } from '@/api/client';
import type { AuditLog, PaginatedResponse } from '@/api/types/generated';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { Modal } from '@/components/common/Modal';
import { TableSkeleton } from '@/components/common/SkeletonLoaders';
import { buttonSecondary, buttonText } from '@/utils/buttonStyles';
import { useQuery } from '@tanstack/react-query';
import { memo, useCallback, useState } from 'react';

// Memoized filters to prevent unnecessary re-renders
const AuditFilters = memo(({
  entityTypeFilter,
  actionFilter,
  searchQuery,
  onEntityTypeChange,
  onActionChange,
  onSearchChange,
}: {
  entityTypeFilter: string;
  actionFilter: string;
  searchQuery: string;
  onEntityTypeChange: (value: string) => void;
  onActionChange: (value: string) => void;
  onSearchChange: (value: string) => void;
}) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Search */}
      <div>
        <label 
          htmlFor="audit-search"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Search
        </label>
        <input
          id="audit-search"
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Entity ID or user email..."
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          aria-label="Search audit logs"
        />
      </div>

      {/* Entity Type Filter */}
      <div>
        <label 
          htmlFor="entity-type-filter"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Entity Type
        </label>
        <select
          id="entity-type-filter"
          value={entityTypeFilter}
          onChange={(e) => onEntityTypeChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          aria-label="Filter by entity type"
        >
          <option value="all">All Types</option>
          <option value="leave_request">Leave Request</option>
          <option value="approval">Approval</option>
          <option value="user">User</option>
          <option value="policy">Policy</option>
        </select>
      </div>

      {/* Action Filter */}
      <div>
        <label 
          htmlFor="action-filter"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Action
        </label>
        <select
          id="action-filter"
          value={actionFilter}
          onChange={(e) => onActionChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          aria-label="Filter by action type"
        >
          <option value="all">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="approve">Approve</option>
          <option value="reject">Reject</option>
        </select>
      </div>
    </div>
  </div>
));

AuditFilters.displayName = 'AuditFilters';

export function AuditPage() {
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>('all');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const pageSize = 20;

  const { data, isLoading, error } = useQuery({
    queryKey: ['audit-logs', entityTypeFilter, actionFilter, searchQuery, page],
    queryFn: async () => {
      const params: any = {
        skip: page * pageSize,
        limit: pageSize,
      };

      if (entityTypeFilter !== 'all') {
        params.entity_type = entityTypeFilter;
      }

      if (actionFilter !== 'all') {
        params.action = actionFilter;
      }

      if (searchQuery) {
        params.search = searchQuery;
      }

      const { data } = await apiClient.get<PaginatedResponse<AuditLog>>('/api/v1/audit/logs', {
        params,
      });
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - audit logs are relatively static
  });

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    setPage(0);
  }, []);

  const handleEntityTypeChange = useCallback((value: string) => {
    setEntityTypeFilter(value);
    setPage(0);
  }, []);

  const handleActionChange = useCallback((value: string) => {
    setActionFilter(value);
    setPage(0);
  }, []);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getActionBadgeClass = (action: string) => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'update':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'delete':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'approve':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'reject':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Audit Logs
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            View all system activity and changes
          </p>
        </div>

        {/* Filters */}
        <AuditFilters
          entityTypeFilter={entityTypeFilter}
          actionFilter={actionFilter}
          searchQuery={searchQuery}
          onEntityTypeChange={handleEntityTypeChange}
          onActionChange={handleActionChange}
          onSearchChange={handleSearchChange}
        />

        {/* Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <TableSkeleton rows={10} columns={6} />
          ) : error ? (
            <div className="p-6">
              <ErrorAlert
                message="Failed to load audit logs. Please try again."
                onClose={() => {}}
              />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        Timestamp
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        Entity Type
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        Action
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        Performed By
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        IP Address
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {data?.items && data.items.length > 0 ? (
                      data.items.map((log) => (
                        <tr
                          key={log.id}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-sm">
                            {formatDate(log.timestamp)}
                          </td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">
                            {log.entity_type}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-medium ${getActionBadgeClass(log.action)}`}
                            >
                              {log.action}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                            {log.performed_by}
                          </td>
                          <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-sm">
                            {log.ip_address || 'N/A'}
                          </td>
                          <td className="py-3 px-4">
                            <button
                              onClick={() => setSelectedLog(log)}
                              className={buttonText}
                              aria-label={`View details for ${log.action} on ${log.entity_type}`}
                            >
                              View Details
                            </button>
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
                            <p className="text-lg font-medium">No audit logs found</p>
                            <p className="text-sm mt-1">
                              Try adjusting your filters or search criteria
                            </p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {data && data.total > 0 && (
                <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    Showing {page * pageSize + 1} to{' '}
                    {Math.min((page + 1) * pageSize, data.total)} of {data.total} entries
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(page - 1)}
                      disabled={page <= 0}
                      className={buttonSecondary}
                      aria-label="Previous page"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page >= totalPages - 1}
                      className={buttonSecondary}
                      aria-label="Next page"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Detail Modal */}
        {selectedLog && (
          <Modal
            isOpen={true}
            onClose={() => setSelectedLog(null)}
            title="Audit Log Details"
            size="lg"
          >
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Timestamp
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {formatDate(selectedLog.timestamp)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Action
                  </label>
                  <p className="mt-1">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getActionBadgeClass(selectedLog.action)}`}
                    >
                      {selectedLog.action}
                    </span>
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Entity Type
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {selectedLog.entity_type}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Entity ID
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white font-mono text-sm">
                    {selectedLog.entity_id}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Performed By
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {selectedLog.performed_by}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    IP Address
                  </label>
                  <p className="mt-1 text-gray-900 dark:text-white">
                    {selectedLog.ip_address || 'N/A'}
                  </p>
                </div>
              </div>

              {selectedLog.old_values && Object.keys(selectedLog.old_values).length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2 block">
                    Old Values
                  </label>
                  <pre className="p-3 bg-gray-50 dark:bg-gray-900 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedLog.old_values, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLog.new_values && Object.keys(selectedLog.new_values).length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2 block">
                    New Values
                  </label>
                  <pre className="p-3 bg-gray-50 dark:bg-gray-900 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedLog.new_values, null, 2)}
                  </pre>
                </div>
              )}

              <div className="flex justify-end">
                <button
                  onClick={() => setSelectedLog(null)}
                  className={buttonSecondary}
                  aria-label="Close audit log details"
                >
                  Close
                </button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </div>
  );
}
