/**
 * Global type definitions
 */

// ============================================================
// BUILD-TIME CONSTANTS (Injected by Vite at build time)
// ============================================================
declare const __BUILD_VERSION__: string;
declare const __BUILD_COMMIT__: string;
declare const __BUILD_DATE__: string;
declare const __BUILD_NUMBER__: string;
declare const __BUILD_MODE__: string;

// ============================================================
// ENVIRONMENT VARIABLE TYPES
// ============================================================
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_OAUTH_CLIENT_ID: string;
  readonly VITE_OAUTH_AUTHORITY: string;
  readonly VITE_OAUTH_REDIRECT_URI: string;
  readonly VITE_OAUTH_POST_LOGOUT_REDIRECT_URI: string;
  readonly VITE_FEATURE_CALENDAR_SYNC: string;
  readonly VITE_FEATURE_HRIS_INTEGRATION: string;
  readonly VITE_FEATURE_PAYROLL_EXPORT: string;
  readonly VITE_FEATURE_ADVANCED_REPORTS: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_SUPPORT_EMAIL: string;
  readonly VITE_BUILD_VERSION?: string;
  readonly VITE_BUILD_COMMIT?: string;
  readonly VITE_BUILD_DATE?: string;
  readonly VITE_BUILD_NUMBER?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// ============================================================
// APPLICATION TYPES
// ============================================================
export interface LoadingState {
  isLoading: boolean;
  isFetching?: boolean;
  error?: Error | null;
}

export interface MutationState {
  isPending: boolean;
  error?: Error | null;
  data?: any;
}

export type Role = 'EMPLOYEE' | 'MANAGER' | 'HR_ADMIN' | 'AUDITOR' | 'SYSTEM_ADMIN';

