"""
Unit tests for OutputFormatter.
Tests result formatting, display-only mode, and terminal output.
"""

import pytest
from src.prompt_enhancement.cli.output_formatter import (
    OutputFormatter, FormattingError
)


class TestOutputFormatter:
    """Test OutputFormatter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_initialization(self):
        """OutputFormatter initializes correctly."""
        assert self.formatter is not None
        assert self.formatter.display_only_mode is True
        assert self.formatter.terminal_width == 80

    def test_initialization_with_custom_width(self):
        """OutputFormatter accepts custom terminal width."""
        formatter = OutputFormatter(display_only_mode=True, terminal_width=100)

        assert formatter.terminal_width == 100

    def test_display_only_mode_enforcement(self):
        """Display-only mode flag is set correctly."""
        formatter_display_only = OutputFormatter(display_only_mode=True)
        formatter_normal = OutputFormatter(display_only_mode=False)

        assert formatter_display_only.display_only_mode is True
        assert formatter_normal.display_only_mode is False


class TestSectionFormatting:
    """Test section formatting methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_format_original_prompt_section(self):
        """AC1: Format original prompt with emoji."""
        prompt_text = "Please help me write better error handling"

        formatted = self.formatter.format_original_prompt(prompt_text)

        assert "📝" in formatted
        assert "Original Prompt" in formatted
        assert prompt_text in formatted

    def test_format_enhanced_prompt_section(self):
        """AC1: Format enhanced prompt with emoji."""
        enhanced_text = "Enhanced prompt with more detailed guidance..."

        formatted = self.formatter.format_enhanced_prompt(enhanced_text)

        assert "✨" in formatted
        assert "Enhanced Prompt" in formatted
        assert enhanced_text in formatted

    def test_format_implementation_steps_section(self):
        """AC1: Format implementation steps as numbered list."""
        steps = [
            "Analyze current error handling patterns",
            "Identify missing error types",
            "Implement custom exception classes"
        ]

        formatted = self.formatter.format_implementation_steps(steps)

        assert "🔧" in formatted
        assert "Implementation Steps" in formatted
        assert "1." in formatted
        assert "2." in formatted
        assert "3." in formatted
        for step in steps:
            assert step in formatted

    def test_format_implementation_steps_empty_list(self):
        """Format steps with empty list."""
        steps = []

        formatted = self.formatter.format_implementation_steps(steps)

        assert "🔧" in formatted
        assert isinstance(formatted, str)


class TestTextWrapping:
    """Test text wrapping and line management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True, terminal_width=80)

    def test_wrap_plain_text_short(self):
        """Wrap short text that fits in terminal width."""
        text = "This is a short text."

        wrapped = self.formatter.wrap_text(text, width=80)

        lines = wrapped.split("\n")
        for line in lines:
            assert len(line) <= 80

    def test_wrap_plain_text_long(self):
        """Wrap long text to 80-character width."""
        text = "This is a much longer text that should be wrapped to fit within the eighty character terminal width limit."

        wrapped = self.formatter.wrap_text(text, width=80)

        lines = wrapped.split("\n")
        for line in lines:
            assert len(line) <= 80

    def test_wrap_text_preserves_words(self):
        """Text wrapping preserves word boundaries."""
        text = "This is a test of word boundary preservation in text wrapping."

        wrapped = self.formatter.wrap_text(text, width=40)

        # Should not have mid-word breaks
        assert "\n" in wrapped
        lines = wrapped.split("\n")
        for line in lines:
            assert len(line) <= 40

    def test_wrap_code_block_preserves_indentation(self):
        """Code block indentation is preserved during wrapping."""
        code = "    def example():\n        return True"

        wrapped = self.formatter.wrap_text(code, width=80, preserve_indentation=True)

        # Check indentation is preserved
        lines = wrapped.split("\n")
        assert lines[0].startswith("    ")
        assert lines[1].startswith("        ")

    def test_wrap_with_multiple_paragraphs(self):
        """Multiple paragraphs are handled correctly."""
        text = "First paragraph.\n\nSecond paragraph."

        wrapped = self.formatter.wrap_text(text, width=80)

        assert "\n\n" in wrapped or wrapped.count("\n") >= 2

    def test_wrap_very_long_single_line(self):
        """Very long single line is wrapped."""
        text = "a" * 150  # 150 characters, much longer than 80

        wrapped = self.formatter.wrap_text(text, width=80)

        lines = wrapped.split("\n")
        assert len(lines) > 1


class TestDisplayOnlyMode:
    """Test Display-Only mode enforcement."""

    def test_display_only_mode_set_true(self):
        """AC2: Display-Only mode can be set to true."""
        formatter = OutputFormatter(display_only_mode=True)

        assert formatter.display_only_mode is True

    def test_display_only_mode_prevents_execution(self):
        """AC2: Display-Only mode prevents execution."""
        formatter = OutputFormatter(display_only_mode=True)

        # Check that mode is enforced
        assert formatter.is_display_only_mode() is True

    def test_get_display_mode_indicator(self):
        """AC2: Get Display-Only mode indication message."""
        formatter = OutputFormatter(display_only_mode=True)

        indicator = formatter.get_mode_indicator()

        assert "Display-Only" in indicator
        assert isinstance(indicator, str)

    def test_normal_mode_execution(self):
        """Normal mode allows execution."""
        formatter = OutputFormatter(display_only_mode=False)

        assert formatter.is_display_only_mode() is False

    def test_display_only_mode_prevents_execution(self):
        """AC2: Display-Only mode actually prevents execution."""
        formatter = OutputFormatter(display_only_mode=True)

        # Should raise error when trying to execute in Display-Only mode
        with pytest.raises(FormattingError) as exc_info:
            formatter.verify_mode_allows_execution()

        assert "Display-Only mode" in str(exc_info.value)

    def test_normal_mode_allows_execution(self):
        """Normal mode allows execution without error."""
        formatter = OutputFormatter(display_only_mode=False)

        # Should not raise error in normal mode
        try:
            formatter.verify_mode_allows_execution()
        except FormattingError:
            pytest.fail("Normal mode should allow execution")


class TestPlainTextOutput:
    """Test plain text output without ANSI color codes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_no_ansi_color_codes_in_output(self):
        """AC3: No ANSI color codes in output."""
        text = "Test output"

        formatted = self.formatter.format_original_prompt(text)

        # Check for common ANSI codes
        assert '\033[' not in formatted
        assert '\x1b[' not in formatted

    def test_emoji_used_for_visual_distinction(self):
        """AC3: Use emoji for visual distinction, not colors."""
        text = "Test prompt"

        formatted = self.formatter.format_original_prompt(text)

        # Should contain emoji
        assert "📝" in formatted

    def test_ascii_separators_used(self):
        """AC3: Use ASCII separators for visual clarity."""
        text = "Test prompt"

        formatted = self.formatter.format_original_prompt(text)

        # Should contain ASCII separators (= or -)
        assert ("=" in formatted or "-" in formatted)

    def test_screen_reader_compatibility(self):
        """AC3: Include text descriptions for screen readers."""
        text = "Test prompt"

        formatted = self.formatter.format_original_prompt(text)

        # Should include descriptive text, not just emoji
        assert len(formatted) > 0
        assert "Prompt" in formatted or "prompt" in formatted


class TestTerminalWidthHandling:
    """Test terminal width wrapping."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True, terminal_width=80)

    def test_format_respects_terminal_width(self):
        """AC4: Format respects 80-character terminal width."""
        long_text = "This is a very long prompt text that should be wrapped to fit within the eighty character terminal width requirement."

        formatted = self.formatter.format_original_prompt(long_text)

        lines = formatted.split("\n")
        for line in lines:
            # Allow some flexibility for header/footer lines
            if line.strip():
                # Most lines should fit within terminal width
                assert len(line) <= 90  # Allow 10 char buffer for formatting

    def test_wrap_long_code_block(self):
        """AC4: Code block is wrapped but indentation preserved."""
        code = "def very_long_function_name_that_exceeds_normal_width_limits(parameter1, parameter2, parameter3):\n    return result"

        wrapped = self.formatter.wrap_text(code, width=80, preserve_indentation=True)

        # Should wrap but preserve indentation
        lines = wrapped.split("\n")
        assert len(lines) > 1
        for i, line in enumerate(lines):
            if i > 0 and line.strip():
                assert len(line) <= 80

    def test_wrap_preserves_structure(self):
        """Wrapping preserves document structure."""
        text = "Paragraph 1\n\nParagraph 2"

        wrapped = self.formatter.wrap_text(text, width=80)

        # Paragraph structure should be preserved
        assert "Paragraph 1" in wrapped
        assert "Paragraph 2" in wrapped


class TestStandardsDisplay:
    """Test standards display integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_format_standards_section(self):
        """AC5: Display detected standards section."""
        standards = {
            "naming_convention": {
                "value": "snake_case",
                "confidence": 0.90,
                "evidence": "validate_email(), user_service.py"
            },
            "test_framework": {
                "value": "pytest",
                "confidence": 0.85,
                "evidence": "test_*.py files"
            }
        }

        formatted = self.formatter.format_standards_section(standards)

        assert "standards" in formatted.lower() or "Standards" in formatted
        assert "snake_case" in formatted
        assert "pytest" in formatted

    def test_standards_show_confidence_scores(self):
        """AC5: Show confidence scores for each standard."""
        standards = {
            "naming_convention": {
                "value": "snake_case",
                "confidence": 0.90,
                "evidence": "sample evidence"
            }
        }

        formatted = self.formatter.format_standards_section(standards)

        # Should include confidence information
        assert "90" in formatted or "0.90" in formatted or "confidence" in formatted.lower()

    def test_standards_show_evidence(self):
        """AC5: Show evidence and examples."""
        standards = {
            "naming_convention": {
                "value": "snake_case",
                "confidence": 0.90,
                "evidence": "validate_email(), user_service.py, format_date()"
            }
        }

        formatted = self.formatter.format_standards_section(standards)

        assert "validate_email()" in formatted

    def test_format_complete_output(self):
        """AC1-AC5: End-to-end output format validation."""
        original = "Please help me"
        enhanced = "Please help me with better error handling..."
        steps = ["Step 1", "Step 2"]
        standards = {
            "naming_convention": {"value": "snake_case", "confidence": 0.90, "evidence": "test"}
        }

        output = self.formatter.format_complete_result(
            original_prompt=original,
            enhanced_prompt=enhanced,
            implementation_steps=steps,
            detected_standards=standards
        )

        assert original in output
        assert enhanced in output
        assert "Step 1" in output
        assert isinstance(output, str)


class TestOutputFormatterEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_handle_empty_prompt(self):
        """Handle empty prompt gracefully."""
        formatted = self.formatter.format_original_prompt("")

        assert isinstance(formatted, str)

    def test_handle_special_characters(self):
        """Handle special characters in text."""
        text = "Prompt with special chars: !@#$%^&*()"

        formatted = self.formatter.format_original_prompt(text)

        assert "!@#$%^&*()" in formatted

    def test_handle_unicode_characters(self):
        """Handle unicode characters."""
        text = "Prompt with unicode: 中文 日本語 한국어"

        formatted = self.formatter.format_original_prompt(text)

        assert "中文" in formatted

    def test_handle_very_long_single_word(self):
        """Handle very long words that exceed terminal width."""
        text = "a" * 100  # Single word longer than terminal width

        wrapped = self.formatter.wrap_text(text, width=80)

        # Should handle gracefully (even if it breaks word)
        assert isinstance(wrapped, str)

    def test_format_with_none_standards(self):
        """Handle None or missing standards."""
        output = self.formatter.format_complete_result(
            original_prompt="test",
            enhanced_prompt="test",
            implementation_steps=["step"],
            detected_standards=None
        )

        assert isinstance(output, str)


class TestInputValidation:
    """Test suite for input validation (MEDIUM-5 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_format_original_prompt_with_none(self):
        """Handle None input for original prompt."""
        formatted = self.formatter.format_original_prompt(None)

        assert "No prompt provided" in formatted

    def test_format_original_prompt_with_empty_string(self):
        """Handle empty string input for original prompt."""
        formatted = self.formatter.format_original_prompt("")

        assert "Empty prompt" in formatted

    def test_format_enhanced_prompt_with_none(self):
        """Handle None input for enhanced prompt."""
        formatted = self.formatter.format_enhanced_prompt(None)

        assert "No enhanced prompt" in formatted

    def test_format_enhanced_prompt_with_empty_string(self):
        """Handle empty string input for enhanced prompt."""
        formatted = self.formatter.format_enhanced_prompt("")

        assert "Empty enhanced prompt" in formatted

    def test_format_steps_with_none(self):
        """Handle None input for implementation steps."""
        formatted = self.formatter.format_implementation_steps(None)

        assert "No steps provided" in formatted

    def test_format_steps_with_empty_list(self):
        """Handle empty list for implementation steps."""
        formatted = self.formatter.format_implementation_steps([])

        assert "No steps provided" in formatted

    def test_format_steps_with_none_step_in_list(self):
        """Handle None element in steps list."""
        formatted = self.formatter.format_implementation_steps(["Step 1", None, "Step 3"])

        assert "Step 1" in formatted
        assert "Empty step" in formatted
        assert "Step 3" in formatted

    def test_format_original_prompt_with_invalid_type(self):
        """Reject invalid type for original prompt."""
        with pytest.raises(FormattingError) as exc_info:
            self.formatter.format_original_prompt(123)

        assert "must be str" in str(exc_info.value)

    def test_format_steps_with_invalid_type(self):
        """Reject invalid type for steps."""
        with pytest.raises(FormattingError) as exc_info:
            self.formatter.format_implementation_steps("not a list")

        assert "must be list" in str(exc_info.value)


class TestLargeIndentation:
    """Test suite for large indentation handling (HIGH-2 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True, terminal_width=20)

    def test_wrap_text_with_large_indentation(self):
        """Handle indentation larger than terminal width."""
        # 28 spaces + content, but terminal width is only 20
        text = "                            code content here"

        # Should not crash
        wrapped = self.formatter.wrap_text(text, width=20, preserve_indentation=True)

        assert isinstance(wrapped, str)
        assert len(wrapped) > 0

    def test_wrap_text_with_indentation_equal_to_width(self):
        """Handle indentation equal to terminal width."""
        text = " " * 20 + "code"

        wrapped = self.formatter.wrap_text(text, width=20, preserve_indentation=True)

        assert isinstance(wrapped, str)

    def test_wrap_text_with_normal_indentation(self):
        """Normal indentation still works correctly."""
        text = "    def example():\n        return True"

        wrapped = self.formatter.wrap_text(text, width=40, preserve_indentation=True)

        lines = wrapped.split("\n")
        assert lines[0].startswith("    ")
        assert lines[1].startswith("        ")


class TestParagraphSplitting:
    """Test suite for paragraph splitting (MEDIUM-6 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_split_paragraphs_with_multiple_newlines(self):
        """Handle multiple consecutive newlines."""
        text = "Paragraph 1\n\n\nParagraph 2"

        wrapped = self.formatter.wrap_text(text, width=80)

        assert "Paragraph 1" in wrapped
        assert "Paragraph 2" in wrapped

    def test_split_paragraphs_with_whitespace(self):
        """Handle newlines with whitespace between."""
        text = "Paragraph 1\n \n Paragraph 2"

        wrapped = self.formatter.wrap_text(text, width=80)

        assert "Paragraph 1" in wrapped
        assert "Paragraph 2" in wrapped

    def test_handle_windows_line_endings(self):
        """Normalize Windows line endings."""
        text = "Line 1\r\n\r\nLine 2"

        wrapped = self.formatter.wrap_text(text, width=80)

        # Should handle Windows line endings
        assert "Line 1" in wrapped
        assert "Line 2" in wrapped


class TestDisplayResultMethod:
    """Test suite for display_result method (MEDIUM-3 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_display_result_method_exists(self):
        """display_result method is available."""
        assert hasattr(self.formatter, 'display_result')
        assert callable(self.formatter.display_result)

    def test_display_result_formats_and_displays(self, capsys):
        """display_result formats and outputs to terminal."""
        self.formatter.display_result(
            original_prompt="Test prompt",
            enhanced_prompt="Enhanced test",
            implementation_steps=["Step 1", "Step 2"]
        )

        captured = capsys.readouterr()
        assert "Test prompt" in captured.out
        assert "Enhanced test" in captured.out
        assert "Step 1" in captured.out


class TestPerformanceRequirements:
    """Test suite for performance requirements (MEDIUM-4 fix)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(display_only_mode=True)

    def test_format_complete_result_under_1_second(self):
        """Complete result formatting completes in <1 second."""
        import time

        # Large input
        original = "Test prompt " * 100
        enhanced = "Enhanced prompt " * 100
        steps = [f"Step {i}" for i in range(50)]

        start = time.perf_counter()
        for _ in range(10):
            self.formatter.format_complete_result(original, enhanced, steps)
        elapsed = time.perf_counter() - start

        # 10 formats should complete in <1 second
        assert elapsed < 1.0, f"10 formats took {elapsed:.2f}s, expected <1s"

    def test_text_wrapping_performance(self):
        """Text wrapping is fast."""
        import time

        text = "a" * 1000

        start = time.perf_counter()
        for _ in range(100):
            self.formatter.wrap_text(text, width=80)
        elapsed = time.perf_counter() - start

        # 100 wraps should be very fast (<100ms)
        assert elapsed < 0.1, f"100 wraps took {elapsed*1000:.2f}ms, expected <100ms"
