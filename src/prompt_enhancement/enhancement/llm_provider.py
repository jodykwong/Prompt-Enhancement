"""
Abstract LLM provider interface for enhancement generation.

Defines common interface for different LLM providers (OpenAI, DeepSeek).
Enables provider-agnostic LLM calls with provider strategy pattern.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM API call."""

    content: str  # Enhanced prompt text
    tokens_input: int
    tokens_output: int
    model: str
    provider: str  # "openai" or "deepseek"
    latency_seconds: float


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Defines interface that all providers (OpenAI, DeepSeek) must implement.
    Enables strategy pattern for provider selection and fallback.
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for authentication
            model: Model name (e.g., "gpt-4-turbo")
        """
        self.api_key = api_key
        self.model = model
        logger.debug(f"Initialized {self.__class__.__name__} with model {model}")

    @abstractmethod
    def call(
        self,
        system_prompt: str,
        user_message: str,
        timeout_seconds: int = 30,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Make LLM API call.

        Args:
            system_prompt: System prompt with project context
            user_message: User message with original prompt
            timeout_seconds: Timeout for API call
            max_tokens: Maximum response tokens

        Returns:
            LLMResponse with enhancement result

        Raises:
            TimeoutError: If call exceeds timeout
            AuthenticationError: If API key invalid
            RateLimitError: If rate limited
            APIError: For other API errors
        """
        pass

    @abstractmethod
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimate cost of API call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pass

    def validate_api_key(self) -> bool:
        """
        Validate that API key is set and not empty.

        Returns:
            True if API key is valid
        """
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    def get_provider_name(self) -> str:
        """
        Get provider name for logging and display.

        Returns:
            Provider name (e.g., "OpenAI", "DeepSeek")
        """
        return self.__class__.__name__.replace("Provider", "")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for LLM enhancements."""

    # Pricing (as of Dec 2024)
    # GPT-4 Turbo: $0.01 per 1K input tokens, $0.03 per 1K output tokens
    INPUT_COST_PER_1K_TOKENS = 0.01
    OUTPUT_COST_PER_1K_TOKENS = 0.03

    def __init__(self, api_key: str):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (sk-...)
        """
        super().__init__(api_key, model="gpt-4-turbo")

    def call(
        self,
        system_prompt: str,
        user_message: str,
        timeout_seconds: int = 30,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Make OpenAI API call (AC1, AC3)."""
        import time
        from openai import OpenAI, AuthenticationError, RateLimitError
        from openai import Timeout as OpenAITimeout

        start_time = time.time()

        try:
            client = OpenAI(api_key=self.api_key)

            logger.debug(
                f"Calling OpenAI {self.model} with {len(system_prompt)} chars system "
                f"+ {len(user_message)} chars user message"
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=timeout_seconds,
            )

            latency = time.time() - start_time

            result = LLMResponse(
                content=response.choices[0].message.content,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                model=self.model,
                provider="openai",
                latency_seconds=latency,
            )

            logger.info(
                f"OpenAI call successful: {result.tokens_input} input, "
                f"{result.tokens_output} output tokens, {latency:.2f}s"
            )

            return result

        except AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {e}")
            raise
        except RateLimitError as e:
            logger.warning(f"OpenAI rate limited: {e}")
            raise
        except OpenAITimeout as e:
            logger.warning(f"OpenAI call timed out: {e}")
            raise TimeoutError(f"OpenAI API timeout after {timeout_seconds}s") from e
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate OpenAI API call cost."""
        input_cost = (input_tokens / 1000) * self.INPUT_COST_PER_1K_TOKENS
        output_cost = (output_tokens / 1000) * self.OUTPUT_COST_PER_1K_TOKENS
        return input_cost + output_cost


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider for LLM enhancements (OpenAI-compatible)."""

    # DeepSeek V3.2 pricing (as of Dec 2024)
    # deepseek-reasoner: $0.0055 per 1K input tokens, $0.022 per 1K output tokens
    INPUT_COST_PER_1K_TOKENS = 0.0055
    OUTPUT_COST_PER_1K_TOKENS = 0.022

    def __init__(self, api_key: str):
        """
        Initialize DeepSeek provider with V3.2 reasoner model.

        Args:
            api_key: DeepSeek API key
        """
        super().__init__(api_key, model="deepseek-reasoner")

    def call(
        self,
        system_prompt: str,
        user_message: str,
        timeout_seconds: int = 30,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Make DeepSeek API call (via OpenAI-compatible endpoint)."""
        import time
        from openai import OpenAI, AuthenticationError, RateLimitError
        from openai import Timeout as OpenAITimeout

        start_time = time.time()

        try:
            # DeepSeek uses OpenAI-compatible API format with V3.2 endpoint
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )

            logger.debug(
                f"Calling DeepSeek {self.model} (V3.2 Reasoning Mode) via OpenAI-compatible API with "
                f"{len(system_prompt)} chars system + {len(user_message)} chars user"
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=timeout_seconds,
            )

            latency = time.time() - start_time

            result = LLMResponse(
                content=response.choices[0].message.content,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                model=self.model,
                provider="deepseek",
                latency_seconds=latency,
            )

            logger.info(
                f"DeepSeek call successful: {result.tokens_input} input, "
                f"{result.tokens_output} output tokens, {latency:.2f}s"
            )

            return result

        except AuthenticationError as e:
            logger.error(f"DeepSeek authentication failed: {e}")
            raise
        except RateLimitError as e:
            logger.warning(f"DeepSeek rate limited: {e}")
            raise
        except OpenAITimeout as e:
            logger.warning(f"DeepSeek call timed out: {e}")
            raise TimeoutError(f"DeepSeek API timeout after {timeout_seconds}s") from e
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate DeepSeek API call cost."""
        input_cost = (input_tokens / 1000) * self.INPUT_COST_PER_1K_TOKENS
        output_cost = (output_tokens / 1000) * self.OUTPUT_COST_PER_1K_TOKENS
        return input_cost + output_cost


def create_provider(provider_name: str, api_key: str) -> LLMProvider:
    """
    Factory function to create LLM provider.

    Args:
        provider_name: "openai" or "deepseek"
        api_key: API key for provider

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider_name not recognized
    """
    if provider_name.lower() == "openai":
        return OpenAIProvider(api_key)
    elif provider_name.lower() == "deepseek":
        return DeepSeekProvider(api_key)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
