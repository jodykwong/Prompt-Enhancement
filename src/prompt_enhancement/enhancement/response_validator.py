"""
LLM response validator for enhancement results.

Validates that LLM responses meet quality requirements (AC2).
"""

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates LLM responses meet quality standards.

    AC2: Response validation - non-empty, actionable, preserves intent, reasonable length
    """

    # Configuration constants
    MIN_LENGTH = 50  # Minimum characters
    MAX_LENGTH = 2000  # Maximum characters per AC2
    ACTIONABLE_KEYWORDS = [
        "step", "implement", "add", "create", "modify", "update",
        "function", "method", "class", "module", "test", "validate",
        "verify", "check", "follow", "ensure", "include", "use",
        "define", "write", "generate", "handle", "process", "manage"
    ]

    def validate_response(self, response: str, original_prompt: str) -> Tuple[bool, List[str]]:
        """
        Validate LLM response.

        Args:
            response: Response text from LLM
            original_prompt: Original user prompt for comparison

        Returns:
            (is_valid: bool, violations: List[str])
        """
        violations = []

        # AC2: Check 1 - Response not empty
        if not response or len(response.strip()) == 0:
            violations.append("Response is empty")
            return False, violations

        # AC2: Check 2 - Response length reasonable
        if len(response) < self.MIN_LENGTH:
            violations.append(f"Response too short (< {self.MIN_LENGTH} chars)")
        if len(response) > self.MAX_LENGTH:
            violations.append(f"Response exceeds maximum length ({self.MAX_LENGTH} chars)")

        # AC2: Check 3 - Contains actionable guidance
        if not self._contains_actionable_guidance(response):
            violations.append("Response lacks actionable guidance")

        # AC2: Check 4 - Preserves original intent
        if not self._preserves_original_intent(response, original_prompt):
            violations.append("Response may not preserve original intent")

        return len(violations) == 0, violations

    def _contains_actionable_guidance(self, response: str) -> bool:
        """
        Check if response contains actionable guidance.

        Looks for keywords like "implement", "step", "test", etc.
        """
        response_lower = response.lower()
        actionable_count = sum(
            1 for keyword in self.ACTIONABLE_KEYWORDS
            if keyword in response_lower
        )

        # At least 3 actionable keywords
        return actionable_count >= 3

    def _preserves_original_intent(self, response: str, original: str) -> bool:
        """
        Check if response preserves original user intent.

        Simple heuristic: looks for key nouns/concepts from original prompt.
        """
        # Extract significant words from original prompt (3+ chars, excluding common words)
        common_words = {"the", "and", "or", "for", "with", "that", "this", "from"}
        original_words = {
            word.lower() for word in re.findall(r'\b\w{3,}\b', original)
            if word.lower() not in common_words
        }

        if not original_words:
            # Can't determine intent
            return True

        # Check if response contains at least 30% of original meaningful words
        response_lower = response.lower()
        matched_words = sum(
            1 for word in original_words
            if word in response_lower
        )

        match_ratio = matched_words / len(original_words) if original_words else 0
        return match_ratio >= 0.3

    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response for display.

        Removes excessive whitespace, ensures proper formatting.

        Args:
            response: Raw response from LLM

        Returns:
            Sanitized response
        """
        # Remove leading/trailing whitespace
        sanitized = response.strip()

        # Replace multiple newlines with single
        sanitized = re.sub(r'\n\n+', '\n\n', sanitized)

        # Ensure ends with period if not already
        if sanitized and not sanitized.endswith(('.', '!', '?', ':')):
            sanitized += '.'

        return sanitized

    def extract_key_sections(self, response: str) -> dict:
        """
        Extract key sections from enhanced prompt.

        Attempts to parse response into:
        - Original concept
        - Implementation steps
        - Testing guidance
        - Special considerations

        Args:
            response: Enhanced prompt text

        Returns:
            Dictionary with extracted sections
        """
        sections = {
            "full_response": response,
            "has_implementation_steps": "step" in response.lower() or "implement" in response.lower(),
            "has_testing_guidance": "test" in response.lower() or "verify" in response.lower(),
            "has_error_handling": "error" in response.lower() or "handle" in response.lower(),
            "estimated_complexity": self._estimate_complexity(response),
        }

        return sections

    def _estimate_complexity(self, response: str) -> str:
        """
        Estimate complexity of described implementation.

        Returns: "simple", "moderate", or "complex"
        """
        response_lower = response.lower()
        line_count = len(response.split('\n'))

        complexity_indicators = {
            "simple": ["basic", "simple", "easy", "straightforward"],
            "complex": ["complex", "advanced", "sophisticated", "intricate", "architecture"]
        }

        complex_score = sum(
            1 for word in complexity_indicators["complex"]
            if word in response_lower
        )

        simple_score = sum(
            1 for word in complexity_indicators["simple"]
            if word in response_lower
        )

        if complex_score > simple_score:
            return "complex"
        elif simple_score > 0 or line_count <= 10:
            return "simple"
        else:
            return "moderate"
