"""
Standards display formatter - presents detected standards with confidence scores.

Formats and displays coding standards detection results with confidence scores,
evidence examples, and exception information for user review and customization.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EvidenceExample:
    """Single evidence example for a detected standard."""

    file_path: str
    example: str
    count: int = 1


@dataclass
class StandardsInfo:
    """Information about a detected standard."""

    name: str
    value: str
    confidence: float  # 0-100
    sample_size: int
    evidence: List[EvidenceExample]
    exceptions: Optional[str] = None
    secondary_value: Optional[str] = None
    secondary_confidence: Optional[float] = None


class StandardsDisplay:
    """Formats and displays detected standards with confidence information."""

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 85
    MEDIUM_CONFIDENCE_THRESHOLD = 60

    def __init__(self):
        """Initialize standards display formatter."""
        logger.debug("Initialized StandardsDisplay")

    @staticmethod
    def get_confidence_level(confidence: float) -> Tuple[str, str]:
        """
        Determine confidence level and emoji.

        Args:
            confidence: Confidence percentage (0-100)

        Returns:
            Tuple of (level_name, emoji)
        """
        if confidence >= StandardsDisplay.HIGH_CONFIDENCE_THRESHOLD:
            return ("High confidence", "✓")
        elif confidence >= StandardsDisplay.MEDIUM_CONFIDENCE_THRESHOLD:
            return ("Medium confidence", "▪")
        else:
            return ("Low confidence", "⚠")

    @staticmethod
    def format_standard(
        standard_info: StandardsInfo,
    ) -> str:
        """
        Format a single standard for display.

        Args:
            standard_info: Standard information to format

        Returns:
            Formatted string representation
        """
        level_name, indicator = StandardsDisplay.get_confidence_level(
            standard_info.confidence
        )

        # Build main line
        lines = [
            f"{indicator} {standard_info.name}: {standard_info.value}",
            f"  Confidence: {standard_info.confidence:.0f}% ({level_name})",
            f"  Sample size: {standard_info.sample_size} files analyzed",
        ]

        # Add secondary convention if present
        if standard_info.secondary_value and standard_info.secondary_confidence:
            lines.append(
                f"  Secondary: {standard_info.secondary_value} "
                f"({standard_info.secondary_confidence:.0f}%)"
            )

        # Add evidence examples
        if standard_info.evidence:
            lines.append("  Evidence:")
            for example in standard_info.evidence[:3]:  # Limit to 3 examples
                lines.append(f"    • {example.file_path}: {example.example}")
                if example.count > 1:
                    lines.append(f"      (found {example.count} times)")

        # Add exceptions if present
        if standard_info.exceptions:
            lines.append(f"  Exceptions: {standard_info.exceptions}")

        # Add guidance for low-confidence standards
        if standard_info.confidence < StandardsDisplay.MEDIUM_CONFIDENCE_THRESHOLD:
            lines.append("  💡 Tip: Use --override to correct if needed")

        return "\n".join(lines)

    @staticmethod
    def format_standards_report(
        standards: Dict[str, StandardsInfo],
        show_detailed: bool = True,
    ) -> str:
        """
        Format complete standards report for display.

        Args:
            standards: Dictionary of standard name -> StandardsInfo
            show_detailed: Whether to show detailed evidence

        Returns:
            Formatted standards report
        """
        lines = [
            "📋 Detected Coding Standards",
            "═" * 50,
            "",
        ]

        for standard_name, standard_info in standards.items():
            if show_detailed:
                lines.append(StandardsDisplay.format_standard(standard_info))
            else:
                # Condensed format
                level_name, indicator = StandardsDisplay.get_confidence_level(
                    standard_info.confidence
                )
                lines.append(
                    f"{indicator} {standard_info.name}: "
                    f"{standard_info.value} ({standard_info.confidence:.0f}%)"
                )
            lines.append("")

        # Add footer with guidance
        lines.extend(
            [
                "═" * 50,
                "",
                "💡 How to customize:",
                "  • Use --override to temporarily change standards",
                "  • Create .pe.yaml for project-wide settings",
                "  • Use --template [name] for preset configurations",
                "",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def format_confidence_summary(
        standards: Dict[str, StandardsInfo],
    ) -> str:
        """
        Format brief confidence summary.

        Args:
            standards: Dictionary of detected standards

        Returns:
            Brief summary string
        """
        high_count = sum(
            1
            for s in standards.values()
            if s.confidence >= StandardsDisplay.HIGH_CONFIDENCE_THRESHOLD
        )
        medium_count = sum(
            1
            for s in standards.values()
            if StandardsDisplay.MEDIUM_CONFIDENCE_THRESHOLD
            <= s.confidence
            < StandardsDisplay.HIGH_CONFIDENCE_THRESHOLD
        )
        low_count = sum(
            1
            for s in standards.values()
            if s.confidence < StandardsDisplay.MEDIUM_CONFIDENCE_THRESHOLD
        )

        total = len(standards)
        lines = [
            f"Standards Detection Summary: {high_count}/{total} high confidence",
        ]

        if medium_count > 0:
            lines.append(f"  • {medium_count} medium confidence standards")
        if low_count > 0:
            lines.append(
                f"  ⚠ {low_count} low confidence standards (verify recommended)"
            )

        return "\n".join(lines)

    @staticmethod
    def format_confidence_warning(
        standards: Dict[str, StandardsInfo],
    ) -> Optional[str]:
        """
        Format warning if low-confidence standards detected.

        Args:
            standards: Dictionary of detected standards

        Returns:
            Warning message or None if all confident
        """
        low_confidence = [
            s
            for s in standards.values()
            if s.confidence < StandardsDisplay.MEDIUM_CONFIDENCE_THRESHOLD
        ]

        if not low_confidence:
            return None

        lines = [
            "⚠️ Low Confidence Standards Detected",
            "",
            "The following standards have low confidence:",
        ]

        for standard in low_confidence:
            lines.append(f"  • {standard.name}: {standard.confidence:.0f}%")

        lines.extend(
            [
                "",
                "Recommendations:",
                "  1. Review detected standards above",
                "  2. Use --override to correct any errors",
                "  3. Or create .pe.yaml for project-wide config",
                "",
            ]
        )

        return "\n".join(lines)
