"""Error classification system for categorizing and handling errors."""

import logging
from enum import Enum
from typing import Optional, Type

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Classification of error types."""

    API_KEY_MISSING = "api_key_missing"
    PROJECT_NOT_DETECTED = "project_not_detected"
    DETECTION_FAILED = "detection_failed"
    API_TIMEOUT = "api_timeout"
    PERMISSION_DENIED = "permission_denied"


class ErrorClassifier:
    """Classifies errors and maps exceptions to error categories."""

    # Map exception types to error categories
    EXCEPTION_MAPPING = {
        KeyError: ErrorCategory.API_KEY_MISSING,
        TimeoutError: ErrorCategory.API_TIMEOUT,
        PermissionError: ErrorCategory.PERMISSION_DENIED,
    }

    # Map error message patterns to categories
    MESSAGE_PATTERNS = {
        "api.key": ErrorCategory.API_KEY_MISSING,
        "openai_api_key": ErrorCategory.API_KEY_MISSING,
        "deepseek_api_key": ErrorCategory.API_KEY_MISSING,
        "project.not.detected": ErrorCategory.PROJECT_NOT_DETECTED,
        "project type": ErrorCategory.PROJECT_NOT_DETECTED,
        "timeout": ErrorCategory.API_TIMEOUT,
        "permission": ErrorCategory.PERMISSION_DENIED,
        "access denied": ErrorCategory.PERMISSION_DENIED,
        "low confidence": ErrorCategory.DETECTION_FAILED,
        "detection failed": ErrorCategory.DETECTION_FAILED,
    }

    @staticmethod
    def classify_exception(
        exception: Exception,
        context: Optional[str] = None,
    ) -> ErrorCategory:
        """
        Classify an exception to an error category.

        Args:
            exception: The exception to classify
            context: Optional context string (used for pattern matching)

        Returns:
            ErrorCategory for the exception
        """
        # Check if exception type is in mapping
        for exc_type, category in ErrorClassifier.EXCEPTION_MAPPING.items():
            if isinstance(exception, exc_type):
                logger.debug(f"Classified {type(exception).__name__} as {category.value}")
                return category

        # Check message patterns
        error_message = str(exception).lower()
        for pattern, category in ErrorClassifier.MESSAGE_PATTERNS.items():
            if pattern in error_message:
                logger.debug(f"Classified by message pattern '{pattern}' as {category.value}")
                return category

        # Check context patterns if provided
        if context:
            context_lower = context.lower()
            for pattern, category in ErrorClassifier.MESSAGE_PATTERNS.items():
                if pattern in context_lower:
                    logger.debug(f"Classified by context pattern '{pattern}' as {category.value}")
                    return category

        # Default to PROJECT_NOT_DETECTED if unable to classify
        logger.debug(f"Could not classify {type(exception).__name__}, defaulting to PROJECT_NOT_DETECTED")
        return ErrorCategory.PROJECT_NOT_DETECTED

    @staticmethod
    def classify_detection_failure(confidence: float) -> ErrorCategory:
        """
        Classify based on standards detection confidence.

        Args:
            confidence: Confidence score from 0.0 to 1.0

        Returns:
            ErrorCategory.DETECTION_FAILED if confidence < 60%,
            or None if detection was successful
        """
        if confidence < 0.6:
            logger.debug(f"Classified low confidence ({confidence:.1%}) as DETECTION_FAILED")
            return ErrorCategory.DETECTION_FAILED
        return None

    @staticmethod
    def classify_missing_api_key(
        openai_key_present: bool,
        deepseek_key_present: bool,
    ) -> Optional[ErrorCategory]:
        """
        Classify based on API key availability.

        Args:
            openai_key_present: Whether OPENAI_API_KEY is set
            deepseek_key_present: Whether DEEPSEEK_API_KEY is set

        Returns:
            ErrorCategory.API_KEY_MISSING if both missing, None otherwise
        """
        if not openai_key_present and not deepseek_key_present:
            logger.debug("Classified missing API keys as API_KEY_MISSING")
            return ErrorCategory.API_KEY_MISSING
        return None

    @staticmethod
    def classify_api_timeout(elapsed_seconds: float) -> Optional[ErrorCategory]:
        """
        Classify based on API timeout.

        Args:
            elapsed_seconds: Seconds elapsed for API call

        Returns:
            ErrorCategory.API_TIMEOUT if timeout exceeded (>20s), None otherwise
        """
        timeout_threshold = 20.0
        if elapsed_seconds > timeout_threshold:
            logger.debug(f"Classified {elapsed_seconds:.1f}s API call as API_TIMEOUT")
            return ErrorCategory.API_TIMEOUT
        return None
