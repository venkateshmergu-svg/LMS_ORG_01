/**
 * Version Display Component
 *
 * Displays build version information in the UI.
 * Used in footer and admin pages for release traceability.
 *
 * @module components/common/VersionDisplay
 */

import { useState } from 'react';
import { getBuildInfo, getVersionString, type BuildInfo } from '@/utils/version';

interface VersionDisplayProps {
  /** Show detailed info on click */
  expandable?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Display variant */
  variant?: 'minimal' | 'compact' | 'full';
}

/**
 * Version badge for footer/status bar
 */
export function VersionDisplay({
  expandable = false,
  className = '',
  variant = 'minimal',
}: VersionDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);
  const info = getBuildInfo();

  const handleClick = () => {
    if (expandable) {
      setShowDetails(!showDetails);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (expandable && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      setShowDetails(!showDetails);
    }
  };

  if (variant === 'minimal') {
    return (
      <span
        className={`text-xs text-gray-500 ${expandable ? 'cursor-pointer hover:text-gray-700' : ''} ${className}`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role={expandable ? 'button' : undefined}
        tabIndex={expandable ? 0 : undefined}
        aria-expanded={expandable ? showDetails : undefined}
        title={`Build: ${info.fullVersion}`}
      >
        {getVersionString()}
      </span>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`text-xs text-gray-500 ${className}`}>
        <span className="font-medium">v{info.version}</span>
        <span className="mx-1">•</span>
        <span className="font-mono">{info.commit.substring(0, 7)}</span>
      </div>
    );
  }

  // Full variant
  return (
    <div className={`text-sm ${className}`}>
      <div className="flex items-center gap-2">
        <span className="font-medium text-gray-700">Version {info.version}</span>
        {info.mode !== 'production' && (
          <span className="px-2 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded-full">
            {info.mode}
          </span>
        )}
      </div>
      <div className="mt-1 text-xs text-gray-500 font-mono">Commit: {info.commit}</div>
      <div className="text-xs text-gray-500">Built: {info.formattedDate}</div>
    </div>
  );
}

/**
 * Detailed version info panel for admin pages
 */
export function VersionInfoPanel({ className = '' }: { className?: string }) {
  const info: BuildInfo = getBuildInfo();

  return (
    <div className={`bg-gray-50 rounded-lg p-4 border border-gray-200 ${className}`}>
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Build Information</h3>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <dt className="text-gray-500">Version</dt>
        <dd className="font-mono text-gray-900">{info.version}</dd>

        <dt className="text-gray-500">Commit</dt>
        <dd className="font-mono text-gray-900">{info.commit}</dd>

        <dt className="text-gray-500">Build Number</dt>
        <dd className="font-mono text-gray-900">#{info.buildNumber}</dd>

        <dt className="text-gray-500">Build Date</dt>
        <dd className="text-gray-900">{info.formattedDate}</dd>

        <dt className="text-gray-500">Environment</dt>
        <dd className="text-gray-900 capitalize">{info.mode}</dd>

        <dt className="text-gray-500">Full Version</dt>
        <dd className="font-mono text-gray-900 text-xs">{info.fullVersion}</dd>
      </dl>
    </div>
  );
}

export default VersionDisplay;
