/**
 * Dashboard Page
 *
 * Main landing page showing user summary, quick actions, and recent activity.
 * 
 * Performance optimizations:
 * - useMemo for computed values (pendingCount, thisMonthCount)
 * - Memoized child components where appropriate
 */

import { useAuth } from '@/auth/AuthProvider';
import { BalanceCard } from '@/features/balance/components/BalanceCard';
import { useLeaveBalance, useLeaveRequests } from '@/features/leave/hooks/useLeaveRequests';
import { format } from 'date-fns';
import { Calendar, FileText, Users } from 'lucide-react';
import { useMemo } from 'react';
import { Link } from 'react-router-dom';

export function DashboardPage() {
  const { user } = useAuth();
  const { data: balance } = useLeaveBalance();
  const { data: requests } = useLeaveRequests({ limit: 5, status: 'all' });

  // Memoize computed values to avoid recalculation on every render
  const { thisMonthCount } = useMemo(() => {
    const thisMonth = requests?.items.filter((r) => {
      const now = new Date();
      const reqDate = new Date(r.start_date);
      return reqDate.getMonth() === now.getMonth() && reqDate.getFullYear() === now.getFullYear();
    }).length ?? 0;
    
    return { thisMonthCount: thisMonth };
  }, [requests?.items]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Here's your leave management summary
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Available Days</p>
                <p className="text-3xl font-bold text-success">{balance?.available ?? 0}</p>
              </div>
              <Calendar className="w-10 h-10 text-success opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Used Days</p>
                <p className="text-3xl font-bold text-error">{balance?.used ?? 0}</p>
              </div>
              <FileText className="w-10 h-10 text-error opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pending</p>
                <p className="text-3xl font-bold text-warning">{balance?.pending ?? 0}</p>
              </div>
              <Users className="w-10 h-10 text-warning opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">This Month</p>
                <p className="text-3xl font-bold">{thisMonthCount}</p>
              </div>
              <Calendar className="w-10 h-10 text-primary opacity-20" />
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Actions */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Link to="/leave/apply" className="btn btn-primary">
                  + Apply for Leave
                </Link>
                <Link to="/leave/history" className="btn btn-secondary">
                  View History
                </Link>
                <Link to="/calendar" className="btn btn-secondary">
                  Team Calendar
                </Link>
              </div>
            </div>

            {/* Recent Requests */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Recent Requests</h2>
                <Link to="/leave/history" className="text-primary hover:underline text-sm">
                  View all →
                </Link>
              </div>

              <div className="card overflow-hidden">
                {requests?.items && requests.items.length > 0 ? (
                  <div className="divide-y divide-gray-200 dark:divide-gray-700">
                    {requests.items.slice(0, 5).map((request) => (
                      <div
                        key={request.id}
                        className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition flex items-center justify-between"
                      >
                        <div>
                          <p className="font-medium">{request.leave_type}</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            {format(new Date(request.start_date), 'MMM dd')} -{' '}
                            {format(new Date(request.end_date), 'MMM dd, yyyy')}
                          </p>
                        </div>
                        <div className="text-right">
                          <span
                            className={`badge ${
                              request.status === 'APPROVED'
                                ? 'badge-success'
                                : request.status === 'REJECTED'
                                  ? 'badge-error'
                                  : 'badge-warning'
                            }`}
                          >
                            {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                    <p>No leave requests yet</p>
                    <Link to="/leave/apply" className="text-primary hover:underline text-sm mt-2 inline-block">
                      Create one now →
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Balance Card */}
          <div>
            <BalanceCard variant="full" />
          </div>
        </div>
      </div>
    </div>
  );
}
