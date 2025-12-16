"""
Output formatter for result display.
Handles result formatting, terminal output, and Display-Only mode.
"""

import logging
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class FormattingError(Exception):
    """Exception raised during output formatting."""
    pass


class OutputFormatter:
    """Formats and displays enhancement results."""

    # Format constants
    TERMINAL_WIDTH = 80
    SEPARATOR_CHARS = "="
    SECTION_SPACING = "\n"

    # Phase emoji markers
    PHASE_EMOJI = {
        "original": "📝",
        "enhanced": "✨",
        "steps": "🔧",
        "standards": "🎯",
    }

    # Phase descriptions
    PHASE_DESCRIPTIONS = {
        "original": "Original Prompt",
        "enhanced": "Enhanced Prompt",
        "steps": "Implementation Steps",
        "standards": "Detected Coding Standards",
    }

    def __init__(self, display_only_mode: bool = True, terminal_width: int = 80):
        """
        Initialize the output formatter.

        Args:
            display_only_mode: If True, enforces Display-Only mode (no execution)
            terminal_width: Terminal width for text wrapping (default 80)
        """
        self.display_only_mode = display_only_mode
        self.terminal_width = terminal_width

        logger.debug(f"OutputFormatter initialized: display_only_mode={display_only_mode}, terminal_width={terminal_width}")

    def is_display_only_mode(self) -> bool:
        """Check if Display-Only mode is active."""
        return self.display_only_mode

    def verify_mode_allows_execution(self) -> None:
        """
        Verify that execution is allowed in current mode.

        Raises:
            FormattingError: If Display-Only mode prevents execution
        """
        if self.display_only_mode:
            raise FormattingError(
                "Cannot execute result in Display-Only mode. "
                "Review the formatted result and manually decide how to proceed. "
                "Copy the enhanced prompt and use it in a new request if desired."
            )

    def get_mode_indicator(self) -> str:
        """
        Get Display-Only mode indication message.

        Returns:
            Mode indicator string
        """
        if self.display_only_mode:
            return "🔐 Display-Only Mode - Review before deciding to use"
        else:
            return "⚡ Normal Mode"

    def wrap_text(self, text: str, width: Optional[int] = None, preserve_indentation: bool = False) -> str:
        """
        Wrap text to terminal width while preserving word boundaries.

        Args:
            text: Text to wrap
            width: Target width (default to terminal_width)
            preserve_indentation: If True, preserve indentation

        Returns:
            Wrapped text
        """
        if width is None:
            width = self.terminal_width

        if not text:
            return ""

        # Handle code blocks with indentation preservation
        if preserve_indentation:
            lines = text.split("\n")
            wrapped_lines = []

            for line in lines:
                # Preserve indentation
                leading_spaces = len(line) - len(line.lstrip())
                indent = " " * leading_spaces

                # Wrap the line content
                if len(line) <= width:
                    wrapped_lines.append(line)
                else:
                    # Get the content without indentation
                    content = line.lstrip()

                    # Wrap the content
                    wrapped_content = textwrap.fill(
                        content,
                        width=width - leading_spaces,
                        break_long_words=True,
                        break_on_hyphens=False
                    )

                    # Re-add indentation to wrapped lines
                    for wrapped_line in wrapped_content.split("\n"):
                        wrapped_lines.append(indent + wrapped_line)

            return "\n".join(wrapped_lines)
        else:
            # Handle paragraphs (preserve multiple newlines)
            paragraphs = text.split("\n\n")
            wrapped_paragraphs = []

            for paragraph in paragraphs:
                # Wrap each paragraph
                wrapped = textwrap.fill(
                    paragraph,
                    width=width,
                    break_long_words=True,
                    break_on_hyphens=False
                )
                wrapped_paragraphs.append(wrapped)

            return "\n\n".join(wrapped_paragraphs)

    def _format_section(self, emoji: str, header: str, content: str) -> str:
        """
        Format a section with emoji, header, and content.

        Args:
            emoji: Emoji for the section
            header: Section header text
            content: Section content

        Returns:
            Formatted section
        """
        separator = self.SEPARATOR_CHARS * self.terminal_width
        lines = [
            separator,
            f"{emoji} {header}",
            separator,
            content,
        ]
        return "\n".join(lines)

    def format_original_prompt(self, prompt_text: str) -> str:
        """
        Format original prompt section (AC1).

        Args:
            prompt_text: The original prompt text

        Returns:
            Formatted section
        """
        emoji = self.PHASE_EMOJI["original"]
        header = self.PHASE_DESCRIPTIONS["original"]

        # Wrap the prompt text
        wrapped_content = self.wrap_text(prompt_text, self.terminal_width)

        return self._format_section(emoji, header, wrapped_content)

    def format_enhanced_prompt(self, enhanced_text: str) -> str:
        """
        Format enhanced prompt section (AC1).

        Args:
            enhanced_text: The enhanced prompt text

        Returns:
            Formatted section
        """
        emoji = self.PHASE_EMOJI["enhanced"]
        header = self.PHASE_DESCRIPTIONS["enhanced"]

        # Wrap the enhanced text
        wrapped_content = self.wrap_text(enhanced_text, self.terminal_width)

        return self._format_section(emoji, header, wrapped_content)

    def format_implementation_steps(self, steps: List[str]) -> str:
        """
        Format implementation steps section as numbered list (AC1).

        Args:
            steps: List of implementation steps

        Returns:
            Formatted section
        """
        emoji = self.PHASE_EMOJI["steps"]
        header = self.PHASE_DESCRIPTIONS["steps"]

        # Format steps as numbered list
        if not steps:
            content = "(No steps provided)"
        else:
            step_lines = []
            for i, step in enumerate(steps, 1):
                step_lines.append(f"{i}. {step}")
            content = "\n".join(step_lines)

        return self._format_section(emoji, header, content)

    def format_standards_section(self, standards: Optional[Dict[str, Any]]) -> str:
        """
        Format detected standards section (AC5).

        Args:
            standards: Dictionary of detected standards

        Returns:
            Formatted section
        """
        emoji = self.PHASE_EMOJI["standards"]
        header = self.PHASE_DESCRIPTIONS["standards"]

        if not standards:
            content = "(No standards detected)"
        else:
            # Format each standard with confidence and evidence
            standard_lines = []

            for standard_name, standard_data in standards.items():
                value = standard_data.get("value", "unknown")
                confidence = standard_data.get("confidence", 0)
                evidence = standard_data.get("evidence", "")

                # Format: name: value (confidence%)
                confidence_pct = int(confidence * 100) if isinstance(confidence, float) else confidence
                line = f"✓ {standard_name}: {value} ({confidence_pct}% confidence)"

                standard_lines.append(line)

                # Add evidence if available
                if evidence:
                    evidence_line = f"   Evidence: {evidence}"
                    standard_lines.append(evidence_line)

            content = "\n".join(standard_lines)

        return self._format_section(emoji, header, content)

    def format_complete_result(
        self,
        original_prompt: str,
        enhanced_prompt: str,
        implementation_steps: List[str],
        detected_standards: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format complete result with all sections (AC1-AC5).

        Args:
            original_prompt: Original prompt text
            enhanced_prompt: Enhanced prompt text
            implementation_steps: List of implementation steps
            detected_standards: Detected standards data

        Returns:
            Complete formatted result
        """
        # Mode indicator
        mode_indicator = self.get_mode_indicator()

        # Format each section
        original_section = self.format_original_prompt(original_prompt)
        enhanced_section = self.format_enhanced_prompt(enhanced_prompt)
        steps_section = self.format_implementation_steps(implementation_steps)
        standards_section = self.format_standards_section(detected_standards) if detected_standards else ""

        # Combine all sections
        sections = [
            mode_indicator,
            "",
            original_section,
            "",
            enhanced_section,
            "",
            steps_section,
        ]

        # Add standards section if available
        if standards_section:
            sections.append("")
            sections.append(standards_section)

        result = "\n".join(sections)

        logger.info(f"Complete result formatted (display_only_mode={self.display_only_mode})")

        return result
