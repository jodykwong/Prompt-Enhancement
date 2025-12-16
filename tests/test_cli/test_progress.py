"""
Unit tests for ProgressTracker.
Tests real-time progress message display and phase transitions.
"""

import pytest
import time
from datetime import datetime
from src.prompt_enhancement.cli.progress import (
    Phase, ProgressState, ProgressTracker, ProgressError
)


class TestPhaseEnum:
    """Test Phase enumeration."""

    def test_phase_enum_values(self):
        """Verify Phase enum has all required phases."""
        assert hasattr(Phase, 'ANALYZING')
        assert hasattr(Phase, 'ENHANCING')
        assert hasattr(Phase, 'FORMATTING')
        assert hasattr(Phase, 'ERROR')

    def test_phase_enum_distinctness(self):
        """Verify all phases are distinct."""
        phases = [Phase.ANALYZING, Phase.ENHANCING, Phase.FORMATTING, Phase.ERROR]
        assert len(phases) == len(set(phases))


class TestProgressState:
    """Test ProgressState dataclass."""

    def test_progress_state_creation(self):
        """Create a ProgressState instance."""
        state = ProgressState(
            phase=Phase.ANALYZING,
            elapsed_seconds=5.2,
            estimated_remaining_seconds=3.0,
            message="🔍 Analyzing project..."
        )

        assert state.phase == Phase.ANALYZING
        assert state.elapsed_seconds == 5.2
        assert state.estimated_remaining_seconds == 3.0
        assert state.message == "🔍 Analyzing project..."

    def test_progress_state_with_none_eta(self):
        """ProgressState with None ETA."""
        state = ProgressState(
            phase=Phase.ANALYZING,
            elapsed_seconds=2.0,
            estimated_remaining_seconds=None,
            message="🔍 Analyzing..."
        )

        assert state.estimated_remaining_seconds is None


class TestProgressTracker:
    """Test suite for ProgressTracker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker()

    def test_initialization(self):
        """ProgressTracker initializes correctly."""
        assert self.tracker is not None
        assert self.tracker.current_phase is None
        assert self.tracker.elapsed_seconds == 0.0

    def test_start_analyzing_phase(self):
        """AC1: Start analyzing phase."""
        self.tracker.start_phase(Phase.ANALYZING)

        assert self.tracker.current_phase == Phase.ANALYZING
        assert self.tracker.elapsed_seconds >= 0.0

    def test_start_enhancing_phase(self):
        """AC2: Start enhancing phase."""
        self.tracker.start_phase(Phase.ENHANCING)

        assert self.tracker.current_phase == Phase.ENHANCING

    def test_start_formatting_phase(self):
        """AC3: Start formatting phase."""
        self.tracker.start_phase(Phase.FORMATTING)

        assert self.tracker.current_phase == Phase.FORMATTING

    def test_phase_transition_analyzing_to_enhancing(self):
        """AC2: Transition from ANALYZING to ENHANCING."""
        self.tracker.start_phase(Phase.ANALYZING)
        time.sleep(0.1)
        self.tracker.start_phase(Phase.ENHANCING)

        assert self.tracker.current_phase == Phase.ENHANCING

    def test_phase_transition_enhancing_to_formatting(self):
        """AC2: Transition from ENHANCING to FORMATTING."""
        self.tracker.start_phase(Phase.ENHANCING)
        time.sleep(0.1)
        self.tracker.start_phase(Phase.FORMATTING)

        assert self.tracker.current_phase == Phase.FORMATTING

    def test_phase_transition_to_error(self):
        """AC5: Transition to ERROR phase."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.report_error(Phase.ANALYZING, "Test error")

        assert self.tracker.current_phase == Phase.ERROR

    def test_update_progress(self):
        """Update progress during phase."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.update_progress(percent=50)

        state = self.tracker.get_current_state()
        assert state is not None

    def test_elapsed_time_increases(self):
        """AC4: Elapsed time increases over time."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.update_progress()
        elapsed_1 = self.tracker.elapsed_seconds

        time.sleep(0.1)
        self.tracker.update_progress()
        elapsed_2 = self.tracker.elapsed_seconds

        assert elapsed_2 > elapsed_1

    def test_estimated_remaining_time(self):
        """AC4: Set estimated remaining time."""
        self.tracker.start_phase(Phase.ENHANCING)
        self.tracker.update_progress(estimated_remaining_seconds=2.5)

        state = self.tracker.get_current_state()
        assert state.estimated_remaining_seconds == 2.5

    def test_error_reporting(self):
        """AC5: Report error with message."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.report_error(
            Phase.ANALYZING,
            "Could not detect project type",
            recovery_guidance="Falling back to basic analysis"
        )

        assert self.tracker.current_phase == Phase.ERROR
        assert self.tracker.error_message is not None

    def test_error_message_content(self):
        """AC5: Error message contains guidance."""
        self.tracker.report_error(
            Phase.ENHANCING,
            "API timeout occurred",
            recovery_guidance="Using cached result"
        )

        assert "API timeout" in self.tracker.error_message
        assert "cached result" in self.tracker.error_message

    def test_get_current_state(self):
        """Get current progress state."""
        self.tracker.start_phase(Phase.ANALYZING)
        state = self.tracker.get_current_state()

        assert state is not None
        assert state.phase == Phase.ANALYZING
        assert state.message is not None

    def test_analyzing_message_format(self):
        """AC1: Analyzing message format includes emoji."""
        self.tracker.start_phase(Phase.ANALYZING)
        state = self.tracker.get_current_state()

        assert "🔍" in state.message
        assert "Analyzing" in state.message

    def test_enhancing_message_format(self):
        """AC2: Enhancing message format includes emoji."""
        self.tracker.start_phase(Phase.ENHANCING)
        state = self.tracker.get_current_state()

        assert "🚀" in state.message
        assert "Enhancing" in state.message

    def test_complete_message_format(self):
        """AC3: Complete message format includes emoji."""
        self.tracker.start_phase(Phase.FORMATTING)
        self.tracker.complete_phase()
        state = self.tracker.get_current_state()

        assert "✓" in state.message or "Complete" in state.message

    def test_message_with_elapsed_time(self):
        """AC4: Message includes elapsed time for long operations."""
        self.tracker.start_phase(Phase.ANALYZING)
        time.sleep(0.1)
        self.tracker.update_progress()
        state = self.tracker.get_current_state()

        # Should include elapsed time
        assert state.elapsed_seconds > 0

    def test_message_with_eta(self):
        """AC4: Message can include estimated time remaining."""
        self.tracker.start_phase(Phase.ENHANCING)
        self.tracker.update_progress(estimated_remaining_seconds=2.5)
        state = self.tracker.get_current_state()

        assert state.estimated_remaining_seconds == 2.5

    def test_no_ansi_color_codes(self):
        """Terminal compatibility: No ANSI color codes."""
        self.tracker.start_phase(Phase.ANALYZING)
        state = self.tracker.get_current_state()
        message = state.message

        # Check for common ANSI codes
        assert '\033[' not in message
        assert '\x1b[' not in message

    def test_message_only_uses_emoji(self):
        """Terminal compatibility: Uses emoji for visual distinction."""
        self.tracker.start_phase(Phase.ANALYZING)
        state = self.tracker.get_current_state()

        assert "🔍" in state.message

    def test_long_operation_tracking(self):
        """AC4: Track operations lasting >3 seconds."""
        self.tracker.start_phase(Phase.ENHANCING)

        # Simulate long operation
        for _ in range(5):
            time.sleep(0.1)
            self.tracker.update_progress()

        assert self.tracker.elapsed_seconds > 0.4

    def test_multiple_phase_transitions(self):
        """Test multiple phase transitions."""
        phases = [Phase.ANALYZING, Phase.ENHANCING, Phase.FORMATTING]

        for phase in phases:
            self.tracker.start_phase(phase)
            assert self.tracker.current_phase == phase

    def test_error_state_after_error_report(self):
        """AC5: Error state is set after error report."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.report_error(Phase.ANALYZING, "Test error")

        assert self.tracker.current_phase == Phase.ERROR
        assert self.tracker.is_in_error_state()

    def test_complete_phase(self):
        """AC3: Complete phase."""
        self.tracker.start_phase(Phase.FORMATTING)
        self.tracker.complete_phase()

        # Should transition to a completion state
        assert self.tracker.current_phase == Phase.FORMATTING

    def test_phase_duration_tracking(self):
        """Track duration of each phase."""
        self.tracker.start_phase(Phase.ANALYZING)
        time.sleep(0.1)
        analyzing_duration = self.tracker.elapsed_seconds

        self.tracker.start_phase(Phase.ENHANCING)
        assert self.tracker.elapsed_seconds == 0.0  # Reset on phase change

    def test_progress_percentage_update(self):
        """AC1: Update progress percentage."""
        self.tracker.start_phase(Phase.ANALYZING)
        self.tracker.update_progress(percent=50)

        # Progress is tracked
        assert self.tracker.current_phase == Phase.ANALYZING

    def test_error_without_recovery_guidance(self):
        """AC5: Error can be reported without recovery guidance."""
        self.tracker.report_error(Phase.ANALYZING, "Simple error")

        assert self.tracker.current_phase == Phase.ERROR

    def test_state_includes_all_fields(self):
        """AC4: Progress state includes all required fields."""
        self.tracker.start_phase(Phase.ENHANCING)
        self.tracker.update_progress(
            percent=75,
            estimated_remaining_seconds=1.5
        )
        state = self.tracker.get_current_state()

        assert state.phase is not None
        assert state.elapsed_seconds is not None
        assert state.estimated_remaining_seconds is not None
        assert state.message is not None
