/**
 * OAuth Callback Handler
 *
 * Receives authorization code from OAuth provider, exchanges it for tokens,
 * and logs user in.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/auth/AuthProvider';
import { exchangeCodeForTokens } from '@/lib/oauth';

export function CallbackPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Extract authorization code from URL
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const oauthError = params.get('error');
        const errorDescription = params.get('error_description');

        // Check for OAuth errors
        if (oauthError) {
          throw new Error(`${oauthError}: ${errorDescription || 'Authorization denied'}`);
        }

        // Check if code was provided
        if (!code) {
          throw new Error('No authorization code received. Please try logging in again.');
        }

        // Exchange code for tokens
        const tokenData = await exchangeCodeForTokens(code);

        // Login user
        await login(tokenData.access_token, tokenData.refresh_token);

        // Redirect to dashboard
        navigate('/dashboard', { replace: true });
      } catch (err) {
        const friendlyError = err instanceof Error ? err.message : 'Authentication failed';
        setError(friendlyError);
        setIsLoading(false);
      }
    };

    handleCallback();
  }, [login, navigate]);

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <div className="max-w-md w-full card">
          <h1 className="text-2xl font-bold text-error mb-4">Authentication Failed</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-6">{error}</p>
          <div className="space-y-2">
            <button
              onClick={() => (window.location.href = '/login')}
              className="w-full btn btn-primary"
            >
              Back to Login
            </button>
            <a
              href="https://support.example.com"
              className="block text-center btn btn-secondary"
              target="_blank"
              rel="noopener noreferrer"
            >
              Get Help
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Loading state
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="inline-block animate-spin mb-4">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full"></div>
        </div>
        <p className="text-gray-600 dark:text-gray-300 font-medium">Completing sign in...</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Please wait while we verify your credentials.</p>
      </div>
    </div>
  );
}
