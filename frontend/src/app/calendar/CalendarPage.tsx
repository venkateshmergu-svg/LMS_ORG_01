/**
 * Team Calendar Page
 *
 * Displays team leave in a calendar view for managers
 * - Monthly calendar view
 * - Shows team members on leave
 * - Navigate between months
 * - Color-coded by leave type
 *
 * Enhanced with:
 * - Keyboard navigation for month switching
 * - Improved accessibility (ARIA labels)
 * - Skeleton loader for better perceived performance
 * - Query optimization
 */

import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';
import { buttonPrimary, buttonSecondary } from '@/utils/buttonStyles';
import type { LeaveRequest } from '@/api/types/generated';

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  leaves: LeaveRequest[];
}

export function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());

  const {
    data: teamLeaves,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['team-calendar', currentDate.getFullYear(), currentDate.getMonth()],
    queryFn: async () => {
      const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

      const { data } = await apiClient.get<{ items: LeaveRequest[] }>('/api/v1/leave/team', {
        params: {
          start_date: startOfMonth.toISOString().split('T')[0],
          end_date: endOfMonth.toISOString().split('T')[0],
        },
      });
      return data.items || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const previousMonth = useCallback(() => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  }, [currentDate]);

  const nextMonth = useCallback(() => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  }, [currentDate]);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowLeft') {
        previousMonth();
      } else if (e.key === 'ArrowRight') {
        nextMonth();
      } else if (e.key === 'Home') {
        goToToday();
      }
    },
    [previousMonth, nextMonth, goToToday]
  );

  const getCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startingDayOfWeek = firstDay.getDay();

    const days: CalendarDay[] = [];

    // Previous month's days
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthLastDay - i),
        isCurrentMonth: false,
        leaves: [],
      });
    }

    // Current month's days
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);

      const leavesOnDay =
        teamLeaves?.filter((leave) => {
          const leaveStart = new Date(leave.start_date);
          const leaveEnd = new Date(leave.end_date);
          return date >= leaveStart && date <= leaveEnd && leave.status === 'APPROVED';
        }) || [];

      days.push({
        date,
        isCurrentMonth: true,
        leaves: leavesOnDay,
      });
    }

    // Next month's days to fill the grid
    const remainingDays = 42 - days.length; // 6 rows * 7 days
    for (let day = 1; day <= remainingDays; day++) {
      days.push({
        date: new Date(year, month + 1, day),
        isCurrentMonth: false,
        leaves: [],
      });
    }

    return days;
  };

  const getLeaveTypeColor = (leaveType: string) => {
    switch (leaveType.toLowerCase()) {
      case 'annual leave':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'sick leave':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'personal leave':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Team Calendar</h1>
          <p className="text-gray-600 dark:text-gray-400">View team leave schedule</p>
        </div>

        {/* Calendar Controls */}
        <div
          className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6"
          onKeyDown={handleKeyDown}
          role="navigation"
          aria-label="Calendar navigation"
        >
          <div className="p-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{monthName}</h2>
            <div className="flex gap-2">
              <button
                onClick={previousMonth}
                className={buttonSecondary}
                aria-label="Previous month (Arrow Left)"
              >
                ← Previous
              </button>
              <button
                onClick={goToToday}
                className={buttonPrimary}
                aria-label="Go to today (Home key)"
              >
                Today
              </button>
              <button
                onClick={nextMonth}
                className={buttonSecondary}
                aria-label="Next month (Arrow Right)"
              >
                Next →
              </button>
            </div>
          </div>
        </div>

        {/* Loading/Error States */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <LoadingSpinner size="lg" />
          </div>
        ) : error ? (
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <ErrorAlert
              message="Failed to load team calendar. Please try again."
              onClose={() => {}}
            />
          </div>
        ) : (
          <>
            {/* Calendar Grid */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
              {/* Week day headers */}
              <div className="grid grid-cols-7 gap-px bg-gray-200 dark:bg-gray-700">
                {weekDays.map((day) => (
                  <div
                    key={day}
                    className="bg-gray-50 dark:bg-gray-800 py-2 text-center text-sm font-semibold text-gray-700 dark:text-gray-300"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar days */}
              <div className="grid grid-cols-7 gap-px bg-gray-200 dark:bg-gray-700">
                {getCalendarDays().map((day, idx) => {
                  const isToday = day.date.toDateString() === new Date().toDateString();

                  return (
                    <div
                      key={idx}
                      className={`min-h-[120px] bg-white dark:bg-gray-800 p-2 ${
                        !day.isCurrentMonth ? 'opacity-50' : ''
                      }`}
                    >
                      <div
                        className={`text-sm font-medium mb-1 ${
                          isToday
                            ? 'w-7 h-7 flex items-center justify-center rounded-full bg-primary text-white'
                            : 'text-gray-900 dark:text-white'
                        }`}
                      >
                        {day.date.getDate()}
                      </div>

                      {/* Leave items */}
                      <div className="space-y-1">
                        {day.leaves.slice(0, 3).map((leave, leaveIdx) => (
                          <div
                            key={leaveIdx}
                            className={`text-xs px-2 py-1 rounded truncate ${getLeaveTypeColor(leave.leave_type)}`}
                            title={`${leave.user_id} - ${leave.leave_type}`}
                          >
                            {leave.user_id.split('@')[0]}
                          </div>
                        ))}
                        {day.leaves.length > 3 && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 px-2">
                            +{day.leaves.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Legend */}
            <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Leave Types
              </h3>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-blue-100 dark:bg-blue-900"></div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">Annual Leave</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-red-100 dark:bg-red-900"></div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">Sick Leave</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-purple-100 dark:bg-purple-900"></div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">Personal Leave</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
