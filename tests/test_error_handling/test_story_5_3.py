"""Tests for Story 5.3: User Confirmation of Degradation Decision."""

import pytest
from src.prompt_enhancement.error_handling.confirmation import (
    UserDecision,
    DiagnosticInfo,
    DegradationConfirmation,
    DiagnosticBuilder,
)
from src.prompt_enhancement.error_handling.degradation import (
    DegradationLevel,
    DegradationInfo,
    DegradationStrategy,
)


class TestDegradationConfirmationAC1:
    """AC1: Show degradation warning before proceeding."""

    def test_confirmation_prompt_shown(self):
        """Test confirmation prompt is shown."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info)

        assert "Quality Will Degrade" in prompt
        assert "⚠️" in prompt
        assert "cannot complete" in prompt.lower() or "could not" in prompt.lower()

    def test_degradation_level_shown(self):
        """Test degradation level is shown in prompt."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info)

        assert "Level 3" in prompt or "Generic" in prompt

    def test_reason_shown_in_prompt(self):
        """Test reason for degradation is shown."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info)

        assert "Reason:" in prompt
        assert "Project not detected" in prompt

    def test_missing_components_listed(self):
        """Test missing components are listed."""
        info = DegradationInfo(
            level=DegradationLevel.WITHOUT_STANDARDS,
            missing_components=["Reliable standards", "Standards detection"],
            reason="Low confidence",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info)

        assert "Reliable standards" in prompt
        assert "✗" in prompt


class TestDegradationConfirmationAC2:
    """AC2: Display degradation confirmation prompt with 3 options."""

    def test_prompt_has_three_options(self):
        """Test prompt includes 3 options."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info, interactive=True)

        assert "[Y]" in prompt
        assert "[N]" in prompt
        assert "[T]" in prompt

    def test_continue_option_labeled(self):
        """Test continue option is labeled."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info, interactive=True)

        assert "[Y] Continue" in prompt

    def test_stop_option_labeled(self):
        """Test stop option is labeled."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info, interactive=True)

        assert "[N] Stop" in prompt

    def test_troubleshoot_option_labeled(self):
        """Test troubleshoot option is labeled."""
        info = DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=["Project context"],
            reason="Project not detected",
        )
        prompt = DegradationConfirmation.format_confirmation_prompt(info, interactive=True)

        assert "[T]" in prompt
        assert "Troubleshoot" in prompt.lower() or "troubleshoot" in prompt.lower()


class TestDegradationConfirmationAC3:
    """AC3: Handle user's continue decision."""

    def test_continue_outcome_message(self):
        """Test message shown when user continues."""
        message = DegradationConfirmation.format_outcome_message(UserDecision.CONTINUE)

        assert "degraded mode" in message.lower()

    def test_continue_decision_enum_exists(self):
        """Test CONTINUE decision enum."""
        assert hasattr(UserDecision, "CONTINUE")
        assert UserDecision.CONTINUE.value == "continue"


class TestDegradationConfirmationAC4:
    """AC4: Handle user's stop decision."""

    def test_stop_outcome_message(self):
        """Test message shown when user stops."""
        message = DegradationConfirmation.format_outcome_message(UserDecision.STOP)

        assert "cancelled" in message.lower()

    def test_stop_decision_enum_exists(self):
        """Test STOP decision enum."""
        assert hasattr(UserDecision, "STOP")
        assert UserDecision.STOP.value == "stop"


class TestDegradationConfirmationAC5:
    """AC5: Handle troubleshoot decision and show diagnostic info."""

    def test_diagnostic_prompt_format(self):
        """Test diagnostic prompt is formatted correctly."""
        diagnostic = DiagnosticInfo(
            attempted_detections=["Project Type Detection"],
            failure_reasons={"Project detection": "No identifying files found"},
            fix_suggestions=["Create package.json for Node.js project"],
            checked_files=["package.json", "requirements.txt"],
            missing_files=["package.json", "requirements.txt"],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Diagnostic Information" in prompt
        assert "📊" in prompt

    def test_diagnostic_shows_attempted_detections(self):
        """Test diagnostic shows attempted detections."""
        diagnostic = DiagnosticInfo(
            attempted_detections=["Project Type Detection", "Standards Detection"],
            failure_reasons={},
            fix_suggestions=[],
            checked_files=[],
            missing_files=[],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Project Type Detection" in prompt
        assert "Standards Detection" in prompt

    def test_diagnostic_shows_failure_reasons(self):
        """Test diagnostic shows failure reasons."""
        diagnostic = DiagnosticInfo(
            attempted_detections=["Project Type Detection"],
            failure_reasons={"Project detection": "No identifying files found"},
            fix_suggestions=[],
            checked_files=[],
            missing_files=[],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Failure Reasons:" in prompt
        assert "No identifying files found" in prompt

    def test_diagnostic_shows_fix_suggestions(self):
        """Test diagnostic shows fix suggestions."""
        diagnostic = DiagnosticInfo(
            attempted_detections=["Project Type Detection"],
            failure_reasons={},
            fix_suggestions=["Create package.json for Node.js projects"],
            checked_files=[],
            missing_files=[],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Potential Fixes:" in prompt
        assert "Create package.json" in prompt

    def test_diagnostic_shows_checked_files(self):
        """Test diagnostic shows checked files."""
        diagnostic = DiagnosticInfo(
            attempted_detections=[],
            failure_reasons={},
            fix_suggestions=[],
            checked_files=["package.json", "requirements.txt"],
            missing_files=["package.json"],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Files Checked:" in prompt
        assert "package.json" in prompt

    def test_diagnostic_shows_file_status(self):
        """Test diagnostic shows file status (found/missing)."""
        diagnostic = DiagnosticInfo(
            attempted_detections=[],
            failure_reasons={},
            fix_suggestions=[],
            checked_files=["package.json", "requirements.txt"],
            missing_files=["package.json", "requirements.txt"],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        # Should show ✗ for missing files
        assert "✗" in prompt

    def test_diagnostic_has_retry_option(self):
        """Test diagnostic prompt includes retry option."""
        diagnostic = DiagnosticInfo(
            attempted_detections=[],
            failure_reasons={},
            fix_suggestions=[],
            checked_files=[],
            missing_files=[],
        )

        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "[R]" in prompt
        assert "Retry" in prompt

    def test_troubleshoot_decision_enum_exists(self):
        """Test TROUBLESHOOT decision enum."""
        assert hasattr(UserDecision, "TROUBLESHOOT")
        assert UserDecision.TROUBLESHOOT.value == "troubleshoot"


class TestDegradationBuilderAC:
    """AC: Diagnostic builder for constructing diagnostic info."""

    def test_diagnostic_builder_add_detection(self):
        """Test builder adds detection attempts."""
        builder = DiagnosticBuilder()
        builder.add_detection_attempt("Project Detection")

        diagnostic = builder.build()
        assert "Project Detection" in diagnostic.attempted_detections

    def test_diagnostic_builder_add_reason(self):
        """Test builder adds failure reasons."""
        builder = DiagnosticBuilder()
        builder.add_failure_reason("Project detection", "No files found")

        diagnostic = builder.build()
        assert "Project detection" in diagnostic.failure_reasons

    def test_diagnostic_builder_add_suggestion(self):
        """Test builder adds fix suggestions."""
        builder = DiagnosticBuilder()
        builder.add_fix_suggestion("Create package.json")

        diagnostic = builder.build()
        assert "Create package.json" in diagnostic.fix_suggestions

    def test_diagnostic_builder_add_files(self):
        """Test builder adds checked files."""
        builder = DiagnosticBuilder()
        builder.add_checked_file("package.json", exists=True)
        builder.add_checked_file("requirements.txt", exists=False)

        diagnostic = builder.build()
        assert "package.json" in diagnostic.checked_files
        assert "requirements.txt" in diagnostic.missing_files

    def test_diagnostic_builder_chain(self):
        """Test builder supports chaining."""
        builder = (
            DiagnosticBuilder()
            .add_detection_attempt("Project Detection")
            .add_failure_reason("Project detection", "No files")
            .add_fix_suggestion("Create files")
            .add_checked_file("package.json", exists=False)
        )

        diagnostic = builder.build()
        assert len(diagnostic.attempted_detections) > 0
        assert len(diagnostic.failure_reasons) > 0
        assert len(diagnostic.fix_suggestions) > 0
        assert len(diagnostic.missing_files) > 0


class TestIntegration_ConfirmationWorkflow:
    """Integration tests for confirmation workflow."""

    def test_full_confirmation_workflow(self):
        """Test complete confirmation workflow."""
        # Simulate degradation decision
        degradation_info = DegradationStrategy.determine_level(
            project_detected=False,
        )

        # Show confirmation prompt
        prompt = DegradationConfirmation.format_confirmation_prompt(degradation_info)

        assert "⚠️" in prompt
        assert "Level 3" in prompt or "Generic" in prompt
        assert "[Y]" in prompt and "[N]" in prompt and "[T]" in prompt

    def test_diagnostic_workflow(self):
        """Test diagnostic information workflow."""
        # Build diagnostic info
        builder = DiagnosticBuilder()
        builder.add_detection_attempt("Project Type Detection")
        builder.add_failure_reason("Project detection", "No identifying files")
        builder.add_fix_suggestion("Create package.json in project root")
        builder.add_checked_file("package.json", exists=False)

        diagnostic = builder.build()
        prompt = DegradationConfirmation.format_diagnostic_prompt(diagnostic)

        assert "Diagnostic" in prompt
        assert "Project Type Detection" in prompt
        assert "Create package.json" in prompt
