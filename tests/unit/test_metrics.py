"""Unit tests for metrics module."""

import pytest

from lms.app.metrics import (
    Counter,
    Histogram,
    api_request_duration_seconds,
    api_requests_total,
    approvals_processed_total,
    leave_requests_created_total,
    notification_failures_total,
    render_metrics,
    reset_metrics,
)


class TestCounter:
    """Tests for Counter metric."""

    def test_initial_value_empty(self):
        """Counter should start with empty values."""
        counter = Counter()
        assert counter.value == {}

    def test_inc_without_labels(self):
        """inc() without labels should increment default key."""
        counter = Counter()
        counter.inc()
        assert counter.value[()] == 1

        counter.inc()
        assert counter.value[()] == 2

    def test_inc_with_labels(self):
        """inc() with labels should track separately."""
        counter = Counter()
        counter.inc(("route1", "GET", "200"))
        counter.inc(("route1", "GET", "200"))
        counter.inc(("route2", "POST", "201"))

        assert counter.value[("route1", "GET", "200")] == 2
        assert counter.value[("route2", "POST", "201")] == 1

    def test_different_labels_tracked_independently(self):
        """Different label combinations should be tracked independently."""
        counter = Counter()
        counter.inc(("a", "1"))
        counter.inc(("b", "2"))
        counter.inc(("a", "1"))

        assert counter.value[("a", "1")] == 2
        assert counter.value[("b", "2")] == 1


class TestHistogram:
    """Tests for Histogram metric."""

    def test_default_buckets(self):
        """Histogram should have default bucket boundaries."""
        histogram = Histogram()
        assert 0.005 in histogram.buckets
        assert 10.0 in histogram.buckets

    def test_custom_buckets(self):
        """Histogram should accept custom bucket boundaries."""
        buckets = (0.1, 0.5, 1.0, 5.0)
        histogram = Histogram(buckets=buckets)
        assert histogram.buckets == buckets

    def test_initial_values(self):
        """Histogram should start with zero values."""
        histogram = Histogram()
        assert histogram.values == []
        assert histogram.sum_value == 0.0
        assert histogram.count_value == 0

    def test_observe_records_value(self):
        """observe() should record the value."""
        histogram = Histogram()
        histogram.observe(0.5)

        assert 0.5 in histogram.values
        assert histogram.sum_value == 0.5
        assert histogram.count_value == 1

    def test_observe_multiple_values(self):
        """observe() should accumulate multiple observations."""
        histogram = Histogram()
        histogram.observe(0.1)
        histogram.observe(0.2)
        histogram.observe(0.3)

        assert len(histogram.values) == 3
        assert histogram.sum_value == pytest.approx(0.6)
        assert histogram.count_value == 3


class TestResetMetrics:
    """Tests for reset_metrics function."""

    def test_reset_clears_all_metrics(self):
        """reset_metrics should clear all global metrics."""
        # Add some values
        from lms.app import metrics

        metrics.api_requests_total.inc(("/test", "GET", "200"))
        metrics.leave_requests_created_total.inc()
        metrics.api_request_duration_seconds.observe(1.5)

        # Reset
        reset_metrics()

        # Verify all cleared
        # Need to re-import to get new references
        from lms.app.metrics import (
            api_request_duration_seconds as new_duration,
        )
        from lms.app.metrics import (
            api_requests_total as new_api,
        )
        from lms.app.metrics import (
            leave_requests_created_total as new_leave,
        )

        assert new_api.value == {}
        assert new_leave.value == {}
        assert new_duration.values == []


class TestRenderMetrics:
    """Tests for render_metrics function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_render_returns_string(self):
        """render_metrics should return a string."""
        result = render_metrics()
        assert isinstance(result, str)

    def test_render_includes_help_lines(self):
        """render_metrics should include HELP comments."""
        result = render_metrics()
        assert "# HELP api_requests_total" in result
        assert "# HELP api_request_duration_seconds" in result
        assert "# HELP leave_requests_created_total" in result

    def test_render_includes_type_lines(self):
        """render_metrics should include TYPE annotations."""
        result = render_metrics()
        assert "# TYPE api_requests_total counter" in result
        assert "# TYPE api_request_duration_seconds histogram" in result

    def test_render_includes_api_request_metrics(self):
        """render_metrics should include api request counts."""
        from lms.app import metrics

        metrics.api_requests_total.inc(("/api/users", "GET", "200"))
        metrics.api_requests_total.inc(("/api/users", "GET", "200"))

        result = render_metrics()

        assert 'route="/api/users"' in result
        assert 'method="GET"' in result
        assert 'status="200"' in result
        assert "} 2" in result  # count of 2

    def test_render_includes_duration_histogram(self):
        """render_metrics should include duration histogram stats."""
        from lms.app import metrics

        metrics.api_request_duration_seconds.observe(0.5)
        metrics.api_request_duration_seconds.observe(1.5)

        result = render_metrics()

        assert "api_request_duration_seconds_sum 2.0" in result
        assert "api_request_duration_seconds_count 2" in result

    def test_render_includes_leave_requests_metric(self):
        """render_metrics should include leave requests counter."""
        result = render_metrics()
        assert "leave_requests_created_total" in result

    def test_render_includes_approvals_metric(self):
        """render_metrics should include approvals counter."""
        result = render_metrics()
        assert "approvals_processed_total" in result

    def test_render_includes_notification_failures_metric(self):
        """render_metrics should include notification failures counter."""
        result = render_metrics()
        assert "notification_failures_total" in result

    def test_render_ends_with_newline(self):
        """render_metrics output should end with newline."""
        result = render_metrics()
        assert result.endswith("\n")
