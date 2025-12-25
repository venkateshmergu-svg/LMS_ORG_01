/**
 * Main App Component
 * 
 * Sets up providers (Auth, ReactQuery, Router) and defines routes
 * Enhanced with lazy loading for better performance
 * 
 * Performance optimizations:
 * - Critical paths (login, dashboard) are eagerly loaded
 * - Non-critical pages use lazy loading for code splitting
 * - Suspense boundaries provide loading feedback
 */

import { AuthProvider } from '@/auth/AuthProvider';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { queryClient } from '@/lib/react-query';
import { QueryClientProvider } from '@tanstack/react-query';
import { Suspense, lazy, memo } from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

// Eager loaded pages (critical path - login and dashboard)
import { CallbackPage } from '@/app/auth/CallbackPage';
import { DashboardPage } from '@/app/dashboard/DashboardPage';
import { NotFoundPage } from '@/app/errors/NotFoundPage';
import { UnauthorizedPage } from '@/app/errors/UnauthorizedPage';
import { LoginPage } from '@/app/login/LoginPage';

// Lazy loaded pages (non-critical, code-split for better initial load)
const LeaveApplicationPage = lazy(() => 
  import('@/app/leave/LeaveApplicationPage').then(m => ({ default: m.LeaveApplicationPage }))
);
const LeaveHistoryPage = lazy(() => 
  import('@/app/leave/LeaveHistoryPage').then(m => ({ default: m.LeaveHistoryPage }))
);
const ApprovalsPage = lazy(() => 
  import('@/app/approvals/ApprovalsPage').then(m => ({ default: m.ApprovalsPage }))
);
const CalendarPage = lazy(() => 
  import('@/app/calendar/CalendarPage').then(m => ({ default: m.CalendarPage }))
);
const ReportsPage = lazy(() => 
  import('@/app/reports/ReportsPage').then(m => ({ default: m.ReportsPage }))
);
const AuditPage = lazy(() => 
  import('@/app/audit/AuditPage').then(m => ({ default: m.AuditPage }))
);

// Memoized loading fallback to prevent re-renders
const PageLoadingFallback = memo(function PageLoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading page...</p>
      </div>
    </div>
  );
});

// Wrapper for lazy loaded routes with Suspense
const LazyRoute = memo(function LazyRoute({ 
  children, 
  requiredRoles 
}: { 
  children: React.ReactNode; 
  requiredRoles?: string[];
}) {
  return (
    <ProtectedRoute requiredRoles={requiredRoles}>
      <Suspense fallback={<PageLoadingFallback />}>
        {children}
      </Suspense>
    </ProtectedRoute>
  );
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/auth/callback" element={<CallbackPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Protected routes - Dashboard is eagerly loaded */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Lazy loaded protected routes */}
            <Route
              path="/leave/apply"
              element={
                <LazyRoute requiredRoles={['EMPLOYEE', 'MANAGER']}>
                  <LeaveApplicationPage />
                </LazyRoute>
              }
            />

            <Route
              path="/leave/application"
              element={
                <LazyRoute requiredRoles={['EMPLOYEE', 'MANAGER']}>
                  <Navigate to="/leave/apply" replace />
                </LazyRoute>
              }
            />

            <Route
              path="/leave/history"
              element={
                <LazyRoute requiredRoles={['EMPLOYEE', 'MANAGER', 'HR_ADMIN']}>
                  <LeaveHistoryPage />
                </LazyRoute>
              }
            />

            <Route
              path="/approvals"
              element={
                <LazyRoute requiredRoles={['MANAGER', 'HR_ADMIN']}>
                  <ApprovalsPage />
                </LazyRoute>
              }
            />

            <Route
              path="/calendar"
              element={
                <LazyRoute requiredRoles={['MANAGER', 'HR_ADMIN']}>
                  <CalendarPage />
                </LazyRoute>
              }
            />

            <Route
              path="/reports"
              element={
                <LazyRoute requiredRoles={['HR_ADMIN']}>
                  <ReportsPage />
                </LazyRoute>
              }
            />

            <Route
              path="/audit"
              element={
                <LazyRoute requiredRoles={['AUDITOR', 'HR_ADMIN', 'SYSTEM_ADMIN']}>
                  <AuditPage />
                </LazyRoute>
              }
            />

            {/* Fallback */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}
