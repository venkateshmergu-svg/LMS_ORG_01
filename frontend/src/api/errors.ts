/**
 * API Error Mapping
 *
 * Converts HTTP errors to user-friendly messages for UI consumption.
 */

import { AxiosError } from 'axios';

export interface APIError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, string>;
}

export function mapAPIError(error: unknown): APIError {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const data = error.response?.data as Record<string, unknown>;
    const detail = (data?.detail as string) || (data?.message as string);

    switch (status) {
      case 400:
        return {
          code: 'VALIDATION_ERROR',
          message: detail || 'Please check your input and try again.',
          field: data?.field as string | undefined,
          details: data?.errors as Record<string, string> | undefined,
        };

      case 401:
        return {
          code: 'UNAUTHORIZED',
          message: 'Your session has expired. Please log in again.',
        };

      case 403:
        return {
          code: 'FORBIDDEN',
          message: 'You do not have permission to perform this action.',
        };

      case 404:
        return {
          code: 'NOT_FOUND',
          message: detail || 'The requested resource was not found.',
        };

      case 409:
        return {
          code: 'CONFLICT',
          message: detail || 'This action conflicts with existing data.',
        };

      case 422:
        return {
          code: 'VALIDATION_ERROR',
          message: 'Validation failed.',
          details: data?.errors as Record<string, string> | undefined,
        };

      case 500:
      case 502:
      case 503:
      case 504:
        return {
          code: 'SERVER_ERROR',
          message:
            'An unexpected error occurred. Our team has been notified. Please try again later.',
        };

      default:
        return {
          code: 'UNKNOWN_ERROR',
          message: error.message || 'An unexpected error occurred.',
        };
    }
  }

  if (error instanceof Error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message,
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred.',
  };
}

/**
 * Get user-friendly message for error code
 */
export function getErrorMessage(errorCode: string): string {
  const messages: Record<string, string> = {
    VALIDATION_ERROR: 'Please check your input and try again.',
    UNAUTHORIZED: 'Your session has expired. Please log in again.',
    FORBIDDEN: 'You do not have permission for this action.',
    NOT_FOUND: 'The requested resource was not found.',
    CONFLICT: 'This action conflicts with existing data.',
    SERVER_ERROR: 'An unexpected error occurred. Please try again later.',
    UNKNOWN_ERROR: 'Something went wrong. Please try again.',
  };

  return messages[errorCode] || 'An error occurred.';
}
