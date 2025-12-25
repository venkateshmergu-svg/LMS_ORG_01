/**
 * Leave Application Form
 *
 * Form for employees to request leave with validation and balance checking.
 */

import { useCreateLeaveRequest, useLeaveBalance } from '@/features/leave/hooks/useLeaveRequests';
import { differenceInDays } from 'date-fns';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';

interface LeaveFormData {
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
}

interface LeaveFormProps {
  onSuccess?: () => void;
}

export function LeaveForm({ onSuccess }: LeaveFormProps) {
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<LeaveFormData>({
    defaultValues: {
      leave_type: 'ANNUAL',
      start_date: '',
      end_date: '',
      reason: '',
    },
  });

  const { data: balance, isLoading: isBalanceLoading } = useLeaveBalance();
  const { mutate, isPending, error } = useCreateLeaveRequest();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const startDate = watch('start_date');
  const endDate = watch('end_date');
  const reasonText = watch('reason');

  // Calculate days requested
  const daysRequested =
    startDate && endDate ? differenceInDays(new Date(endDate), new Date(startDate)) + 1 : 0;

  // Get available balance for selected leave type
  const availableDays = balance?.available || 0;
  const insufficientBalance = daysRequested > availableDays && daysRequested > 0;

  const onSubmit = (data: LeaveFormData) => {
    if (insufficientBalance) {
      return;
    }

    mutate(data, {
      onSuccess: () => {
        setSuccessMessage('Leave request submitted successfully!');
        reset();
        onSuccess?.();
      },
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
          <p className="text-green-800 dark:text-green-200 font-medium">✓ {successMessage}</p>
        </div>
      )}

      {/* Leave Type */}
      <div>
        <label className="block text-sm font-medium mb-2">Leave Type *</label>
        <Controller
          name="leave_type"
          control={control}
          rules={{ required: 'Leave type is required' }}
          render={({ field }) => (
            <select {...field} className="input">
              <option value="ANNUAL">Annual Leave</option>
              <option value="SICK">Sick Leave</option>
              <option value="PERSONAL">Personal Leave</option>
              <option value="UNPAID">Unpaid Leave</option>
            </select>
          )}
        />
        {errors.leave_type && (
          <p className="text-error text-sm mt-1">✗ {errors.leave_type.message}</p>
        )}
      </div>

      {/* Date Range */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Start Date *</label>
          <Controller
            name="start_date"
            control={control}
            rules={{
              required: 'Start date is required',
              validate: (value) => {
                const selectedDate = new Date(value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                return selectedDate >= today || 'Cannot apply for past dates';
              },
            }}
            render={({ field }) => <input {...field} type="date" className="input" />}
          />
          {errors.start_date && (
            <p className="text-error text-sm mt-1">✗ {errors.start_date.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">End Date *</label>
          <Controller
            name="end_date"
            control={control}
            rules={{
              required: 'End date is required',
              validate: (value) => {
                if (!startDate) return true;
                return (
                  new Date(value) >= new Date(startDate) ||
                  'End date must be on or after start date'
                );
              },
            }}
            render={({ field }) => <input {...field} type="date" className="input" />}
          />
          {errors.end_date && (
            <p className="text-error text-sm mt-1">✗ {errors.end_date.message}</p>
          )}
        </div>
      </div>

      {/* Balance Summary */}
      {daysRequested > 0 && (
        <div
          className={`p-4 rounded-lg ${
            insufficientBalance
              ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
              : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
          }`}
        >
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Days Requested</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">{daysRequested}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Available</p>
              <p
                className={`text-lg font-bold ${
                  insufficientBalance
                    ? 'text-error'
                    : 'text-success'
                }`}
              >
                {isBalanceLoading ? '...' : availableDays}
              </p>
            </div>
          </div>

          {insufficientBalance && (
            <p className="text-sm text-error font-medium">
              ⚠️ Insufficient balance. You need {daysRequested - availableDays} more days.
            </p>
          )}
        </div>
      )}

      {/* Reason */}
      <div>
        <label className="block text-sm font-medium mb-2">Reason for Leave *</label>
        <Controller
          name="reason"
          control={control}
          rules={{
            required: 'Please provide a reason for your leave',
            minLength: { value: 10, message: 'Please provide at least 10 characters' },
          }}
          render={({ field }) => (
            <textarea
              {...field}
              rows={4}
              className="input"
              placeholder="Explain why you're taking leave..."
            />
          )}
        />
        {errors.reason && (
          <p className="text-error text-sm mt-1">✗ {errors.reason.message}</p>
        )}
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {reasonText?.length || 0} / 1000 characters
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
          <p className="text-error text-sm font-medium">✗ {error.message}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isPending || insufficientBalance || isBalanceLoading}
          className="flex-1 btn btn-primary"
        >
          {isPending ? 'Submitting...' : 'Submit Application'}
        </button>
        <button type="reset" className="flex-1 btn btn-secondary">
          Clear Form
        </button>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
        * Required fields. Your request will be sent to your manager for approval.
      </p>
    </form>
  );
}
