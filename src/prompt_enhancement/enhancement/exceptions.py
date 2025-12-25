"""
Enhancement-specific exceptions.

Error categories (AC3) for LLM API failures.
"""


class EnhancementError(Exception):
    """Base exception for enhancement errors."""

    def __init__(self, message: str, category: str, recovery_suggestion: str = None):
        self.message = message
        self.category = category
        self.recovery_suggestion = recovery_suggestion
        super().__init__(message)


class AuthenticationError(EnhancementError):
    """API key invalid or missing (AC3)."""

    def __init__(self, message: str = "API key invalid or missing"):
        super().__init__(
            message,
            category="AUTH_ERROR",
            recovery_suggestion="Check your API key configuration"
        )


class RateLimitError(EnhancementError):
    """Too many API requests (AC3)."""

    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(
            message,
            category="RATE_LIMIT_ERROR",
            recovery_suggestion="Wait a moment and try again"
        )


class TimeoutError(EnhancementError):
    """API request timed out (AC3)."""

    def __init__(self, message: str = "API request timed out"):
        super().__init__(
            message,
            category="TIMEOUT_ERROR",
            recovery_suggestion="Request timeout - try again with a simpler prompt"
        )


class ServerError(EnhancementError):
    """LLM service unavailable (AC3)."""

    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(
            message,
            category="SERVER_ERROR",
            recovery_suggestion="Try again in a few moments"
        )


class ValidationError(EnhancementError):
    """Response validation failed (AC2)."""

    def __init__(self, message: str = "Response validation failed"):
        super().__init__(
            message,
            category="VALIDATION_ERROR",
            recovery_suggestion="Try with a different prompt"
        )
