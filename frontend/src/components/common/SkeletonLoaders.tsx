/**
 * Skeleton Loaders
 * 
 * Consistent skeleton loading states for better perceived performance
 */

/**
 * Table skeleton loader
 */
export function TableSkeleton({ rows = 5, columns = 6 }: { rows?: number; columns?: number }) {
  return (
    <div className="animate-pulse">
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 flex gap-4">
        {Array.from({ length: columns }).map((_, idx) => (
          <div key={idx} className="h-4 bg-gray-200 dark:bg-gray-600 rounded flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {Array.from({ length: rows }).map((_, rowIdx) => (
          <div key={rowIdx} className="px-4 py-3 flex gap-4">
            {Array.from({ length: columns }).map((_, colIdx) => (
              <div key={colIdx} className="h-4 bg-gray-200 dark:bg-gray-600 rounded flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Card skeleton loader
 */
export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse">
      <div className="h-6 bg-gray-200 dark:bg-gray-600 rounded w-1/3 mb-4" />
      {Array.from({ length: lines }).map((_, idx) => (
        <div
          key={idx}
          className={`h-4 bg-gray-200 dark:bg-gray-600 rounded mb-3 ${
            idx === lines - 1 ? 'w-2/3' : 'w-full'
          }`}
        />
      ))}
    </div>
  );
}

/**
 * List item skeleton loader
 */
export function ListItemSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx} className="p-4 flex items-center justify-between animate-pulse">
          <div className="flex-1">
            <div className="h-5 bg-gray-200 dark:bg-gray-600 rounded w-1/3 mb-2" />
            <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-1/2" />
          </div>
          <div className="h-6 bg-gray-200 dark:bg-gray-600 rounded w-20" />
        </div>
      ))}
    </div>
  );
}

/**
 * Form skeleton loader
 */
export function FormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {Array.from({ length: 4 }).map((_, idx) => (
        <div key={idx}>
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-24 mb-2" />
          <div className="h-10 bg-gray-200 dark:bg-gray-600 rounded w-full" />
        </div>
      ))}
      <div className="h-10 bg-gray-200 dark:bg-gray-600 rounded w-32" />
    </div>
  );
}

/**
 * Stats grid skeleton loader
 */
export function StatsGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-2/3 mb-3" />
          <div className="h-8 bg-gray-200 dark:bg-gray-600 rounded w-1/2" />
        </div>
      ))}
    </div>
  );
}
