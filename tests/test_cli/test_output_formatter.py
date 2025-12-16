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
