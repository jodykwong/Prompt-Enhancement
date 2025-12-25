"""User-friendly error messages for each error category."""

import logging
from dataclasses import dataclass
from typing import Optional

from .classification import ErrorCategory

logger = logging.getLogger(__name__)


@dataclass
class UserErrorMessage:
    """User-friendly error message with resolution steps."""

    title: str
    message: str
    steps: list[str]
    category: ErrorCategory


class ErrorMessageFormatter:
    """Formats user-friendly error messages for each error category."""

    @staticmethod
    def format_error(
        category: ErrorCategory,
        context: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> UserErrorMessage:
        """
        Format error message for user display.

        Args:
            category: The error category
            context: Optional context (e.g., "while analyzing project")
            confidence: Optional confidence score (for DETECTION_FAILED)

        Returns:
            UserErrorMessage with title, message, and resolution steps
        """
        if category == ErrorCategory.API_KEY_MISSING:
            return ErrorMessageFormatter._format_api_key_missing()
        elif category == ErrorCategory.PROJECT_NOT_DETECTED:
            return ErrorMessageFormatter._format_project_not_detected()
        elif category == ErrorCategory.DETECTION_FAILED:
            return ErrorMessageFormatter._format_detection_failed(confidence)
        elif category == ErrorCategory.API_TIMEOUT:
            return ErrorMessageFormatter._format_api_timeout()
        elif category == ErrorCategory.PERMISSION_DENIED:
            return ErrorMessageFormatter._format_permission_denied()
        else:
            # Fallback for unknown category
            return ErrorMessageFormatter._format_generic_error(category)

    @staticmethod
    def _format_api_key_missing() -> UserErrorMessage:
        """Format API key missing error."""
        return UserErrorMessage(
            title="❌ API Key Not Configured",
            message="Please set your OpenAI or DeepSeek API key:",
            steps=[
                "Run: /pe-setup",
                "Or export: export OPENAI_API_KEY=sk-...",
                "Or add to ~/.prompt-enhancement/config.yaml",
            ],
            category=ErrorCategory.API_KEY_MISSING,
        )

    @staticmethod
    def _format_project_not_detected() -> UserErrorMessage:
        """Format project not detected error."""
        return UserErrorMessage(
            title="⚠️ Project Type Not Detected",
            message="System could not identify project language.",
            steps=[
                "Ensure you are in project root directory",
                "Project should contain package.json, requirements.txt, etc.",
                "System will use generic enhancement",
            ],
            category=ErrorCategory.PROJECT_NOT_DETECTED,
        )

    @staticmethod
    def _format_detection_failed(confidence: Optional[float] = None) -> UserErrorMessage:
        """Format standards detection failed error."""
        confidence_pct = (
            f"{int(confidence * 100)}%"
            if confidence is not None
            else "low"
        )

        return UserErrorMessage(
            title="⚠️ Low Confidence in Standard Detection",
            message=f"System has low confidence in detected standards (Confidence: {confidence_pct})",
            steps=[
                "Confirm detected standards with --override",
                "Use --override to manually set standards",
                "Create .pe.yaml configuration in project",
            ],
            category=ErrorCategory.DETECTION_FAILED,
        )

    @staticmethod
    def _format_api_timeout() -> UserErrorMessage:
        """Format API timeout error."""
        return UserErrorMessage(
            title="⚠️ API Timeout",
            message="LLM API is taking too long.",
            steps=[
                "Check your internet connection",
                "Retry the operation",
                "If persistent, the API may be experiencing issues",
            ],
            category=ErrorCategory.API_TIMEOUT,
        )

    @staticmethod
    def _format_permission_denied() -> UserErrorMessage:
        """Format permission denied error."""
        return UserErrorMessage(
            title="⚠️ Permission Denied",
            message="Cannot access some project files.",
            steps=[
                "Check file permissions in your project",
                "Ensure you have read access to project files",
                "Analysis will use accessible files only",
            ],
            category=ErrorCategory.PERMISSION_DENIED,
        )

    @staticmethod
    def _format_generic_error(category: ErrorCategory) -> UserErrorMessage:
        """Format generic error for unknown categories."""
        return UserErrorMessage(
            title="⚠️ An Error Occurred",
            message=f"Error: {category.value}",
            steps=[
                "Check logs for detailed information",
                "Retry the operation",
                "Run /pe-help for documentation",
            ],
            category=category,
        )

    @staticmethod
    def format_for_display(error_message: UserErrorMessage) -> str:
        """
        Format error message for terminal display.

        Args:
            error_message: UserErrorMessage to format

        Returns:
            Formatted string for display
        """
        lines = [
            error_message.title,
            "",
            error_message.message,
            "",
        ]

        lines.extend(error_message.steps)
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_recovery_message(category: ErrorCategory) -> str:
        """
        Format recovery suggestion message.

        Args:
            category: The error category

        Returns:
            Recovery message with log location and suggestions
        """
        recovery_steps = {
            ErrorCategory.API_KEY_MISSING: "Run /pe-setup to configure API key",
            ErrorCategory.PROJECT_NOT_DETECTED: "Ensure you're in project root with package.json or requirements.txt",
            ErrorCategory.DETECTION_FAILED: "Use --override to manually set standards or create .pe.yaml",
            ErrorCategory.API_TIMEOUT: "Check internet connection and retry",
            ErrorCategory.PERMISSION_DENIED: "Check file permissions or run from accessible directory",
        }

        specific_step = recovery_steps.get(
            category,
            "Check logs for detailed information",
        )

        message = f"""
❌ An Error Occurred

Diagnostic information saved to:
~/.prompt-enhancement/logs/pe.log

Suggested steps:
1. {specific_step}
2. Retry the operation
3. If issue persists, run /pe-logs for more information

For more help: /pe-help
"""
        return message.strip()
