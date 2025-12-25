/**
 * OAuth2 Configuration & Utilities
 */

export const oauthConfig = {
  clientId: (import.meta.env.VITE_OAUTH_CLIENT_ID as string) || '',
  authority: (import.meta.env.VITE_OAUTH_AUTHORITY as string) || '',
  redirectUri: `${window.location.origin}/auth/callback`,
  scopes: ['openid', 'profile', 'email'],
};

/**
 * Generate authorization URL for OAuth provider
 */
export function getAuthorizationUrl(): string {
  // Local-dev fallback: if no external authority/clientId is configured,
  // short-circuit to an internal callback route that the backend accepts.
  if (!oauthConfig.authority || !oauthConfig.clientId) {
    return `${window.location.origin}/auth/callback?code=dev`;
  }

  const params = new URLSearchParams({
    client_id: oauthConfig.clientId,
    redirect_uri: oauthConfig.redirectUri,
    response_type: 'code',
    scope: oauthConfig.scopes.join(' '),
    state: generateRandomState(),
  });

  return `${oauthConfig.authority}/authorize?${params.toString()}`;
}

/**
 * Generate random state for CSRF protection
 */
export function generateRandomState(): string {
  return Math.random().toString(36).substring(2, 15);
}

/**
 * Exchange authorization code for tokens
 */
export async function exchangeCodeForTokens(code: string): Promise<{
  access_token: string;
  refresh_token: string;
  token_type: string;
}> {
  const response = await fetch(`${(import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      client_id: oauthConfig.clientId,
      redirect_uri: oauthConfig.redirectUri,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || errorData.message || 'Token exchange failed'
    );
  }

  return response.json();
}
