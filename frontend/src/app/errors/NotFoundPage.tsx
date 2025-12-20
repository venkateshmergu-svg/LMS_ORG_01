/**
 * Not Found (404) Error Page
 */

import { useNavigate } from 'react-router-dom';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-400 mb-2">404</h1>
        <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}
