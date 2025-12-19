"""
Enhancement generator - orchestrates LLM-based prompt enhancement.

Combines ProjectContext, PromptBuilder, and LLM providers to generate
project-aware enhancements (AC1-AC8).
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from openai import AuthenticationError, RateLimitError, Timeout

from .context import ProjectContext
from .prompt_builder import PromptBuilder
from .llm_provider import LLMProvider, create_provider, LLMResponse
from .response_validator import ResponseValidator
from .exceptions import (
    EnhancementError,
    AuthenticationError as AuthError,
    RateLimitError as RateLimitErr,
    TimeoutError as TimeoutErr,
    ServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancementResult:
    """Result from enhancement generation (AC1, AC2)."""

    original_prompt: str
    enhanced_prompt: str
    provider: str
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    generation_time_seconds: float
    was_degraded: bool = False
    degradation_reason: Optional[str] = None
    quality_warnings: list = None

    def __post_init__(self):
        if self.quality_warnings is None:
            self.quality_warnings = []


class EnhancementGenerator:
    """
    Orchestrates project-aware prompt enhancement.

    Coordinates:
    - ProjectContext collection
    - Prompt formatting
    - LLM API calls (with fallback)
    - Response validation
    - Graceful degradation
    """

    # Timeout configuration (AC3)
    SOFT_TIMEOUT_SECONDS = 5  # Start degradation
    HARD_TIMEOUT_SECONDS = 30  # Absolute limit
    MAX_RETRIES = 1  # Retry once on certain errors

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize enhancement generator.

        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        self.prompt_builder = PromptBuilder()
        self.response_validator = ResponseValidator()
        logger.debug("Initialized EnhancementGenerator")

    def generate_enhancement(
        self,
        user_prompt: str,
        project_context: ProjectContext,
        use_degradation: bool = True,
    ) -> EnhancementResult:
        """
        Generate project-aware enhancement.

        AC1: Call LLM with project context
        AC2: Validate response
        AC3: Handle timeouts and errors
        AC4: Implement retry and fallback

        Args:
            user_prompt: Original user prompt
            project_context: Collected project context (from Story 3.1)
            use_degradation: Allow graceful degradation on failure

        Returns:
            EnhancementResult with enhanced prompt

        Raises:
            EnhancementError: If enhancement fails completely
        """
        logger.info(f"Generating enhancement for prompt ({len(user_prompt)} chars)")
        start_time = time.time()

        try:
            # Step 1: Select LLM provider (AC6)
            provider = self._select_provider()

            # Step 2: Build structured prompt (AC1, AC5)
            llm_prompt = self.prompt_builder.build_prompt(
                user_prompt=user_prompt,
                project_context=project_context,
            )
            system_prompt = self.prompt_builder.build_system_prompt()

            logger.debug(f"Built LLM prompt ({len(llm_prompt)} chars)")

            # Step 3: Call LLM API (AC1, AC3)
            response = self._call_llm_with_retry(
                provider=provider,
                system_prompt=system_prompt,
                user_message=llm_prompt,
                timeout_seconds=self.HARD_TIMEOUT_SECONDS,
            )

            # Step 4: Validate response (AC2)
            is_valid, violations = self.response_validator.validate_response(
                response=response.content,
                original_prompt=user_prompt,
            )

            if not is_valid:
                logger.warning(f"Response validation failed: {violations}")
                raise ValidationError(f"Response validation failed: {', '.join(violations)}")

            # Success - return result
            elapsed = time.time() - start_time
            estimated_cost = provider.estimate_cost(
                response.tokens_input,
                response.tokens_output,
            )

            result = EnhancementResult(
                original_prompt=user_prompt,
                enhanced_prompt=self.response_validator.sanitize_response(response.content),
                provider=response.provider,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
                estimated_cost=estimated_cost,
                generation_time_seconds=elapsed,
                was_degraded=False,
            )

            logger.info(
                f"Enhancement successful: {response.tokens_input} input, "
                f"{response.tokens_output} output, ${estimated_cost:.4f}, {elapsed:.2f}s"
            )

            return result

        except EnhancementError:
            # Expected enhancement error
            raise
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in enhancement: {e}")
            if use_degradation:
                return self._degrade_to_generic_enhancement(
                    user_prompt=user_prompt,
                    reason=str(e),
                )
            else:
                raise EnhancementError(
                    f"Enhancement failed: {e}",
                    category="UNEXPECTED_ERROR",
                )

    def _select_provider(self) -> LLMProvider:
        """
        Select LLM provider (AC6).

        Tries OpenAI first, falls back to DeepSeek.

        Returns:
            LLMProvider instance

        Raises:
            AuthenticationError: If no valid API keys available
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")

        if openai_key:
            logger.debug("Using OpenAI provider")
            return create_provider("openai", openai_key)
        elif deepseek_key:
            logger.debug("Using DeepSeek provider (OpenAI unavailable)")
            return create_provider("deepseek", deepseek_key)
        else:
            logger.error("No API keys available")
            raise AuthError("No OPENAI_API_KEY or DEEPSEEK_API_KEY found")

    def _call_llm_with_retry(
        self,
        provider: LLMProvider,
        system_prompt: str,
        user_message: str,
        timeout_seconds: int,
    ) -> LLMResponse:
        """
        Call LLM with retry logic (AC3, AC4).

        Retries once on timeout/network errors, not on auth errors.

        Args:
            provider: LLM provider to use
            system_prompt: System prompt with context
            user_message: User message
            timeout_seconds: Hard timeout limit

        Returns:
            LLMResponse from successful call

        Raises:
            EnhancementError subclass for various error types
        """
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                logger.debug(f"LLM call attempt {attempt + 1}/{self.MAX_RETRIES + 1}")

                response = provider.call(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    timeout_seconds=timeout_seconds,
                )

                logger.debug(f"LLM call succeeded on attempt {attempt + 1}")
                return response

            except AuthenticationError as e:
                # Don't retry auth errors
                logger.error(f"Authentication error: {e}")
                raise AuthError(str(e))

            except RateLimitError as e:
                # Might succeed on retry
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Rate limited, retrying... ({attempt + 1}/{self.MAX_RETRIES})")
                    time.sleep(1)  # Brief backoff
                    continue
                else:
                    logger.error(f"Rate limit exceeded: {e}")
                    raise RateLimitErr(str(e))

            except Timeout as e:
                # Might succeed on retry
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Timeout, retrying... ({attempt + 1}/{self.MAX_RETRIES})")
                    time.sleep(0.5)  # Brief backoff
                    continue
                else:
                    logger.error(f"Timeout after {timeout_seconds}s")
                    raise TimeoutErr(f"LLM timeout after {timeout_seconds}s")

            except Exception as e:
                # Unknown error
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"API error, retrying: {e}")
                    time.sleep(0.5)
                    continue
                else:
                    logger.error(f"API error: {e}")
                    raise ServerError(f"LLM API error: {e}")

    def _degrade_to_generic_enhancement(
        self,
        user_prompt: str,
        reason: str,
    ) -> EnhancementResult:
        """
        Graceful degradation (AC4).

        Returns basic enhancement without project awareness.

        Args:
            user_prompt: Original prompt
            reason: Reason for degradation

        Returns:
            EnhancementResult with degraded quality
        """
        logger.warning(f"Degrading to generic enhancement: {reason}")

        # Simple generic enhancement (note: no project-aware customization)
        enhanced = (
            f"{user_prompt}\n\n"
            f"[Generic enhancement - project-specific guidance not available]\n\n"
            f"Key considerations:\n"
            f"1. Clearly define requirements\n"
            f"2. Provide implementation steps\n"
            f"3. Include testing approach\n"
            f"4. Handle edge cases\n"
            f"5. Document assumptions"
        )

        return EnhancementResult(
            original_prompt=user_prompt,
            enhanced_prompt=enhanced,
            provider="generic-fallback",
            tokens_input=0,
            tokens_output=0,
            estimated_cost=0.0,
            generation_time_seconds=0.1,
            was_degraded=True,
            degradation_reason=reason,
            quality_warnings=[
                "⚠️ Using generic enhancement (no project awareness)",
                f"Reason: {reason}",
                "Project-specific standards were not applied",
            ],
        )
