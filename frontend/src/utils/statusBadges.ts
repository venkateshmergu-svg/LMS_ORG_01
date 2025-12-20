/**
 * Status Badge Utilities
 * 
 * Consistent status badge styling across the application
 */

/**
 * Get Tailwind classes for leave request status badges
 */
export function getLeaveStatusClass(status: string): string {
  const statusUpper = status.toUpperCase();
  
  switch (statusUpper) {
    case 'APPROVED':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'REJECTED':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    case 'WITHDRAWN':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
}

/**
 * Get Tailwind classes for sync/integration status badges
 */
export function getSyncStatusClass(status: string): string {
  const statusUpper = status.toUpperCase();
  
  switch (statusUpper) {
    case 'SUCCESS':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'FAILED':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'IN_PROGRESS':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
}

/**
 * Get Tailwind classes for audit action badges
 */
export function getActionBadgeClass(action: string): string {
  const actionLower = action.toLowerCase();
  
  switch (actionLower) {
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
}
