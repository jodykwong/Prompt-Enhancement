"""
Progress tracker for real-time command execution feedback.
Handles progress display, phase transitions, and error reporting.
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional


# Configure logging
logger = logging.getLogger(__name__)


class Phase(Enum):
    """Execution phase enumeration."""
    ANALYZING = "analyzing"
    ENHANCING = "enhancing"
    FORMATTING = "formatting"
    ERROR = "error"


class ProgressError(Exception):
    """Exception raised during progress tracking."""
    pass


@dataclass
class ProgressState:
    """Current progress state snapshot."""
    phase: Phase
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float]
    message: str


class ProgressTracker:
    """Tracks and displays progress for command execution."""

    # Phase emoji markers
    PHASE_EMOJI = {
        Phase.ANALYZING: "🔍",
        Phase.ENHANCING: "🚀",
        Phase.FORMATTING: "✓",
        Phase.ERROR: "❌",
    }

    # Phase descriptions
    PHASE_DESCRIPTIONS = {
        Phase.ANALYZING: "Analyzing project",
        Phase.ENHANCING: "Enhancing prompt",
        Phase.FORMATTING: "Formatting results",
        Phase.ERROR: "Error occurred",
    }

    def __init__(self):
        """Initialize the progress tracker."""
        self.current_phase: Optional[Phase] = None
        self.phase_start_time: Optional[float] = None
        self.elapsed_seconds: float = 0.0
        self.estimated_remaining_seconds: Optional[float] = None
        self.current_progress_percent: float = 0.0
        self.error_message: Optional[str] = None
        self.is_error_state: bool = False

    def start_phase(self, phase: Phase) -> None:
        """
        Start a new execution phase.

        Args:
            phase: The phase to start

        Raises:
            ProgressError: If trying to start invalid phase transition
        """
        # Reset elapsed time for new phase
        self.phase_start_time = time.time()
        self.elapsed_seconds = 0.0
        self.estimated_remaining_seconds = None
        self.current_progress_percent = 0.0
        self.current_phase = phase
        self.is_error_state = False
        self.error_message = None

        logger.debug(f"Started phase: {phase.value}")

    def update_progress(
        self,
        percent: Optional[float] = None,
        estimated_remaining_seconds: Optional[float] = None
    ) -> None:
        """
        Update progress for current phase.

        Args:
            percent: Progress percentage (0-100)
            estimated_remaining_seconds: Estimated time remaining
        """
        if self.phase_start_time is not None:
            self.elapsed_seconds = time.time() - self.phase_start_time

        if percent is not None:
            self.current_progress_percent = percent

        if estimated_remaining_seconds is not None:
            self.estimated_remaining_seconds = estimated_remaining_seconds

    def complete_phase(self) -> None:
        """Mark the current phase as complete."""
        if self.current_phase:
            logger.debug(f"Completed phase: {self.current_phase.value}")

    def report_error(
        self,
        phase: Phase,
        error_description: str,
        recovery_guidance: Optional[str] = None
    ) -> None:
        """
        Report an error during execution.

        Args:
            phase: Phase where error occurred
            error_description: Description of the error
            recovery_guidance: Optional guidance for recovery
        """
        self.current_phase = Phase.ERROR
        self.is_error_state = True

        # Build error message
        error_parts = [
            f"❌ {Phase(phase).name.capitalize()} failed: {error_description}"
        ]

        if recovery_guidance:
            error_parts.append(f"   Recovery: {recovery_guidance}")

        self.error_message = "\n".join(error_parts)

        logger.error(self.error_message)

    def is_in_error_state(self) -> bool:
        """Check if tracker is in error state."""
        return self.is_error_state

    def get_current_state(self) -> Optional[ProgressState]:
        """
        Get current progress state.

        Returns:
            ProgressState with current progress information
        """
        if self.current_phase is None:
            return None

        message = self._format_message()

        return ProgressState(
            phase=self.current_phase,
            elapsed_seconds=self.elapsed_seconds,
            estimated_remaining_seconds=self.estimated_remaining_seconds,
            message=message
        )

    def _format_message(self) -> str:
        """
        Format progress message for display.

        Returns:
            Formatted message with emoji and status
        """
        if self.is_error_state:
            return self.error_message or "❌ An error occurred"

        if self.current_phase is None:
            return ""

        # Get phase emoji and description
        emoji = self.PHASE_EMOJI.get(self.current_phase, "")
        description = self.PHASE_DESCRIPTIONS.get(self.current_phase, "")

        # Build message
        message_parts = [f"{emoji} {description}..."]

        # Add elapsed time
        if self.elapsed_seconds > 0:
            message_parts.append(f"[{self.elapsed_seconds:.1f}s elapsed]")

        # Add estimated remaining time
        if self.estimated_remaining_seconds is not None:
            message_parts.append(
                f"[est. {self.estimated_remaining_seconds:.1f}s remaining]"
            )

        # Add progress percentage
        if self.current_progress_percent > 0 and self.current_progress_percent <= 100:
            message_parts.append(f"({self.current_progress_percent:.0f}%)")

        return " ".join(message_parts)

    def format_analyzing_message(self) -> str:
        """Format analyzing phase message (AC1)."""
        self.current_phase = Phase.ANALYZING
        return self._format_message()

    def format_enhancing_message(self) -> str:
        """Format enhancing phase message (AC2)."""
        self.current_phase = Phase.ENHANCING
        return self._format_message()

    def format_complete_message(self) -> str:
        """Format completion message (AC3)."""
        self.current_phase = Phase.FORMATTING
        return "✓ Complete!"

    def format_error_message(
        self,
        phase: Phase,
        error_description: str,
        recovery_guidance: Optional[str] = None
    ) -> str:
        """
        Format error message (AC5).

        Args:
            phase: Phase where error occurred
            error_description: Error description
            recovery_guidance: Optional recovery guidance

        Returns:
            Formatted error message
        """
        self.report_error(phase, error_description, recovery_guidance)
        return self.error_message or ""

    def clear_message(self) -> None:
        """Clear current message (for terminal output handling)."""
        # This would handle terminal escape sequences to clear lines
        # For now, just a placeholder
        pass

    def should_show_long_duration_update(self) -> bool:
        """
        Check if long-duration update should be shown (AC4).

        Returns:
            True if phase has lasted >3 seconds
        """
        return self.elapsed_seconds > 3.0
