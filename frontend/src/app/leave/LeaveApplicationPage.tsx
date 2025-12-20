/**
 * Leave Application Page
 *
 * Form for employees to apply for leave.
 */

import { useNavigate } from 'react-router-dom';
import { LeaveForm } from '@/features/leave/components/LeaveForm';
import { useLeaveBalance } from '@/features/leave/hooks/useLeaveRequests';

export function LeaveApplicationPage() {
  const navigate = useNavigate();
  const { data: balance, isLoading: isBalanceLoading } = useLeaveBalance();

  const handleSuccess = () => {
    // Redirect to history after successful submission
    setTimeout(() => {
      navigate('/leave/history');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Apply for Leave</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Submit a new leave request. Your manager will review and approve it.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Form */}
          <div className="md:col-span-2 card">
            <LeaveForm onSuccess={handleSuccess} />
          </div>

          {/* Sidebar: Quick Info */}
          <div className="space-y-4">
            {/* Balance Summary */}
            <div className="card">
              <h3 className="font-semibold mb-4">Your Balance</h3>
              {isBalanceLoading ? (
                <p className="text-gray-500 dark:text-gray-400">Loading...</p>
              ) : balance ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Available</p>
                    <p className="text-3xl font-bold text-success">{balance.available}</p>
                  </div>
                  <hr className="dark:border-gray-700" />
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Used</p>
                      <p className="text-lg font-semibold">{balance.used}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Pending</p>
                      <p className="text-lg font-semibold text-warning">{balance.pending}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-error">Unable to load balance</p>
              )}
            </div>

            {/* Tips */}
            <div className="card bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <h3 className="font-semibold mb-3 text-sm">💡 Tips</h3>
              <ul className="text-sm space-y-2 text-gray-700 dark:text-gray-300">
                <li>• Apply in advance when possible</li>
                <li>• Provide a clear reason</li>
                <li>• Check balance before applying</li>
                <li>• Your manager will notify you</li>
              </ul>
            </div>

            {/* Help */}
            <div className="card">
              <h3 className="font-semibold mb-2 text-sm">Need Help?</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                Contact your HR department for questions about leave policies.
              </p>
              <a href="/audit" className="text-sm text-primary hover:underline">
                View my history →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
