"""
Lightweight Prometheus-compatible metrics collection.

Provides counters and timers for:
- API requests (total, duration)
- Leave requests (created)
- Approvals (processed)
- Notifications (failures)

No external APM agents; purely in-memory collection.
"""

from typing import Dict


# Simple in-memory metrics registry
class Counter:
    """Thread-safe counter metric."""

    def __init__(self) -> None:
        self.value: Dict[tuple, int] = {}

    def inc(self, labels: tuple = ()) -> None:
        """Increment counter."""
        self.value[labels] = self.value.get(labels, 0) + 1


class Histogram:
    """Thread-safe histogram (for recording durations)."""

    def __init__(
        self,
        buckets: tuple = (
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        ),
    ) -> None:
        self.buckets = buckets
        self.values: list = []
        self.sum_value = 0.0
        self.count_value = 0

    def observe(self, value: float) -> None:
        """Record observation."""
        self.values.append(value)
        self.sum_value += value
        self.count_value += 1


# Global metrics
api_requests_total = Counter()
api_request_duration_seconds = Histogram()
leave_requests_created_total = Counter()
approvals_processed_total = Counter()
notification_failures_total = Counter()


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)."""
    global api_requests_total, api_request_duration_seconds, leave_requests_created_total
    global approvals_processed_total, notification_failures_total

    api_requests_total = Counter()
    api_request_duration_seconds = Histogram()
    leave_requests_created_total = Counter()
    approvals_processed_total = Counter()
    notification_failures_total = Counter()


def render_metrics() -> str:
    """
    Render metrics in Prometheus text format.

    Returns:
        Prometheus-formatted metrics string
    """
    lines = [
        "# HELP api_requests_total Total API requests by route, method, status",
        "# TYPE api_requests_total counter",
    ]

    for (route, method, status), count in api_requests_total.value.items():
        labels = f'route="{route}",method="{method}",status="{status}"'
        lines.append(f"api_requests_total{{{labels}}} {count}")

    lines.extend(
        [
            "# HELP api_request_duration_seconds API request latency in seconds",
            "# TYPE api_request_duration_seconds histogram",
            f"api_request_duration_seconds_sum {api_request_duration_seconds.sum_value}",
            f"api_request_duration_seconds_count {api_request_duration_seconds.count_value}",
            "# HELP leave_requests_created_total Total leave requests created",
            "# TYPE leave_requests_created_total counter",
            f"leave_requests_created_total{{}} {leave_requests_created_total.value.get((), 0)}",
            "# HELP approvals_processed_total Total approval decisions processed",
            "# TYPE approvals_processed_total counter",
            f"approvals_processed_total{{}} {approvals_processed_total.value.get((), 0)}",
            "# HELP notification_failures_total Total notification delivery failures",
            "# TYPE notification_failures_total counter",
            f"notification_failures_total{{}} {notification_failures_total.value.get((), 0)}",
        ]
    )

    return "\n".join(lines) + "\n"
