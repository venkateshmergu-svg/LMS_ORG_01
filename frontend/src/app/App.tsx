/**
 * Main App Component
 * 
 * Sets up providers (Auth, ReactQuery, Router) and defines routes
 * Enhanced with lazy loading for better performance
 */

import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { queryClient } from '@/lib/react-query';
import { AuthProvider } from '@/auth/AuthProvider';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

// Eager loaded pages (critical path)
import { LoginPage } from '@/app/login/LoginPage';
import { CallbackPage } from '@/app/auth/CallbackPage';
import { DashboardPage } from '@/app/dashboard/DashboardPage';
import { LeaveApplicationPage } from '@/app/leave/LeaveApplicationPage';
import { LeaveHistoryPage } from '@/app/leave/LeaveHistoryPage';
import { ApprovalsPage } from '@/app/approvals/ApprovalsPage';
import { UnauthorizedPage } from '@/app/errors/UnauthorizedPage';
import { NotFoundPage } from '@/app/errors/NotFoundPage';

// Lazy loaded pages (non-critical, heavy components)
const CalendarPage = lazy(() => import('@/app/calendar/CalendarPage').then(m => ({ default: m.CalendarPage })));
const ReportsPage = lazy(() => import('@/app/reports/ReportsPage').then(m => ({ default: m.ReportsPage })));
const AuditPage = lazy(() => import('@/app/audit/AuditPage').then(m => ({ default: m.AuditPage })));

// Loading fallback component
function PageLoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading page...</p>
      </div>
    </div>
  );
}

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

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/leave/apply"
              element={
                <ProtectedRoute requiredRoles={['EMPLOYEE', 'MANAGER']}>
                  <LeaveApplicationPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/leave/history"
              element={
                <ProtectedRoute requiredRoles={['EMPLOYEE', 'MANAGER', 'HR_ADMIN']}>
                  <LeaveHistoryPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/approvals"
              element={
                <ProtectedRoute requiredRoles={['MANAGER', 'HR_ADMIN']}>
                  <ApprovalsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/calendar"
              element={
                <ProtectedRoute requiredRoles={['MANAGER', 'HR_ADMIN']}>
                  <Suspense fallback={<PageLoadingFallback />}>
                    <CalendarPage />
                  </Suspense>
                </ProtectedRoute>
              }
            />

            <Route
              path="/reports"
              element={
                <ProtectedRoute requiredRoles={['HR_ADMIN']}>
                  <Suspense fallback={<PageLoadingFallback />}>
                    <ReportsPage />
                  </Suspense>
                </ProtectedRoute>
              }
            />

            <Route
              path="/audit"
              element={
                <ProtectedRoute requiredRoles={['AUDITOR', 'HR_ADMIN', 'SYSTEM_ADMIN']}>
                  <Suspense fallback={<PageLoadingFallback />}>
                    <AuditPage />
                  </Suspense>
                </ProtectedRoute>
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
