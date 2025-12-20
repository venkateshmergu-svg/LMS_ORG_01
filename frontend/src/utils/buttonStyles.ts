/**
 * Button Style Utilities
 * 
 * Consistent button styling hierarchy across the application
 */

/**
 * Primary action button (main CTAs)
 */
export const buttonPrimary = 
  'px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

/**
 * Secondary action button
 */
export const buttonSecondary = 
  'px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

/**
 * Destructive action button (delete, reject, withdraw)
 */
export const buttonDestructive = 
  'px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

/**
 * Text/link button (subtle actions)
 */
export const buttonText = 
  'text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

/**
 * Small icon button
 */
export const buttonIcon = 
  'p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors';
