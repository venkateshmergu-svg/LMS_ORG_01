/**
 * Login Page
 *
 * OAuth2/OIDC login form.
 * Redirects to OAuth provider for authentication.
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/auth/AuthProvider';
import { getAuthorizationUrl } from '@/lib/oauth';

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  const handleOAuthLogin = () => {
    try {
      const authUrl = getAuthorizationUrl();
      window.location.href = authUrl;
    } catch (error) {
      console.error('Failed to start OAuth flow:', error);
      alert('Unable to start login. Please try again later.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">
      <div className="max-w-md w-full card shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 text-primary">LMS</h1>
          <p className="text-gray-600 dark:text-gray-300 font-medium">Leave Management System</p>
        </div>

        <p className="text-center text-gray-600 dark:text-gray-300 mb-6">
          Sign in with your organization account to manage your leave.
        </p>

        <button onClick={handleOAuthLogin} className="w-full btn btn-primary text-lg py-3 font-medium">
          🔐 Sign in with OAuth2
        </button>

        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            You will be redirected to your organization's identity provider to securely authenticate.
          </p>
        </div>
      </div>
    </div>
  );
}
