/**
 * Unauthorized (403) Error Page
 */

import { useNavigate } from 'react-router-dom';

export function UnauthorizedPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-error mb-2">403</h1>
        <h2 className="text-2xl font-semibold mb-4">Access Denied</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8 max-w-md">
          You do not have permission to access this resource. If you believe this is an error, please contact your administrator.
        </p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}
