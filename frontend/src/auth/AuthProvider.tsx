/**
 * Auth Context & Provider
 *
 * Manages authentication state, user profile, and role-based access control.
 */
/* eslint-disable react-refresh/only-export-components */

import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { clearTokens, getAccessToken, setTokens } from './tokens';

export interface User {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';

  const normalizeUser = (raw: User): User => ({
    ...raw,
    roles: (raw.roles ?? []).map((r) => r.toUpperCase()),
  });

  // Initialize auth on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();
      if (token) {
        try {
          const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(normalizeUser(userData));
          } else if (response.status === 401) {
            clearTokens();
            setUser(null);
          }
        } catch (err) {
          console.error('Auth init failed:', err);
          setError('Failed to initialize authentication');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [apiBaseUrl]);

  const login = async (accessToken: string, refreshToken: string) => {
    try {
      setTokens(accessToken, refreshToken);

      const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const userData = await response.json();
      setUser(normalizeUser(userData));
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      clearTokens();
      throw err;
    }
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    window.location.href = '/login';
  };

  const hasRole = (role: string): boolean => {
    return user?.roles.includes(role) ?? false;
  };

  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some((role) => user?.roles.includes(role)) ?? false;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        logout,
        hasRole,
        hasAnyRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
