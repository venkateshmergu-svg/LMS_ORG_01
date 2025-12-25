"""Unit tests for security middleware."""

import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import status

from lms.app.core.exceptions import (
    EntityNotFoundException,
    InsufficientBalanceException,
    LeaveOverlapException,
    LMSException,
    PolicyValidationException,
    WorkflowStateException,
)
from lms.app.middleware.security import (
    ErrorHandlerMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    @pytest.fixture(autouse=True)
    def reset_middleware_state(self):
        """Reset middleware class state before each test."""
        # Reset class-level state
        RateLimitMiddleware._fallback_log.clear()
        RateLimitMiddleware._redis_client = None
        RateLimitMiddleware._redis_checked = False
        yield
        # Clean up after test
        RateLimitMiddleware._fallback_log.clear()
        RateLimitMiddleware._redis_client = None
        RateLimitMiddleware._redis_checked = False

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        # Force memory fallback by marking Redis as checked and unavailable
        RateLimitMiddleware._redis_checked = True
        RateLimitMiddleware._redis_client = None
        app = MagicMock()
        return RateLimitMiddleware(app)

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = MagicMock()
        request.method = "POST"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        return request

    # -------------------------------------------------------------------------
    # Rate limit memory tests
    # -------------------------------------------------------------------------
    def test_check_rate_limit_memory_allows_requests_under_limit(self, middleware):
        """Memory rate limiter should allow requests under limit."""
        now = time.time()

        # First request should not be rate limited
        result = middleware._check_rate_limit_memory("192.168.1.1", now)

        assert result is False

    def test_check_rate_limit_memory_blocks_when_exceeded(self, middleware):
        """Memory rate limiter should block when limit exceeded."""
        client_ip = "192.168.1.2"
        now = time.time()

        # Fill up to the limit
        for i in range(RateLimitMiddleware.RATE_LIMIT_MAX):
            middleware._check_rate_limit_memory(client_ip, now + i * 0.001)

        # Next request should be rate limited
        result = middleware._check_rate_limit_memory(client_ip, now + 1)

        assert result is True

    def test_check_rate_limit_memory_allows_after_window_expires(self, middleware):
        """Memory rate limiter should allow requests after window expires."""
        client_ip = "192.168.1.3"
        old_time = time.time() - RateLimitMiddleware.RATE_LIMIT_WINDOW - 10

        # Add old requests outside the window
        RateLimitMiddleware._fallback_log[client_ip] = [old_time] * 100

        # New request should be allowed (old ones expired)
        result = middleware._check_rate_limit_memory(client_ip, time.time())

        assert result is False

    # -------------------------------------------------------------------------
    # Redis fallback tests
    # -------------------------------------------------------------------------
    def test_check_rate_limit_redis_falls_back_to_memory(self, middleware):
        """Redis rate limiter should fall back to memory when Redis unavailable."""
        # Force Redis to be unavailable
        RateLimitMiddleware._redis_checked = True
        RateLimitMiddleware._redis_client = None

        now = time.time()
        result = middleware._check_rate_limit_redis("192.168.1.4", now)

        # Should use memory fallback, which allows first request
        assert result is False

    @patch.object(RateLimitMiddleware, "_get_redis_client")
    def test_check_rate_limit_redis_handles_redis_error(
        self, mock_get_redis, middleware
    ):
        """Redis rate limiter should handle Redis errors gracefully."""
        mock_redis = MagicMock()
        mock_redis.pipeline.return_value.execute.side_effect = Exception("Redis error")
        mock_get_redis.return_value = mock_redis

        now = time.time()
        result = middleware._check_rate_limit_redis("192.168.1.5", now)

        # Should fall back to memory
        assert result is False

    # -------------------------------------------------------------------------
    # dispatch() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_dispatch_allows_get_requests(self, middleware, mock_request):
        """dispatch() should not rate limit GET requests."""
        mock_request.method = "GET"
        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_rate_limits_post_requests(self, middleware, mock_request):
        """dispatch() should rate limit POST requests when limit exceeded."""
        mock_request.method = "POST"
        client_ip = mock_request.client.host

        # Fill up the rate limit by simulating many past requests
        now = time.time()
        RateLimitMiddleware._fallback_log[client_ip] = [
            now
        ] * RateLimitMiddleware.RATE_LIMIT_MAX

        call_next = AsyncMock()

        response = await middleware.dispatch(mock_request, call_next)

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_allows_post_under_limit(self, middleware, mock_request):
        """dispatch() should allow POST requests under limit."""
        mock_request.method = "POST"

        call_next = AsyncMock(return_value=MagicMock())

        response = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_uses_x_forwarded_for(self, middleware, mock_request):
        """dispatch() should use X-Forwarded-For header for client IP."""
        mock_request.method = "POST"
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}

        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(mock_request, call_next)

        # Check that the IP was tracked - defaultdict creates entry on access
        assert len(RateLimitMiddleware._fallback_log.get("10.0.0.1", [])) > 0

    @pytest.mark.asyncio
    async def test_dispatch_handles_no_client(self, middleware, mock_request):
        """dispatch() should handle request with no client."""
        mock_request.method = "POST"
        mock_request.client = None
        mock_request.headers = {}

        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(mock_request, call_next)

        # Check that "unknown" was tracked
        assert len(RateLimitMiddleware._fallback_log.get("unknown", [])) > 0


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        return SecurityHeadersMiddleware(app)

    @pytest.mark.asyncio
    async def test_adds_x_content_type_options(self, middleware):
        """Should add X-Content-Type-Options header."""
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-Content-Type-Options"] == "nosniff"

    @pytest.mark.asyncio
    async def test_adds_x_frame_options(self, middleware):
        """Should add X-Frame-Options header."""
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.asyncio
    async def test_adds_x_xss_protection(self, middleware):
        """Should add X-XSS-Protection header."""
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.asyncio
    async def test_adds_referrer_policy(self, middleware):
        """Should add Referrer-Policy header."""
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    @pytest.mark.asyncio
    async def test_adds_strict_transport_security(self, middleware):
        """Should add Strict-Transport-Security header."""
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert "max-age=" in result.headers["Strict-Transport-Security"]


class TestErrorHandlerMiddleware:
    """Tests for ErrorHandlerMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        return ErrorHandlerMiddleware(app)

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/test"
        return request

    @pytest.mark.asyncio
    async def test_passes_through_successful_requests(self, middleware, mock_request):
        """Should pass through successful requests unchanged."""
        expected_response = MagicMock()
        call_next = AsyncMock(return_value=expected_response)

        result = await middleware.dispatch(mock_request, call_next)

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_handles_entity_not_found_exception(self, middleware, mock_request):
        """Should return 404 for EntityNotFoundException."""
        from uuid import uuid4

        call_next = AsyncMock(side_effect=EntityNotFoundException("User", uuid4()))

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_handles_workflow_state_exception(self, middleware, mock_request):
        """Should return 409 for WorkflowStateException."""
        # WorkflowStateException(current_state, attempted_action)
        call_next = AsyncMock(side_effect=WorkflowStateException("DRAFT", "approve"))

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_handles_leave_overlap_exception(self, middleware, mock_request):
        """Should return 400 for LeaveOverlapException."""
        call_next = AsyncMock(
            side_effect=LeaveOverlapException(["2024-01-15", "2024-01-16"])
        )

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_handles_insufficient_balance_exception(
        self, middleware, mock_request
    ):
        """Should return 400 for InsufficientBalanceException."""
        # InsufficientBalanceException(available, requested, leave_type)
        call_next = AsyncMock(
            side_effect=InsufficientBalanceException(2.0, 5.0, "ANNUAL")
        )

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_handles_policy_validation_exception(self, middleware, mock_request):
        """Should return 400 for PolicyValidationException."""
        call_next = AsyncMock(side_effect=PolicyValidationException("Invalid policy"))

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_handles_generic_lms_exception(self, middleware, mock_request):
        """Should return 400 for generic LMSException."""
        call_next = AsyncMock(side_effect=LMSException("Generic error", "ERR001"))

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_handles_unexpected_exception(self, middleware, mock_request):
        """Should return 500 for unexpected exceptions."""
        call_next = AsyncMock(side_effect=ValueError("Unexpected error"))

        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_does_not_expose_stack_trace(self, middleware, mock_request):
        """Should not expose stack trace in error response."""
        call_next = AsyncMock(side_effect=RuntimeError("Internal details"))

        result = await middleware.dispatch(mock_request, call_next)

        # Response body should be generic
        body = (
            result.body.decode() if hasattr(result.body, "decode") else str(result.body)
        )
        assert "Internal details" not in body
        assert "traceback" not in body.lower()
