"""Tests for Story 5.1: Error Classification and User-Friendly Messages."""

import pytest
from src.prompt_enhancement.error_handling.classification import ErrorCategory, ErrorClassifier
from src.prompt_enhancement.error_handling.messages import UserErrorMessage, ErrorMessageFormatter


class TestErrorClassificationAC1:
    """AC1: Error classification into 5 categories."""

    def test_classify_api_key_missing_by_exception(self):
        """Test classifying KeyError as API_KEY_MISSING."""
        category = ErrorClassifier.classify_exception(KeyError("OPENAI_API_KEY"))
        assert category == ErrorCategory.API_KEY_MISSING

    def test_classify_api_timeout_by_exception(self):
        """Test classifying TimeoutError as API_TIMEOUT."""
        category = ErrorClassifier.classify_exception(TimeoutError("API call timeout"))
        assert category == ErrorCategory.API_TIMEOUT

    def test_classify_permission_denied_by_exception(self):
        """Test classifying PermissionError as PERMISSION_DENIED."""
        category = ErrorClassifier.classify_exception(PermissionError("Access denied"))
        assert category == ErrorCategory.PERMISSION_DENIED

    def test_classify_by_message_pattern(self):
        """Test classifying by message pattern."""
        category = ErrorClassifier.classify_exception(
            ValueError("OPENAI_API_KEY not found")
        )
        assert category == ErrorCategory.API_KEY_MISSING

    def test_classify_detection_failed_by_confidence(self):
        """Test classifying low confidence as DETECTION_FAILED."""
        category = ErrorClassifier.classify_detection_failure(0.45)
        assert category == ErrorCategory.DETECTION_FAILED

    def test_classify_not_detection_failed_high_confidence(self):
        """Test that high confidence doesn't classify as DETECTION_FAILED."""
        category = ErrorClassifier.classify_detection_failure(0.75)
        assert category is None

    def test_classify_api_key_missing_both_missing(self):
        """Test classifying when both API keys are missing."""
        category = ErrorClassifier.classify_missing_api_key(
            openai_key_present=False,
            deepseek_key_present=False,
        )
        assert category == ErrorCategory.API_KEY_MISSING

    def test_classify_not_api_key_missing_one_present(self):
        """Test that having one key present means not API_KEY_MISSING."""
        category = ErrorClassifier.classify_missing_api_key(
            openai_key_present=True,
            deepseek_key_present=False,
        )
        assert category is None

    def test_classify_api_timeout_by_elapsed_time(self):
        """Test classifying by elapsed time > 20 seconds."""
        category = ErrorClassifier.classify_api_timeout(25.5)
        assert category == ErrorCategory.API_TIMEOUT

    def test_classify_not_api_timeout_under_threshold(self):
        """Test that time under 20 seconds doesn't classify as timeout."""
        category = ErrorClassifier.classify_api_timeout(15.0)
        assert category is None


class TestErrorClassificationAC2:
    """AC2: API_KEY_MISSING error message."""

    def test_api_key_missing_message_title(self):
        """Test API_KEY_MISSING has correct title."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        assert "❌" in msg.title
        assert "API Key" in msg.title

    def test_api_key_missing_has_setup_step(self):
        """Test API_KEY_MISSING includes /pe-setup step."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        assert any("/pe-setup" in step for step in msg.steps)

    def test_api_key_missing_has_export_step(self):
        """Test API_KEY_MISSING includes export step."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        assert any("export" in step.lower() for step in msg.steps)

    def test_api_key_missing_has_config_file_step(self):
        """Test API_KEY_MISSING includes config file step."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        assert any("config.yaml" in step for step in msg.steps)

    def test_api_key_missing_display_format(self):
        """Test API_KEY_MISSING formats properly for display."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        display = ErrorMessageFormatter.format_for_display(msg)
        assert "❌ API Key Not Configured" in display
        assert "/pe-setup" in display


class TestErrorClassificationAC3:
    """AC3: PROJECT_NOT_DETECTED error message."""

    def test_project_not_detected_message_title(self):
        """Test PROJECT_NOT_DETECTED has warning emoji."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PROJECT_NOT_DETECTED)
        assert "⚠️" in msg.title
        assert "Project" in msg.title

    def test_project_not_detected_has_directory_step(self):
        """Test PROJECT_NOT_DETECTED suggests checking project root."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PROJECT_NOT_DETECTED)
        assert any("project root" in step.lower() for step in msg.steps)

    def test_project_not_detected_has_files_step(self):
        """Test PROJECT_NOT_DETECTED mentions identifying files."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PROJECT_NOT_DETECTED)
        assert any(
            ("package.json" in step or "requirements.txt" in step)
            for step in msg.steps
        )

    def test_project_not_detected_has_generic_fallback(self):
        """Test PROJECT_NOT_DETECTED mentions generic enhancement."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PROJECT_NOT_DETECTED)
        assert any("generic" in step.lower() for step in msg.steps)


class TestErrorClassificationAC4:
    """AC4: DETECTION_FAILED error message."""

    def test_detection_failed_message_title(self):
        """Test DETECTION_FAILED has warning emoji."""
        msg = ErrorMessageFormatter.format_error(
            ErrorCategory.DETECTION_FAILED,
            confidence=0.45,
        )
        assert "⚠️" in msg.title
        assert "Low Confidence" in msg.title

    def test_detection_failed_shows_confidence_percentage(self):
        """Test DETECTION_FAILED includes actual confidence."""
        msg = ErrorMessageFormatter.format_error(
            ErrorCategory.DETECTION_FAILED,
            confidence=0.45,
        )
        assert "45%" in msg.message

    def test_detection_failed_has_override_step(self):
        """Test DETECTION_FAILED suggests using --override."""
        msg = ErrorMessageFormatter.format_error(
            ErrorCategory.DETECTION_FAILED,
            confidence=0.50,
        )
        assert any("--override" in step for step in msg.steps)

    def test_detection_failed_has_config_step(self):
        """Test DETECTION_FAILED suggests creating .pe.yaml."""
        msg = ErrorMessageFormatter.format_error(
            ErrorCategory.DETECTION_FAILED,
            confidence=0.50,
        )
        assert any(".pe.yaml" in step for step in msg.steps)


class TestErrorClassificationAC5:
    """AC5: Standard error message format (no jargon)."""

    def test_api_key_missing_no_jargon(self):
        """Test API_KEY_MISSING message has no technical jargon."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_KEY_MISSING)
        display = ErrorMessageFormatter.format_for_display(msg)
        jargon_terms = ["exception", "traceback", "stack", "errno", "code"]
        for term in jargon_terms:
            assert term.lower() not in display.lower()

    def test_project_not_detected_no_jargon(self):
        """Test PROJECT_NOT_DETECTED message has no technical jargon."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PROJECT_NOT_DETECTED)
        display = ErrorMessageFormatter.format_for_display(msg)
        assert "exception" not in display.lower()
        assert "traceback" not in display.lower()

    def test_detection_failed_no_jargon(self):
        """Test DETECTION_FAILED message has no technical jargon."""
        msg = ErrorMessageFormatter.format_error(
            ErrorCategory.DETECTION_FAILED,
            confidence=0.45,
        )
        display = ErrorMessageFormatter.format_for_display(msg)
        assert "algorithm" not in display.lower()
        assert "threshold" not in display.lower()

    def test_api_timeout_message_clear(self):
        """Test API_TIMEOUT message is clear and actionable."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.API_TIMEOUT)
        assert "⚠️" in msg.title
        assert len(msg.steps) > 0
        display = ErrorMessageFormatter.format_for_display(msg)
        assert "internet" in display.lower() or "connection" in display.lower()

    def test_permission_denied_message_clear(self):
        """Test PERMISSION_DENIED message is clear and actionable."""
        msg = ErrorMessageFormatter.format_error(ErrorCategory.PERMISSION_DENIED)
        assert "⚠️" in msg.title
        assert len(msg.steps) > 0

    def test_emoji_indicators_present(self):
        """Test all error messages use emoji for quick identification."""
        for category in ErrorCategory:
            msg = ErrorMessageFormatter.format_error(category)
            # Should have either ❌ (critical) or ⚠️ (warning)
            assert "❌" in msg.title or "⚠️" in msg.title


class TestErrorClassificationIntegration:
    """Integration tests for error classification and messages."""

    def test_classify_and_format_full_workflow(self):
        """Test complete workflow: exception → classify → format."""
        exc = KeyError("OPENAI_API_KEY")
        category = ErrorClassifier.classify_exception(exc)
        msg = ErrorMessageFormatter.format_error(category)
        display = ErrorMessageFormatter.format_for_display(msg)

        assert category == ErrorCategory.API_KEY_MISSING
        assert "API Key" in display
        assert "❌" in display
        assert "/pe-setup" in display

    def test_recovery_message_for_each_category(self):
        """Test that recovery messages exist for all categories."""
        for category in ErrorCategory:
            recovery = ErrorMessageFormatter.format_recovery_message(category)
            assert "~/.prompt-enhancement/logs/pe.log" in recovery
            assert "Suggested steps:" in recovery
            assert category.value is not None

    def test_message_formatting_consistency(self):
        """Test that message formatting is consistent across categories."""
        categories = [
            ErrorCategory.API_KEY_MISSING,
            ErrorCategory.PROJECT_NOT_DETECTED,
            ErrorCategory.API_TIMEOUT,
            ErrorCategory.PERMISSION_DENIED,
        ]

        for category in categories:
            msg = ErrorMessageFormatter.format_error(category)
            display = ErrorMessageFormatter.format_for_display(msg)

            # All messages should have emoji
            assert "❌" in display or "⚠️" in display
            # All messages should have steps
            assert len(msg.steps) > 0
            # All messages should have title
            assert msg.title is not None
            assert len(msg.title) > 0

    def test_confidence_score_formatting(self):
        """Test that confidence scores are formatted as percentages."""
        for confidence in [0.25, 0.50, 0.75]:
            msg = ErrorMessageFormatter.format_error(
                ErrorCategory.DETECTION_FAILED,
                confidence=confidence,
            )
            expected_pct = f"{int(confidence * 100)}%"
            assert expected_pct in msg.message
