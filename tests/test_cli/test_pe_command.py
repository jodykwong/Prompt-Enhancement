"""
Unit tests for PeCommand.
Tests the `/pe` command handler and Claude Code integration.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.prompt_enhancement.cli.pe_command import PeCommand
from src.prompt_enhancement.cli.parser import ParseError


class TestPeCommand:
    """Test suite for PeCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = PeCommand()

    def test_basic_command_parsing(self):
        """AC1: Basic `/pe "prompt"` command execution."""
        result = self.command.execute('/pe "Please help me write better error handling"')

        assert result is not None
        assert result["prompt"] == "Please help me write better error handling"
        assert result["working_dir"] is not None
        assert result["status"] == "success"
        assert "🔍" in result["acknowledgment"]

    def test_command_with_override_flag(self):
        """AC2: Command with --override flag."""
        result = self.command.execute('/pe --override naming=camelCase "my prompt"')

        assert result["status"] == "success"
        assert result["prompt"] == "my prompt"
        assert result["overrides"]["naming"] == "camelCase"
        assert "🔍 Analyzing your project" in result["acknowledgment"]

    def test_missing_prompt_error(self):
        """AC3: Error handling for missing prompt."""
        result = self.command.execute('/pe')

        assert result["status"] == "error"
        assert "prompt" in result["message"].lower()
        assert "/pe" in result["message"]
        assert result["error_code"] == "MISSING_PROMPT"

    def test_invalid_flag_error(self):
        """AC3: Error handling for invalid flag."""
        result = self.command.execute('/pe --invalid-flag value "prompt"')

        assert result["status"] == "error"
        assert "invalid" in result["message"].lower() or "flag" in result["message"].lower()
        assert result["error_code"] == "INVALID_FLAG"

    def test_working_directory_detection(self):
        """AC1: Working directory is correctly detected."""
        result = self.command.execute('/pe "test"')

        assert result["working_dir"] is not None
        assert result["working_dir"] == os.getcwd()
        assert len(result["working_dir"]) > 0

    def test_error_message_helpfulness(self):
        """AC3: Error messages are helpful and actionable."""
        result = self.command.execute('/pe')

        # Error message should suggest correct syntax
        assert "Usage:" in result["message"] or "/pe" in result["message"]
        assert "prompt" in result["message"].lower()

    def test_acknowledgment_is_non_blocking(self):
        """AC1: Acknowledgment is returned immediately without waiting."""
        result = self.command.execute('/pe "prompt"')

        # Acknowledgment should be present and include progress emoji
        assert "acknowledgment" in result
        assert len(result["acknowledgment"]) > 0
        assert result["acknowledgment"].startswith("🔍")

    def test_no_sensitive_data_in_error(self):
        """Sensitive data should not appear in error messages."""
        result = self.command.execute('/pe invalid syntax here')

        # Should have helpful error, not raw exception
        assert "Traceback" not in result["message"]
        assert "Exception" not in result["message"]

    def test_multiple_override_flags(self):
        """Parse multiple --override flags."""
        result = self.command.execute(
            '/pe --override naming=camelCase --override style=compact "prompt"'
        )

        assert result["status"] == "success"
        assert result["overrides"]["naming"] == "camelCase"
        assert result["overrides"]["style"] == "compact"

    def test_empty_prompt_error(self):
        """AC3: Error for empty quoted prompt."""
        result = self.command.execute('/pe ""')

        assert result["status"] == "error"
        assert "empty" in result["message"].lower() or "prompt" in result["message"].lower()
        assert result["error_code"] == "EMPTY_PROMPT"

    def test_unclosed_quote_error(self):
        """Error for unclosed quotes."""
        result = self.command.execute('/pe "this quote is never closed')

        assert result["status"] == "error"
        assert "quote" in result["message"].lower() or "closed" in result["message"].lower()
        assert result["error_code"] == "PARSE_ERROR"

    def test_result_structure(self):
        """Verify result has expected structure."""
        result = self.command.execute('/pe "test"')

        assert isinstance(result, dict)
        assert "status" in result
        assert "prompt" in result
        assert "working_dir" in result
        assert "acknowledgment" in result

    def test_error_result_structure(self):
        """Verify error result has expected structure."""
        result = self.command.execute('/pe')

        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        assert "error_code" in result
        assert result["status"] == "error"

    def test_command_response_time(self):
        """Command parsing should complete in <100ms."""
        import time

        start = time.time()
        result = self.command.execute('/pe "quick test"')
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"Command took {elapsed}ms, expected <100ms"
        assert result["status"] == "success"

    def test_special_characters_in_prompt(self):
        """Handle special characters in prompt."""
        result = self.command.execute('/pe "Code with !@#$% special chars"')

        assert result["status"] == "success"
        assert "!@#$%" in result["prompt"]

    def test_multiline_prompt(self):
        """Handle multiline prompts with escaped newlines."""
        result = self.command.execute('/pe "Line 1\\nLine 2\\nLine 3"')

        assert result["status"] == "success"
        assert "Line 1" in result["prompt"]
        assert "Line 2" in result["prompt"]

    def test_prompt_with_internal_quotes(self):
        """Handle prompts with escaped quotes inside."""
        result = self.command.execute('/pe "He said \\"Hello\\" to me"')

        assert result["status"] == "success"
        assert 'He said "Hello" to me' == result["prompt"]

    def test_very_long_prompt(self):
        """Handle very long prompt text."""
        long_text = "a" * 5000
        result = self.command.execute(f'/pe "{long_text}"')

        assert result["status"] == "success"
        assert result["prompt"] == long_text

    def test_invalid_override_value(self):
        """Error on invalid override value."""
        result = self.command.execute('/pe --override naming=invalid_value "prompt"')

        assert result["status"] == "error"
        assert "invalid" in result["message"].lower()
        assert result["error_code"] == "INVALID_OVERRIDE"

    def test_malformed_override_flag(self):
        """Error on malformed --override flag."""
        result = self.command.execute('/pe --override missing_equals "prompt"')

        assert result["status"] == "error"
        assert "override" in result["message"].lower() or "=" in result["message"]
        assert result["error_code"] in ["PARSE_ERROR", "INVALID_OVERRIDE"]

    def test_invalid_command_prefix(self):
        """Error on invalid command prefix."""
        result = self.command.execute('/enhance "test"')

        assert result["status"] == "error"
        assert "/pe" in result["message"]

    def test_flag_without_value_error(self):
        """Error when flag lacks value."""
        result = self.command.execute('/pe --override')

        assert result["status"] == "error"
        assert "flag" in result["message"].lower() or "value" in result["message"].lower()
        # Error could be classified as PARSE_ERROR or INVALID_OVERRIDE depending on detection
        assert result["error_code"] in ["PARSE_ERROR", "INVALID_OVERRIDE"]

    def test_multiple_prompts_error(self):
        """Error when multiple prompts provided."""
        result = self.command.execute('/pe "first" "second"')

        assert result["status"] == "error"
        assert "multiple" in result["message"].lower() or "prompt" in result["message"].lower()
        assert result["error_code"] == "PARSE_ERROR"

    def test_command_response_has_no_traceback(self):
        """Error responses should not include Python tracebacks."""
        result = self.command.execute('/pe')

        assert "Traceback" not in str(result["message"])
        assert "File \"" not in str(result["message"])  # Python traceback style

    def test_acknowledgment_format(self):
        """Acknowledgment should have specific format."""
        result = self.command.execute('/pe "test prompt"')

        ack = result["acknowledgment"]
        assert ack.startswith("🔍")
        assert "Analyzing" in ack
        assert "test prompt" in ack
