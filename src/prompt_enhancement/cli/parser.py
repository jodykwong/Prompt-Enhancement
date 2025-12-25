"""
Parameter parser for `/pe` command.
Handles parsing of prompt text, flags, and overrides.
"""

import os
import re
import shlex
from dataclasses import dataclass
from typing import Dict, Optional, Any


class ParseError(Exception):
    """Exception raised when parameter parsing fails."""
    pass


@dataclass
class ParseResult:
    """Result of successful parameter parsing."""
    prompt: str
    working_dir: str
    overrides: Dict[str, str]
    is_valid: bool = True


# Valid override options
VALID_OVERRIDE_OPTIONS = {
    "naming": ["camelCase", "snake_case", "PascalCase", "kebab-case"],
    "style": ["compact", "detailed", "minimal"],
    "template": ["refactor", "optimize", "test", "document"],
    "type": ["enhancement", "fix", "feature"],
}

# Valid flags
VALID_FLAGS = {"override", "template", "type"}

# Max prompt length (10,000 characters)
MAX_PROMPT_LENGTH = 10000


class ParameterParser:
    """Parser for `/pe` command parameters."""

    def __init__(self):
        """Initialize the parameter parser."""
        self.valid_override_options = VALID_OVERRIDE_OPTIONS
        self.valid_flags = VALID_FLAGS

    def parse(self, command_string: str) -> ParseResult:
        """
        Parse a `/pe` command string.

        Args:
            command_string: The full command string, e.g., '/pe "prompt" --override naming=camelCase'

        Returns:
            ParseResult containing parsed prompt, working directory, and overrides

        Raises:
            ParseError: If parsing fails (missing quotes, invalid flags, etc.)
        """
        # Strip command prefix
        if not command_string.startswith("/pe"):
            raise ParseError("Command must start with /pe")

        remaining = command_string[3:].strip()

        # Extract all tokens
        tokens = self._tokenize(remaining)

        # Separate flags and prompt
        flags = {}
        prompt_token = None

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.startswith("--"):
                # This is a flag
                flag_name = token[2:]
                if flag_name not in self.valid_flags:
                    raise ParseError(
                        f"Invalid flag '--{flag_name}'. Valid flags are: {', '.join(f'--{f}' for f in self.valid_flags)}"
                    )

                # Get flag value
                if i + 1 >= len(tokens):
                    raise ParseError(f"Flag '--{flag_name}' requires a value")

                i += 1
                flag_value = tokens[i]

                # Handle special case for --override flag with key=value
                if flag_name == "override":
                    if "=" not in flag_value:
                        raise ParseError(f"Override flag must be in format --override key=value")
                    key, value = flag_value.split("=", 1)
                    self._validate_override(key, value)
                    flags[key] = value
                else:
                    flags[flag_name] = flag_value

                i += 1
            else:
                # This could be the prompt or an unquoted token
                # Check if it's quoted
                if token.startswith('"') and token.endswith('"'):
                    # Properly quoted prompt
                    if prompt_token is not None:
                        raise ParseError("Multiple prompts detected. Only one prompt allowed.")
                    prompt_token = token
                else:
                    # Unquoted text - this is an error
                    raise ParseError(f'Prompt must be quoted. Did you forget quotes? Try: /pe "{token}"')
                i += 1

        # Validate required prompt
        if prompt_token is None:
            raise ParseError('Missing required prompt. Usage: /pe "your prompt here"')

        # Unquote and validate prompt
        prompt = self._unquote_string(prompt_token)
        if not prompt or prompt.strip() == "":
            raise ParseError('Prompt cannot be empty. Usage: /pe "your prompt here"')

        # Validate prompt length
        if len(prompt) > MAX_PROMPT_LENGTH:
            raise ParseError(
                f'Prompt too long ({len(prompt)} chars). '
                f'Maximum {MAX_PROMPT_LENGTH} characters allowed.'
            )

        # Get working directory with error handling
        try:
            working_dir = os.getcwd()
        except (OSError, FileNotFoundError) as e:
            raise ParseError(
                f"Unable to determine working directory: {e}. "
                "Please ensure you're running this from a valid directory."
            )

        return ParseResult(
            prompt=prompt,
            working_dir=working_dir,
            overrides=flags,
            is_valid=True
        )

    def _tokenize(self, remaining: str) -> list:
        """
        Tokenize the command string, respecting quoted strings.

        Args:
            remaining: The string after removing the /pe prefix

        Returns:
            List of tokens
        """
        tokens = []
        i = 0
        current_token = ""

        while i < len(remaining):
            char = remaining[i]

            if char == '"':
                # Start of quoted string
                if current_token:
                    # If we have accumulated text without a quote, it's unquoted
                    tokens.append(current_token)
                    current_token = ""

                quote_end = self._find_closing_quote(remaining, i + 1)
                if quote_end == -1:
                    raise ParseError("Unclosed quote in command")
                tokens.append(remaining[i:quote_end + 1])
                i = quote_end + 1
            elif char == " ":
                # Whitespace separator
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                i += 1
            else:
                # Regular character
                current_token += char
                i += 1

        if current_token:
            tokens.append(current_token)

        return tokens

    def _find_closing_quote(self, s: str, start: int) -> int:
        """
        Find the closing quote position.

        Args:
            s: String to search in
            start: Position to start searching from

        Returns:
            Index of closing quote, or -1 if not found
        """
        i = start
        while i < len(s):
            if s[i] == '"':
                # Check if it's escaped
                if i > 0 and s[i - 1] == "\\":
                    i += 1
                    continue
                return i
            i += 1
        return -1

    def _unquote_string(self, quoted_str: str) -> str:
        """
        Remove quotes and unescape content.

        Args:
            quoted_str: String with quotes (e.g., '"hello"')

        Returns:
            Unquoted and unescaped string
        """
        if not (quoted_str.startswith('"') and quoted_str.endswith('"')):
            raise ParseError(f"Prompt must be quoted. Got: {quoted_str}")

        # Remove outer quotes
        content = quoted_str[1:-1]

        # Unescape sequences in correct order: \\\\ must be handled first
        # Use a temporary placeholder to avoid double-processing
        content = content.replace('\\\\', '\x00')  # Temp placeholder for backslash
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\x00', '\\')  # Restore backslash

        return content

    def _validate_override(self, key: str, value: str) -> None:
        """
        Validate override key and value.

        Args:
            key: Override key
            value: Override value

        Raises:
            ParseError: If override is invalid
        """
        if key not in self.valid_override_options:
            valid_keys = ", ".join(self.valid_override_options.keys())
            raise ParseError(f"Invalid override key '{key}'. Valid keys are: {valid_keys}")

        valid_values = self.valid_override_options[key]
        if value not in valid_values:
            raise ParseError(
                f"Invalid value '{value}' for override '{key}'. "
                f"Valid values are: {', '.join(valid_values)}"
            )
