/**
 * Approval Detail Modal
 *
 * Modal dialog for approving/rejecting a leave request.
 * Allows manager to add comments when taking action.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { XIcon } from 'lucide-react';

interface ApprovalDetailModalProps {
  isOpen: boolean;
  approval: {
    id: string;
    employeeName: string;
    startDate: string;
    endDate: string;
    days: number;
    reason: string;
  };
  onApprove: (comments?: string) => void;
  onReject: (comments: string) => void;
  isLoading: boolean;
  onClose: () => void;
}

interface ActionFormData {
  comments: string;
}

export function ApprovalDetailModal({
  isOpen,
  approval,
  onApprove,
  onReject,
  isLoading,
  onClose,
}: ApprovalDetailModalProps) {
  const [action, setAction] = useState<'approve' | 'reject' | null>(null);
  const { register, handleSubmit, watch, reset, formState: { errors } } = useForm<ActionFormData>({
    defaultValues: {
      comments: '',
    },
  });

  const comments = watch('comments');

  const handleApproveSubmit = () => {
    onApprove(comments || undefined);
    reset();
    setAction(null);
  };

  const handleRejectSubmit = () => {
    if (!comments.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    onReject(comments);
    reset();
    setAction(null);
  };

  const handleCloseModal = () => {
    reset();
    setAction(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div>
            <h2 className="text-2xl font-bold">Review Leave Request</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              From: {approval.employeeName}
            </p>
          </div>
          <button
            onClick={handleCloseModal}
            disabled={isLoading}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition"
          >
            <XIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Request Details */}
          <div className="space-y-4">
            <h3 className="font-semibold">Request Details</h3>
            <div className="grid grid-cols-2 gap-4">
              {/* Employee Name */}
              <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Employee</p>
                <p className="font-medium">{approval.employeeName}</p>
              </div>

              {/* Days */}
              <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Days Requested</p>
                <p className="font-medium text-lg">{approval.days}</p>
              </div>

              {/* Start Date */}
              <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Start Date</p>
                <p className="font-medium">
                  {new Date(approval.startDate).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </p>
              </div>

              {/* End Date */}
              <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">End Date</p>
                <p className="font-medium">
                  {new Date(approval.endDate).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </p>
              </div>
            </div>

            {/* Reason */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded border border-blue-200 dark:border-blue-800">
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Reason for Leave</p>
              <p className="text-gray-900 dark:text-white">{approval.reason}</p>
            </div>
          </div>

          {/* Action Selection */}
          {!action ? (
            <div className="space-y-3">
              <p className="text-sm font-medium">What would you like to do?</p>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setAction('approve')}
                  className="btn btn-success"
                  disabled={isLoading}
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => setAction('reject')}
                  className="btn btn-error"
                  disabled={isLoading}
                >
                  ✕ Reject
                </button>
              </div>
            </div>
          ) : (
            // Action Form
            <form
              onSubmit={handleSubmit(
                action === 'approve' ? handleApproveSubmit : handleRejectSubmit
              )}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium mb-2">
                  {action === 'approve'
                    ? 'Comments (Optional)'
                    : 'Reason for Rejection (Required)'}
                </label>
                <textarea
                  {...register('comments', {
                    required: action === 'reject' ? 'Rejection reason is required' : false,
                    minLength:
                      action === 'reject'
                        ? { value: 10, message: 'Please provide at least 10 characters' }
                        : undefined,
                    maxLength: { value: 500, message: 'Maximum 500 characters' },
                  })}
                  placeholder={
                    action === 'approve'
                      ? 'Add any approval notes...'
                      : 'Explain why you are rejecting this request...'
                  }
                  className="input h-32 resize-none"
                />
                {errors.comments && (
                  <p className="text-error text-xs mt-1">{errors.comments.message}</p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {comments.length}/500 characters
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setAction(null);
                    reset();
                  }}
                  disabled={isLoading}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading || (action === 'reject' && !comments.trim())}
                  className={`btn ${action === 'approve' ? 'btn-success' : 'btn-error'}`}
                >
                  {isLoading
                    ? action === 'approve'
                      ? 'Approving...'
                      : 'Rejecting...'
                    : action === 'approve'
                      ? 'Confirm Approval'
                      : 'Confirm Rejection'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
