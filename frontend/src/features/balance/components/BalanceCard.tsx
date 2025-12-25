/**
 * Balance Card Component
 *
 * Displays leave balance breakdown with visual progress bars.
 * Shows available, used, and pending days.
 * 
 * Performance optimizations:
 * - Memoized to prevent unnecessary re-renders
 * - useMemo for computed percentage values
 * - useCallback for event handlers
 */

import { useLeaveBalance } from '@/features/leave/hooks/useLeaveRequests';
import { RefreshCw } from 'lucide-react';
import { memo, useCallback, useMemo } from 'react';

interface BalanceCardProps {
  variant?: 'compact' | 'full';
  onRefresh?: () => void;
}

export const BalanceCard = memo(function BalanceCard({ variant = 'full', onRefresh }: BalanceCardProps) {
  const { data: balance, isLoading, refetch, isFetching } = useLeaveBalance();

  // Memoize refresh handler
  const handleRefresh = useCallback(() => {
    refetch();
    onRefresh?.();
  }, [refetch, onRefresh]);

  // Memoize percentage calculations
  const percentages = useMemo(() => {
    if (!balance) return { used: 0, pending: 0, available: 100 };
    
    const total = balance.available + balance.used + balance.pending;
    const usedPercent = total > 0 ? (balance.used / total) * 100 : 0;
    const pendingPercent = total > 0 ? (balance.pending / total) * 100 : 0;
    const availablePercent = 100 - usedPercent - pendingPercent;
    
    return { 
      used: usedPercent, 
      pending: pendingPercent, 
      available: availablePercent,
      total 
    };
  }, [balance]);

  if (isLoading) {
    return (
      <div className={`card animate-pulse ${variant === 'compact' ? 'p-4' : 'p-6'}`}>
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4 w-24" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (!balance) {
    return (
      <div className={`card ${variant === 'compact' ? 'p-4' : 'p-6'}`}>
        <p className="text-error">Unable to load balance</p>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-sm">Leave Balance</h3>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Available</span>
            <span className="font-bold text-success">{balance.available}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-success h-2 rounded-full transition-all"
              style={{ width: `${percentages.available}%` }}
            />
          </div>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">Used</p>
            <p className="font-semibold">{balance.used}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">Pending</p>
            <p className="font-semibold text-warning">{balance.pending}</p>
          </div>
        </div>
      </div>
    );
  }

  // Full variant
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold">Leave Balance</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {percentages.total} days total annual leave
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isFetching}
          className="btn btn-sm btn-secondary"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          {isFetching ? 'Updating...' : 'Refresh'}
        </button>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex h-8 rounded-lg overflow-hidden bg-gray-200 dark:bg-gray-700">
          {/* Available */}
          <div
            className="bg-success flex items-center justify-center transition-all"
            style={{ width: `${percentages.available}%` }}
            title={`Available: ${balance.available}`}
          >
            {percentages.available > 15 && (
              <span className="text-white text-xs font-semibold">{balance.available}</span>
            )}
          </div>

          {/* Pending */}
          <div
            className="bg-warning flex items-center justify-center transition-all"
            style={{ width: `${percentages.pending}%` }}
            title={`Pending: ${balance.pending}`}
          >
            {percentages.pending > 15 && (
              <span className="text-white text-xs font-semibold">{balance.pending}</span>
            )}
          </div>

          {/* Used */}
          <div
            className="bg-error flex items-center justify-center transition-all"
            style={{ width: `${percentages.used}%` }}
            title={`Used: ${balance.used}`}
          >
            {percentages.used > 15 && (
              <span className="text-white text-xs font-semibold">{balance.used}</span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Available */}
        <div className="bg-success/10 dark:bg-success/20 p-4 rounded-lg border border-success/20">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-medium mb-2">AVAILABLE</p>
          <p className="text-3xl font-bold text-success">{balance.available}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Ready to use</p>
        </div>

        {/* Pending */}
        <div className="bg-warning/10 dark:bg-warning/20 p-4 rounded-lg border border-warning/20">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-medium mb-2">PENDING</p>
          <p className="text-3xl font-bold text-warning">{balance.pending}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Awaiting approval</p>
        </div>

        {/* Used */}
        <div className="bg-error/10 dark:bg-error/20 p-4 rounded-lg border border-error/20">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-medium mb-2">USED</p>
          <p className="text-3xl font-bold text-error">{balance.used}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Already used</p>
        </div>
      </div>

      {/* Info */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        {balance.available === 0 && (
          <div className="bg-error/10 dark:bg-error/20 p-3 rounded border border-error/20">
            <p className="text-sm text-error font-medium">⚠️ No leave available</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              Wait for pending requests to be approved or use to be processed.
            </p>
          </div>
        )}
        {balance.pending > 0 && (
          <div className="bg-warning/10 dark:bg-warning/20 p-3 rounded border border-warning/20">
            <p className="text-sm text-warning font-medium">⏳ {balance.pending} day(s) pending</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              Awaiting manager approval
            </p>
          </div>
        )}
        {balance.available > 0 && balance.pending === 0 && (
          <div className="bg-success/10 dark:bg-success/20 p-3 rounded border border-success/20">
            <p className="text-sm text-success font-medium">✓ Balance available</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              You can apply for up to {balance.available} more days
            </p>
          </div>
        )}
      </div>
    </div>
  );
});
