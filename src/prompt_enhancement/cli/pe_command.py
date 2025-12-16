"""
/pe Command Handler for Claude Code.
Handles execution of the `/pe` enhancement command.
"""

import os
import logging
from typing import Dict, Any
from .parser import ParameterParser, ParseError
from .performance import PerformanceTracker, TimeBudget


# Configure logging
logger = logging.getLogger(__name__)


class PeCommand:
    """Handler for Claude Code `/pe` command."""

    # Error category constants
    ERROR_MISSING_PROMPT = "MISSING_PROMPT"
    ERROR_EMPTY_PROMPT = "EMPTY_PROMPT"
    ERROR_INVALID_FLAG = "INVALID_FLAG"
    ERROR_INVALID_OVERRIDE = "INVALID_OVERRIDE"
    ERROR_PARSE_ERROR = "PARSE_ERROR"

    def __init__(self):
        """Initialize the PE command handler."""
        self.parser = ParameterParser()
        self.performance_tracker = PerformanceTracker()
        # Set default time budget (5-15 second target)
        self.time_budget = TimeBudget(
            total_seconds=15,
            analysis_seconds=5,
            standards_seconds=2,
            llm_seconds=5,
            formatting_seconds=1,
            cache_seconds=1
        )
        self.performance_tracker.set_budget(self.time_budget)

    def execute(self, command_string: str) -> Dict[str, Any]:
        """
        Execute a `/pe` command.

        Args:
            command_string: The full command string from Claude Code

        Returns:
            Dictionary with status, prompt, working_dir, overrides, acknowledgment, and performance metrics
        """
        # Reset tracker for new execution
        self.performance_tracker = PerformanceTracker()
        self.performance_tracker.set_budget(self.time_budget)

        try:
            # Track command parsing
            self.performance_tracker.start_phase("command_parsing")

            # Parse the command
            parse_result = self.parser.parse(command_string)
            self.performance_tracker.end_phase("command_parsing")

            # Build acknowledgment
            acknowledgment = self._build_acknowledgment(parse_result.prompt)

            # Get performance metrics
            metrics = self.performance_tracker.get_metrics()

            # Return success result
            return {
                "status": "success",
                "prompt": parse_result.prompt,
                "working_dir": parse_result.working_dir,
                "overrides": parse_result.overrides,
                "acknowledgment": acknowledgment,
                "error_code": None,
                "performance": {
                    "total_execution_time": metrics.total_execution_time,
                    "phase_times": metrics.phase_times,
                    "cache_hit": metrics.cache_hit,
                },
            }

        except ParseError as e:
            # Handle parse errors
            return self._handle_parse_error(str(e))
        except (ValueError, TypeError, AttributeError) as e:
            # Specific error handling instead of catching all exceptions
            logger.error(f"Error in PeCommand.execute: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "An unexpected error occurred while processing your command.",
                "error_code": "UNEXPECTED_ERROR",
            }

    def _build_acknowledgment(self, prompt: str) -> str:
        """
        Build a processing acknowledgment message.

        Args:
            prompt: The parsed prompt text

        Returns:
            Friendly acknowledgment message with progress emoji
        """
        # Truncate long prompts for display
        display_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
        return f"🔍 Analyzing your project...\n   Prompt: {display_prompt}"

    def _handle_parse_error(self, error_message: str) -> Dict[str, Any]:
        """
        Convert parse errors to user-friendly error messages.

        Args:
            error_message: Error message from parser

        Returns:
            Error result dictionary
        """
        error_msg_lower = error_message.lower()

        # Classify the error
        if "prompt" in error_msg_lower and "missing" in error_msg_lower:
            error_code = self.ERROR_MISSING_PROMPT
            message = (
                'Missing required prompt.\n'
                'Usage: /pe "your prompt here"\n\n'
                'Example: /pe "Help me write better error handling"'
            )
        elif "empty" in error_msg_lower:
            error_code = self.ERROR_EMPTY_PROMPT
            message = (
                'Prompt cannot be empty.\n'
                'Usage: /pe "your prompt here"'
            )
        elif "flag" in error_msg_lower and "invalid" in error_msg_lower:
            error_code = self.ERROR_INVALID_FLAG
            message = (
                f'{error_message}\n\n'
                'Valid flags: --override, --template, --type'
            )
        elif "override" in error_msg_lower:
            error_code = self.ERROR_INVALID_OVERRIDE
            message = (
                f'{error_message}\n\n'
                'Example: /pe --override naming=camelCase "my prompt"'
            )
        elif "quote" in error_msg_lower:
            error_code = self.ERROR_PARSE_ERROR
            message = (
                'Prompt must be enclosed in quotes.\n'
                'Example: /pe "your prompt here"'
            )
        else:
            # Generic parse error
            error_code = self.ERROR_PARSE_ERROR
            message = (
                f'{error_message}\n\n'
                'Usage: /pe "your prompt here"'
            )

        logger.debug(f"Parse error: {error_message}")

        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
        }
