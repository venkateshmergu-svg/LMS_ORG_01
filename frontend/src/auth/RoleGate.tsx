/**
 * Role-Based Component Gating
 *
 * Conditionally renders children based on user roles.
 * Example: <RoleGate requiredRoles={['MANAGER']}>Approve Button</RoleGate>
 */

import { ReactNode } from 'react';
import { useAuth } from './AuthProvider';

interface RoleGateProps {
  children: ReactNode;
  requiredRoles: string[];
  fallback?: ReactNode;
}

export function RoleGate({ children, requiredRoles, fallback = null }: RoleGateProps) {
  const { hasAnyRole } = useAuth();

  if (!hasAnyRole(requiredRoles)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
