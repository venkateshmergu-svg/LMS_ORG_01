/**
 * Approvals Page
 */

import { ApprovalQueue } from '@/features/approvals/components/ApprovalQueue';

export function ApprovalsPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">Pending Approvals</h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Review and approve leave requests from your team members.
          </p>
        </div>

        <ApprovalQueue pageSize={10} />
      </div>
    </div>
  );
}
