/**
 * Token Storage Abstraction
 * 
 * Stores JWT tokens in memory (secure against XSS, but lost on refresh).
 * For production, consider httpOnly cookies issued by the backend.
 */

let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(access: string, refresh: string): void {
  accessToken = access;
  refreshToken = refresh;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getRefreshToken(): string | null {
  return refreshToken;
}

export function clearTokens(): void {
  accessToken = null;
  refreshToken = null;
}

export async function refreshAccessToken(): Promise<string> {
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch(`${(import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    accessToken = data.access_token;
    refreshToken = data.refresh_token || refreshToken;

    return accessToken || '';
  } catch (error) {
    clearTokens();
    throw error;
  }
}
