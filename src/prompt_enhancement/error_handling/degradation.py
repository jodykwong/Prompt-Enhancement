"""Graceful degradation system for maintaining value when constraints encountered."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """Quality levels for enhancement degradation."""

    FULL = 1
    WITHOUT_STANDARDS = 2
    GENERIC = 3


@dataclass
class DegradationInfo:
    """Information about a degradation decision."""

    level: DegradationLevel
    missing_components: List[str] = field(default_factory=list)
    reason: str = ""
    recommendation: str = ""
    cached: bool = False


class DegradationStrategy:
    """Determines appropriate degradation level based on detection results."""

    @staticmethod
    def determine_level(
        project_detected: bool = True,
        standards_confidence: float = 1.0,
        api_timeout: bool = False,
        cache_available: bool = False,
        file_access_denied: bool = False,
    ) -> DegradationInfo:
        """
        Determine appropriate degradation level.

        Args:
            project_detected: Whether project type was successfully detected
            standards_confidence: Confidence score for standards detection (0.0-1.0)
            api_timeout: Whether API call timed out
            cache_available: Whether cached standards available
            file_access_denied: Whether file access was restricted

        Returns:
            DegradationInfo with selected level and metadata
        """
        # Check for Level 1 (Full Enhancement)
        if (
            project_detected
            and standards_confidence >= 0.6
            and not api_timeout
            and not file_access_denied
        ):
            return DegradationInfo(
                level=DegradationLevel.FULL,
                reason="All detection successful",
                missing_components=[],
                recommendation="Full enhancement with project context and standards",
            )

        # Check for Level 2 (Enhancement Without Standards)
        missing_components = []
        reasons = []

        if not project_detected:
            missing_components.append("Project context")
            reasons.append("project type not detected")

        if standards_confidence < 0.6:
            missing_components.append("Reliable standards")
            reasons.append(f"low confidence ({standards_confidence:.0%})")

        if file_access_denied:
            missing_components.append("Complete file access")
            reasons.append("file access restricted")

        # API timeout can use cache if available
        if api_timeout:
            if cache_available:
                return DegradationInfo(
                    level=DegradationLevel.WITHOUT_STANDARDS,
                    missing_components=["Real-time standards"],
                    reason="API timeout, using cached standards",
                    recommendation="Retry operation or check API status",
                    cached=True,
                )
            else:
                # No cache available, must degrade to Level 3
                missing_components.append("Real-time standards")
                reasons.append("API timeout and no cache")

        # If we can still provide some enhancement without standards
        if project_detected and not api_timeout and standards_confidence < 0.6:
            return DegradationInfo(
                level=DegradationLevel.WITHOUT_STANDARDS,
                missing_components=missing_components,
                reason=(
                    " and ".join(reasons) if reasons else "Standards detection failed"
                ),
                recommendation="Use detected standards or create .pe.yaml for better results",
                cached=False,
            )

        # Default to Level 3 (Generic Enhancement)
        if not missing_components:
            missing_components = ["Project context", "Coding standards"]

        return DegradationInfo(
            level=DegradationLevel.GENERIC,
            missing_components=missing_components,
            reason=(
                " and ".join(reasons)
                if reasons
                else "Unable to detect project or standards"
            ),
            recommendation="Ensure you're in project root with identifying files (package.json, requirements.txt, etc.)",
            cached=False,
        )

    @staticmethod
    def get_level_description(level: DegradationLevel) -> str:
        """
        Get human-readable description of a degradation level.

        Args:
            level: The degradation level

        Returns:
            Description string
        """
        descriptions = {
            DegradationLevel.FULL: "Level 1 (Full Enhancement) - Project context + Coding standards",
            DegradationLevel.WITHOUT_STANDARDS: "Level 2 (Enhancement Without Standards) - Project context only",
            DegradationLevel.GENERIC: "Level 3 (Generic Enhancement) - Basic enhancement without project context",
        }
        return descriptions.get(level, "Unknown level")

    @staticmethod
    def get_level_capabilities(level: DegradationLevel) -> dict:
        """
        Get capabilities available at each degradation level.

        Args:
            level: The degradation level

        Returns:
            Dictionary of capabilities
        """
        capabilities = {
            DegradationLevel.FULL: {
                "project_detection": True,
                "standards_detection": True,
                "implementation_steps": True,
                "quality": "High",
            },
            DegradationLevel.WITHOUT_STANDARDS: {
                "project_detection": True,
                "standards_detection": False,
                "implementation_steps": False,
                "quality": "Reduced",
            },
            DegradationLevel.GENERIC: {
                "project_detection": False,
                "standards_detection": False,
                "implementation_steps": False,
                "quality": "Minimum",
            },
        }
        return capabilities.get(level, {})

    @staticmethod
    def format_degradation_info(info: DegradationInfo) -> str:
        """
        Format degradation info for user display.

        Args:
            info: The degradation information

        Returns:
            Formatted string for display
        """
        lines = []

        # Add level
        level_desc = DegradationStrategy.get_level_description(info.level)
        lines.append(f"Degradation Level: {level_desc}")
        lines.append("")

        # Add reason
        if info.reason:
            lines.append(f"Reason: {info.reason}")

        # Add missing components
        if info.missing_components:
            lines.append("Missing:")
            for component in info.missing_components:
                lines.append(f"  ✗ {component}")

        # Add cached note
        if info.cached:
            lines.append("")
            lines.append("Note: Using cached standards from previous analysis")

        # Add recommendation
        if info.recommendation:
            lines.append("")
            lines.append(f"Recommendation: {info.recommendation}")

        return "\n".join(lines)
