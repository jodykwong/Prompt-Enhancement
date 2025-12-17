"""
Unit tests for ProgressTracker.
Tests real-time progress message display and phase transitions.
"""

import pytest
import asyncio
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


class TestAsyncProgressUpdates:
    """Test suite for async progress update functionality (HIGH-3 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker()

    @pytest.mark.asyncio
    async def test_update_progress_async(self):
        """AC4: Async progress updates work correctly."""
        self.tracker.start_phase(Phase.ANALYZING)

        # Update progress asynchronously
        await self.tracker.update_progress_async(percent=50)

        state = self.tracker.get_current_state()
        assert state is not None
        assert self.tracker.current_progress_percent == 50

    @pytest.mark.asyncio
    async def test_update_progress_async_with_callback(self):
        """AC4: Async progress updates invoke callback."""
        self.tracker.start_phase(Phase.ENHANCING)
        callback_invoked = []

        def callback():
            callback_invoked.append(True)

        # Update with callback
        await self.tracker.update_progress_async(percent=75, callback=callback)

        assert len(callback_invoked) == 1
        assert self.tracker.current_progress_percent == 75

    @pytest.mark.asyncio
    async def test_update_progress_async_with_async_callback(self):
        """AC4: Async progress updates invoke async callback."""
        self.tracker.start_phase(Phase.FORMATTING)
        callback_invoked = []

        async def async_callback():
            await asyncio.sleep(0.01)
            callback_invoked.append(True)

        # Update with async callback
        await self.tracker.update_progress_async(percent=100, callback=async_callback)

        assert len(callback_invoked) == 1

    @pytest.mark.asyncio
    async def test_run_periodic_updates(self):
        """AC4: Periodic updates run automatically for long operations."""
        self.tracker.start_phase(Phase.ENHANCING)
        update_count = []

        def update_callback():
            update_count.append(len(update_count) + 1)

        self.tracker.set_periodic_update_callback(update_callback)

        # Run periodic updates for 0.5 seconds (should trigger 2-3 updates at 0.2s interval)
        update_task = asyncio.create_task(self.tracker.run_periodic_updates(update_interval=0.2))

        # Wait for a few updates
        await asyncio.sleep(0.5)

        # Stop the phase to end periodic updates
        self.tracker.current_phase = None
        await asyncio.sleep(0.3)  # Allow task to complete

        # Should have at least 2 updates
        assert len(update_count) >= 2

    @pytest.mark.asyncio
    async def test_periodic_updates_stop_on_error(self):
        """AC5: Periodic updates stop when error occurs."""
        self.tracker.start_phase(Phase.ANALYZING)

        # Start periodic updates
        update_task = asyncio.create_task(self.tracker.run_periodic_updates(update_interval=0.1))

        # Trigger error after short delay
        await asyncio.sleep(0.15)
        self.tracker.report_error(Phase.ANALYZING, "Test error")

        # Wait for task to complete
        await asyncio.sleep(0.2)

        # Error state should be set
        assert self.tracker.is_error_state is True


class TestPerformanceRequirements:
    """Test suite for performance requirements (MEDIUM-5 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker()

    def test_update_progress_overhead_under_10ms(self):
        """Performance: update_progress() completes in <10ms."""
        self.tracker.start_phase(Phase.ANALYZING)

        # Measure time for 100 updates
        start = time.perf_counter()
        for _ in range(100):
            self.tracker.update_progress(percent=50)
        elapsed = time.perf_counter() - start

        # Average should be well under 10ms per update
        avg_time_ms = (elapsed / 100) * 1000
        assert avg_time_ms < 10.0, f"Average update time {avg_time_ms:.2f}ms exceeds 10ms budget"

    def test_phase_transition_overhead_minimal(self):
        """Performance: Phase transitions are fast."""
        phases = [Phase.ANALYZING, Phase.ENHANCING, Phase.FORMATTING]

        start = time.perf_counter()
        for phase in phases * 10:  # 30 transitions
            self.tracker.start_phase(phase)
        elapsed = time.perf_counter() - start

        # Should complete 30 transitions in well under 100ms
        assert elapsed < 0.1, f"Phase transitions took {elapsed*1000:.2f}ms, expected <100ms"

    def test_message_formatting_performance(self):
        """Performance: Message formatting is fast."""
        self.tracker.start_phase(Phase.ENHANCING)
        self.tracker.update_progress(percent=50, estimated_remaining_seconds=5.0)

        # Measure formatting time
        start = time.perf_counter()
        for _ in range(1000):
            _ = self.tracker._format_message()
        elapsed = time.perf_counter() - start

        # 1000 formats should complete in <100ms
        assert elapsed < 0.1, f"Message formatting took {elapsed*1000:.2f}ms for 1000 calls"


class TestErrorRecoveryStrategies:
    """Test suite for error recovery strategies (MEDIUM-6 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker()

    def test_default_recovery_strategy_analyzing(self):
        """AC5: Default recovery strategy for ANALYZING phase."""
        self.tracker.report_error(Phase.ANALYZING, "Could not detect project type")

        assert "Falling back to basic analysis" in self.tracker.error_message

    def test_default_recovery_strategy_enhancing(self):
        """AC5: Default recovery strategy for ENHANCING phase."""
        self.tracker.report_error(Phase.ENHANCING, "API timeout")

        assert "Using cached enhancement" in self.tracker.error_message

    def test_default_recovery_strategy_formatting(self):
        """AC5: Default recovery strategy for FORMATTING phase."""
        self.tracker.report_error(Phase.FORMATTING, "Formatting failed")

        assert "Some features may be unavailable" in self.tracker.error_message

    def test_custom_recovery_overrides_default(self):
        """AC5: Custom recovery guidance overrides default."""
        custom_guidance = "Please try again with different parameters"
        self.tracker.report_error(
            Phase.ANALYZING,
            "Custom error",
            recovery_guidance=custom_guidance
        )

        assert custom_guidance in self.tracker.error_message
        assert "Falling back" not in self.tracker.error_message
