/**
 * Build Version Utilities
 * 
 * Provides access to build-time metadata for release traceability.
 * These values are injected at build time and are immutable.
 * 
 * @module utils/version
 */

export interface BuildInfo {
  /** Semantic version (e.g., "1.2.3") */
  version: string;
  /** Git commit SHA (short or full) */
  commit: string;
  /** ISO 8601 build timestamp */
  buildDate: string;
  /** CI build number */
  buildNumber: string;
  /** Build mode (development, production, test, etc.) */
  mode: string;
  /** Human-readable build timestamp */
  formattedDate: string;
  /** Full version string for display */
  fullVersion: string;
}

/**
 * Get complete build information
 */
export function getBuildInfo(): BuildInfo {
  const version = __BUILD_VERSION__;
  const commit = __BUILD_COMMIT__;
  const buildDate = __BUILD_DATE__;
  const buildNumber = __BUILD_NUMBER__;
  const mode = __BUILD_MODE__;

  // Format date for human readability
  let formattedDate: string;
  try {
    formattedDate = new Date(buildDate).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  } catch {
    formattedDate = buildDate;
  }

  // Create full version string (e.g., "1.2.3+abc123.456")
  const shortCommit = commit.substring(0, 7);
  const fullVersion = `${version}+${shortCommit}.${buildNumber}`;

  return {
    version,
    commit,
    buildDate,
    buildNumber,
    mode,
    formattedDate,
    fullVersion,
  };
}

/**
 * Get version string for display in UI footer
 */
export function getVersionString(): string {
  const { version, commit, mode } = getBuildInfo();
  const shortCommit = commit.substring(0, 7);
  
  if (mode === 'production') {
    return `v${version}`;
  }
  
  return `v${version} (${shortCommit})`;
}

/**
 * Get detailed version info for admin/debug pages
 */
export function getDetailedVersionInfo(): string {
  const info = getBuildInfo();
  return [
    `Version: ${info.version}`,
    `Commit: ${info.commit}`,
    `Build: #${info.buildNumber}`,
    `Date: ${info.formattedDate}`,
    `Mode: ${info.mode}`,
  ].join('\n');
}

/**
 * Log build info to console (useful for debugging)
 */
export function logBuildInfo(): void {
  const info = getBuildInfo();
  console.info(
    '%c🏗️ LMS Frontend Build Info',
    'font-weight: bold; font-size: 14px;'
  );
  console.table({
    Version: info.version,
    Commit: info.commit,
    'Build Number': info.buildNumber,
    'Build Date': info.formattedDate,
    Mode: info.mode,
  });
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return __BUILD_MODE__ === 'development';
}

/**
 * Check if running in production mode
 */
export function isProduction(): boolean {
  return __BUILD_MODE__ === 'production';
}

/**
 * Get environment-specific configuration
 */
export function getEnvironmentConfig() {
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
    oauthClientId: import.meta.env.VITE_OAUTH_CLIENT_ID,
    oauthAuthority: import.meta.env.VITE_OAUTH_AUTHORITY,
    oauthRedirectUri: import.meta.env.VITE_OAUTH_REDIRECT_URI,
    appName: import.meta.env.VITE_APP_NAME,
    supportEmail: import.meta.env.VITE_SUPPORT_EMAIL,
    features: {
      calendarSync: import.meta.env.VITE_FEATURE_CALENDAR_SYNC === 'true',
      hrisIntegration: import.meta.env.VITE_FEATURE_HRIS_INTEGRATION === 'true',
      payrollExport: import.meta.env.VITE_FEATURE_PAYROLL_EXPORT === 'true',
      advancedReports: import.meta.env.VITE_FEATURE_ADVANCED_REPORTS === 'true',
    },
  };
}
