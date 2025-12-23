"""User confirmation system for degradation decisions."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .degradation import DegradationLevel, DegradationInfo

logger = logging.getLogger(__name__)


class UserDecision(Enum):
    """User's decision when prompted about degradation."""

    CONTINUE = "continue"
    STOP = "stop"
    TROUBLESHOOT = "troubleshoot"
    RETRY = "retry"


@dataclass
class DiagnosticInfo:
    """Diagnostic information for troubleshooting."""

    attempted_detections: List[str]
    failure_reasons: dict
    fix_suggestions: List[str]
    checked_files: List[str]
    missing_files: List[str]


class DegradationConfirmation:
    """Handles user confirmation for degradation decisions."""

    @staticmethod
    def format_confirmation_prompt(
        degradation_info: DegradationInfo,
        interactive: bool = True,
    ) -> str:
        """
        Format degradation confirmation prompt.

        Args:
            degradation_info: The degradation decision info
            interactive: Whether to include interactive options

        Returns:
            Formatted prompt string
        """
        prompt_lines = [
            "⚠️ Quality Will Degrade",
            "",
            f"System could not complete full enhancement.",
            f"Suggested degradation level: {DegradationConfirmation._level_name(degradation_info.level)}",
            "",
        ]

        if degradation_info.reason:
            prompt_lines.append(f"Reason: {degradation_info.reason}")
            prompt_lines.append("")

        if degradation_info.missing_components:
            prompt_lines.append("Missing:")
            for component in degradation_info.missing_components:
                prompt_lines.append(f"  ✗ {component}")
            prompt_lines.append("")

        if interactive:
            prompt_lines.extend([
                "Would you like to:",
                "[Y] Continue (Accept degraded quality)",
                "[N] Stop (Cancel enhancement)",
                "[T] Troubleshoot (View diagnostic info)",
                "",
            ])

        return "\n".join(prompt_lines)

    @staticmethod
    def format_diagnostic_prompt(diagnostic: DiagnosticInfo) -> str:
        """
        Format diagnostic information prompt.

        Args:
            diagnostic: The diagnostic information

        Returns:
            Formatted diagnostic prompt
        """
        lines = [
            "📊 Diagnostic Information",
            "",
            "Detection Attempted:",
        ]

        for detection in diagnostic.attempted_detections:
            lines.append(f"├─ {detection}")

        if diagnostic.failure_reasons:
            lines.append("")
            lines.append("Failure Reasons:")
            for reason, detail in diagnostic.failure_reasons.items():
                lines.append(f"├─ {reason}: {detail}")

        if diagnostic.fix_suggestions:
            lines.append("")
            lines.append("Potential Fixes:")
            for i, suggestion in enumerate(diagnostic.fix_suggestions, 1):
                lines.append(f"{i}. {suggestion}")

        if diagnostic.checked_files:
            lines.append("")
            lines.append("Files Checked:")
            for file_path in diagnostic.checked_files:
                status = "✓" if file_path not in diagnostic.missing_files else "✗"
                lines.append(f"  {status} {file_path}")

        lines.extend([
            "",
            "Would you like to:",
            "[R] Retry after fixing",
            "[C] Continue anyway (degraded mode)",
            "[N] Cancel",
        ])

        return "\n".join(lines)

    @staticmethod
    def _level_name(level: DegradationLevel) -> str:
        """Get level name from enum."""
        names = {
            DegradationLevel.FULL: "Level 1 (Full Enhancement)",
            DegradationLevel.WITHOUT_STANDARDS: "Level 2 (Enhancement Without Standards)",
            DegradationLevel.GENERIC: "Level 3 (Generic Enhancement)",
        }
        return names.get(level, "Unknown Level")

    @staticmethod
    def format_outcome_message(decision: UserDecision) -> str:
        """
        Format outcome message based on user decision.

        Args:
            decision: The user's decision

        Returns:
            Outcome message
        """
        messages = {
            UserDecision.CONTINUE: "Continuing in degraded mode...",
            UserDecision.STOP: "Enhancement cancelled.",
            UserDecision.TROUBLESHOOT: "Showing diagnostic information...",
            UserDecision.RETRY: "Retrying enhancement...",
        }
        return messages.get(decision, "Processing your request...")


class DiagnosticBuilder:
    """Builder for creating diagnostic information."""

    def __init__(self):
        """Initialize builder."""
        self.attempted_detections = []
        self.failure_reasons = {}
        self.fix_suggestions = []
        self.checked_files = []
        self.missing_files = []

    def add_detection_attempt(self, detection_name: str) -> "DiagnosticBuilder":
        """Add a detection attempt."""
        self.attempted_detections.append(detection_name)
        return self

    def add_failure_reason(self, reason: str, detail: str) -> "DiagnosticBuilder":
        """Add a failure reason."""
        self.failure_reasons[reason] = detail
        return self

    def add_fix_suggestion(self, suggestion: str) -> "DiagnosticBuilder":
        """Add a fix suggestion."""
        self.fix_suggestions.append(suggestion)
        return self

    def add_checked_file(self, file_path: str, exists: bool = True) -> "DiagnosticBuilder":
        """Add a checked file."""
        self.checked_files.append(file_path)
        if not exists:
            self.missing_files.append(file_path)
        return self

    def build(self) -> DiagnosticInfo:
        """Build diagnostic info."""
        return DiagnosticInfo(
            attempted_detections=self.attempted_detections,
            failure_reasons=self.failure_reasons,
            fix_suggestions=self.fix_suggestions,
            checked_files=self.checked_files,
            missing_files=self.missing_files,
        )
