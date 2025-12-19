"""
Sensitive data validator for project context.

Ensures that API keys, credentials, tokens, and other sensitive
information are not included in LLM prompts (AC4).
"""

import logging
import re
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SensitiveDataValidator:
    """
    Validates context to ensure no sensitive data leaks.

    Detects:
    - API keys (sk-, OPENAI_API_KEY, etc.)
    - Authentication tokens
    - Credentials patterns
    - Internal URLs and secrets
    """

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "openai_key": r"sk-[A-Za-z0-9]{20,}",
        "api_key_pattern": r"api[_-]?key\s*[:=]\s*[^\s]{20,}",
        "token_pattern": r"token\s*[:=]\s*[^\s]{20,}",
        "password_pattern": r"password\s*[:=]\s*[^\s]+",
        "secret_pattern": r"secret\s*[:=]\s*[^\s]{20,}",
        "deepseek_pattern": r"sk-[A-Za-z0-9]{30,}",  # DeepSeek keys
        "aws_pattern": r"AKIA[0-9A-Z]{16}",  # AWS keys
        "github_token": r"ghp_[A-Za-z0-9_]{36,}",
    }

    def __init__(self):
        """Initialize validator with compiled regex patterns."""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.SENSITIVE_PATTERNS.items()
        }

    def validate_context_dict(self, context_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that context dictionary contains no sensitive data.

        Args:
            context_dict: Dictionary representation of ProjectContext

        Returns:
            (is_valid: bool, violations: List[str])
            - is_valid: True if no sensitive data found
            - violations: List of found sensitive data issues
        """
        violations = []

        # Convert dict to string and check
        context_str = str(context_dict)
        for pattern_name, pattern in self.compiled_patterns.items():
            matches = pattern.findall(context_str)
            if matches:
                violations.append(f"Found {pattern_name} pattern: {len(matches)} matches")
                logger.debug(f"Sensitive data detected: {pattern_name} ({len(matches)} matches)")

        # Check specific fields that should never contain sensitive data
        violations.extend(self._validate_field("user_overrides", context_dict.get("user_overrides", {})))
        violations.extend(self._validate_field("project_name", context_dict.get("project_name", "")))

        return len(violations) == 0, violations

    def _validate_field(self, field_name: str, field_value: Any) -> List[str]:
        """
        Validate a specific field for sensitive data.

        Args:
            field_name: Name of field being validated
            field_value: Value to check

        Returns:
            List of violations found in this field
        """
        violations = []
        field_str = str(field_value)

        for pattern_name, pattern in self.compiled_patterns.items():
            if pattern.search(field_str):
                violations.append(
                    f"Sensitive data in '{field_name}': {pattern_name} pattern detected"
                )
                logger.debug(f"Sensitive data in '{field_name}': {pattern_name}")

        return violations

    def validate_prompt_text(self, prompt_text: str) -> tuple[bool, List[str]]:
        """
        Validate that prompt text contains no sensitive data.

        Args:
            prompt_text: The final LLM prompt text

        Returns:
            (is_valid: bool, violations: List[str])
        """
        violations = []

        for pattern_name, pattern in self.compiled_patterns.items():
            matches = pattern.findall(prompt_text)
            if matches:
                violations.append(f"Sensitive data in prompt: {pattern_name}")
                logger.debug(f"Sensitive data in final prompt: {pattern_name}")

        return len(violations) == 0, violations

    def sanitize_for_logging(self, text: str) -> str:
        """
        Sanitize text for safe logging (redact sensitive data).

        Args:
            text: Text to sanitize

        Returns:
            Text with sensitive patterns redacted
        """
        sanitized = text
        for pattern_name, pattern in self.compiled_patterns.items():
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized

    def check_environment_variables(self) -> List[str]:
        """
        Check if sensitive environment variables are set.

        Returns:
            List of found sensitive env vars (non-empty means they're set)
        """
        import os
        sensitive_env_vars = [
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "ANTHROPIC_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "GITHUB_TOKEN",
        ]

        found = []
        for var in sensitive_env_vars:
            if os.getenv(var):
                found.append(var)

        return found
