"""
Unit tests for ParameterParser.
Tests parameter parsing for `/pe` command with flags and options.
"""

import pytest
from src.prompt_enhancement.cli.parser import ParameterParser, ParseError


class TestParameterParser:
    """Test suite for ParameterParser class."""

    def test_parse_basic_prompt(self):
        """AC1: Parse basic prompt text in quotes."""
        parser = ParameterParser()
        result = parser.parse('/pe "Please help me write better error handling"')

        assert result.prompt == "Please help me write better error handling"
        assert result.working_dir is not None
        assert result.overrides == {}
        assert result.is_valid is True

    def test_parse_quoted_prompt_with_spaces(self):
        """Parse prompt with multiple spaces."""
        parser = ParameterParser()
        result = parser.parse('/pe "Hello world with   multiple spaces"')

        assert result.prompt == "Hello world with   multiple spaces"

    def test_parse_prompt_with_special_chars(self):
        """Parse prompt containing special characters."""
        parser = ParameterParser()
        result = parser.parse('/pe "Write code with !@#$% special chars"')

        assert result.prompt == "Write code with !@#$% special chars"

    def test_parse_prompt_with_escaped_quotes(self):
        """Parse prompt with escaped quotes inside."""
        parser = ParameterParser()
        result = parser.parse('/pe "He said \\"Hello\\" to me"')

        assert result.prompt == 'He said "Hello" to me'

    def test_parse_prompt_with_newlines(self):
        """Parse prompt with newline characters."""
        parser = ParameterParser()
        result = parser.parse('/pe "Line 1\\nLine 2\\nLine 3"')

        assert "Line 1" in result.prompt
        assert "Line 2" in result.prompt
        assert "Line 3" in result.prompt

    def test_parse_with_override_flag_before_prompt(self):
        """AC2: Parse with --override flag before prompt."""
        parser = ParameterParser()
        result = parser.parse('/pe --override naming=camelCase "my prompt"')

        assert result.prompt == "my prompt"
        assert result.overrides.get("naming") == "camelCase"
        assert result.is_valid is True

    def test_parse_with_override_flag_after_prompt(self):
        """Parse with --override flag after prompt."""
        parser = ParameterParser()
        result = parser.parse('/pe "my prompt" --override naming=snake_case')

        assert result.prompt == "my prompt"
        assert result.overrides.get("naming") == "snake_case"

    def test_parse_with_multiple_override_flags(self):
        """Parse with multiple --override flags."""
        parser = ParameterParser()
        result = parser.parse('/pe --override naming=camelCase --override style=compact "prompt"')

        assert result.prompt == "prompt"
        assert result.overrides.get("naming") == "camelCase"
        assert result.overrides.get("style") == "compact"

    def test_parse_with_invalid_override_value(self):
        """Parse with invalid override value."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override naming=invalid_value "prompt"')

        assert "invalid_value" in str(exc_info.value).lower()
        assert "valid values" in str(exc_info.value).lower()

    def test_parse_with_template_flag(self):
        """Parse with --template flag."""
        parser = ParameterParser()
        result = parser.parse('/pe --template refactor "my prompt"')

        assert result.prompt == "my prompt"
        assert result.overrides.get("template") == "refactor"

    def test_parse_with_type_flag(self):
        """Parse with --type flag."""
        parser = ParameterParser()
        result = parser.parse('/pe --type enhancement "my prompt"')

        assert result.prompt == "my prompt"
        assert result.overrides.get("type") == "enhancement"

    def test_missing_quotes_error(self):
        """AC3: Error when prompt is missing quotes."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe without quotes')

        error_msg = str(exc_info.value).lower()
        assert "quote" in error_msg
        assert "/pe" in str(exc_info.value)

    def test_missing_prompt_error(self):
        """AC3: Error when prompt is completely missing."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe')

        error_msg = str(exc_info.value).lower()
        assert "prompt" in error_msg or "required" in error_msg

    def test_missing_prompt_with_flags_error(self):
        """AC3: Error when prompt is missing but flags present."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override naming=camelCase')

        error_msg = str(exc_info.value).lower()
        assert "prompt" in error_msg

    def test_empty_prompt_error(self):
        """AC3: Error when prompt is empty string."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe ""')

        error_msg = str(exc_info.value).lower()
        assert "empty" in error_msg or "prompt" in error_msg

    def test_invalid_flag_error(self):
        """AC3: Error on invalid flag name."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --invalid-flag value "prompt"')

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "flag" in error_msg

    def test_malformed_override_flag(self):
        """AC2: Error on malformed --override flag (missing =)."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override naming "prompt"')

        error_msg = str(exc_info.value).lower()
        assert "=" in str(exc_info.value) or "format" in error_msg

    def test_unclosed_quote_error(self):
        """Error on unclosed quote."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe "this quote is never closed')

        error_msg = str(exc_info.value).lower()
        assert "quote" in error_msg or "closed" in error_msg

    def test_parse_result_structure(self):
        """Verify ParseResult has expected attributes."""
        parser = ParameterParser()
        result = parser.parse('/pe "test prompt"')

        assert hasattr(result, 'prompt')
        assert hasattr(result, 'working_dir')
        assert hasattr(result, 'overrides')
        assert hasattr(result, 'is_valid')
        assert isinstance(result.overrides, dict)
        assert isinstance(result.is_valid, bool)

    def test_parse_long_prompt(self):
        """Parse very long prompt text."""
        long_text = "a" * 5000
        parser = ParameterParser()
        result = parser.parse(f'/pe "{long_text}"')

        assert result.prompt == long_text

    def test_flag_case_insensitivity(self):
        """Parse flag names (case sensitive actually - should be lowercase)."""
        parser = ParameterParser()

        # Flags should be lowercase
        with pytest.raises(ParseError):
            parser.parse('/pe --Override naming=camelCase "prompt"')

    def test_parse_multiple_word_command(self):
        """Verify /pe command prefix is required."""
        parser = ParameterParser()
        result = parser.parse('/pe "prompt"')

        assert result.is_valid is True

    def test_working_directory_detection(self):
        """AC1: Working directory is populated in result."""
        parser = ParameterParser()
        result = parser.parse('/pe "test"')

        # Working directory should be set
        assert result.working_dir is not None
        assert len(result.working_dir) > 0

    def test_parse_with_equals_in_override_value(self):
        """Parse override value that contains equals sign - should fail with invalid value."""
        parser = ParameterParser()

        # This should fail because "key=value" is not a valid override value for "style"
        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override style=key=value "prompt"')

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "valid values" in error_msg

    def test_invalid_command_prefix(self):
        """Error if command doesn't start with /pe."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/enhance "prompt"')

        error_msg = str(exc_info.value).lower()
        assert "/pe" in str(exc_info.value)

    def test_flag_without_value(self):
        """Error when flag lacks a value."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override')

        error_msg = str(exc_info.value).lower()
        assert "require" in error_msg or "value" in error_msg

    def test_multiple_prompts(self):
        """Error when multiple quoted prompts are provided."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe "first" "second"')

        error_msg = str(exc_info.value).lower()
        assert "multiple" in error_msg or "prompt" in error_msg

    def test_unquoted_flag_name(self):
        """Error when unquoted text appears where prompt expected."""
        parser = ParameterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('/pe --override naming=camelCase unquoted_text')

        error_msg = str(exc_info.value).lower()
        assert "quote" in error_msg

    def test_prompt_exceeds_max_length(self):
        """Error when prompt exceeds MAX_PROMPT_LENGTH."""
        parser = ParameterParser()

        # Create a prompt longer than 10,000 chars
        long_prompt = "a" * 10001

        with pytest.raises(ParseError) as exc_info:
            parser.parse(f'/pe "{long_prompt}"')

        error_msg = str(exc_info.value).lower()
        assert "too long" in error_msg or "maximum" in error_msg

    def test_escaped_backslash_and_quote(self):
        """Test that \\" is correctly parsed as escaped backslash and quote."""
        parser = ParameterParser()

        # Input: /pe "He said \\"Hello\\""
        # Expected: He said \"Hello\"
        result = parser.parse('/pe "He said \\\\\\"Hello\\\\\\""')

        # Should have both backslashes and quotes
        assert "\\" in result.prompt
        assert '"' in result.prompt
        assert 'He said' in result.prompt

    def test_unquote_string_not_quoted_error(self):
        """Test _unquote_string raises error for non-quoted strings."""
        parser = ParameterParser()
        with pytest.raises(ParseError) as exc_info:
            parser._unquote_string('not quoted string')
        assert "quoted" in str(exc_info.value).lower()

    def test_tokenize_with_unquoted_text(self):
        """Test _tokenize properly handles unquoted text."""
        parser = ParameterParser()
        tokens = parser._tokenize('--override naming=camelCase "prompt text"')
        # Should have flag, flag value, and quoted prompt
        assert len(tokens) == 3
        assert tokens[0] == '--override'
        assert tokens[1] == 'naming=camelCase'
        assert tokens[2] == '"prompt text"'

    def test_validate_override_with_invalid_key(self):
        """Test _validate_override rejects invalid override keys."""
        parser = ParameterParser()
        with pytest.raises(ParseError) as exc_info:
            parser._validate_override('invalid_key', 'value')
        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "key" in error_msg

    def test_validate_override_with_invalid_value(self):
        """Test _validate_override rejects invalid values for keys."""
        parser = ParameterParser()
        with pytest.raises(ParseError) as exc_info:
            parser._validate_override('naming', 'invalid_style')
        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "value" in error_msg

    def test_find_closing_quote_not_escaped(self):
        """Test _find_closing_quote correctly identifies unescaped quotes."""
        parser = ParameterParser()
        # String with escaped quote then unescaped quote
        s = 'some text \\" and then " ending'
        # Start from position after first quote
        result = parser._find_closing_quote(s, 12)
        # Should find the unescaped quote
        assert s[result] == '"'
        assert 'and then' in s[:result]
