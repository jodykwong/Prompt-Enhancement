"""
Implementation step extractor - parses LLM responses to extract structured steps.

Implements AC1: Extract implementation steps from LLM response in various formats.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class StepFormat(Enum):
    """Format of implementation steps detected."""

    NUMBERED = "numbered"  # 1. Step, 2. Step
    BULLETS = "bullets"  # - Step, * Step, • Step
    PROSE = "prose"  # Paragraph format with step markers
    MIXED = "mixed"  # Multiple formats in same response
    UNKNOWN = "unknown"  # Could not detect format


@dataclass
class ImplementationStep:
    """Single implementation step extracted from response."""

    number: int  # Sequential step number
    content: str  # Step content (cleaned)
    original_text: str  # Original text as found in response
    format_detected: StepFormat  # How this step was formatted
    dependencies: List[int] = None  # Step numbers this depends on
    is_actionable: bool = True  # Has verb + object
    complexity: str = "moderate"  # simple, moderate, complex

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class StepGroup:
    """Group of related steps."""

    name: str  # Group name/category
    steps: List[ImplementationStep]  # Steps in this group
    description: str = ""  # Group description


@dataclass
class ExtractedSteps:
    """Result of step extraction (AC1)."""

    steps: List[ImplementationStep]  # All extracted steps
    step_groups: List[StepGroup]  # Grouped steps
    format_detected: StepFormat  # Overall format detected
    total_steps: int  # Count of steps
    has_dependencies: bool  # Whether dependencies were detected
    original_response: str  # Original LLM response


class StepExtractor:
    """
    Extracts implementation steps from LLM-generated enhancement responses.

    Handles multiple input formats:
    - Numbered: "1. First step", "2. Second step"
    - Bullets: "- Step", "* Step", "• Step"
    - Prose: Paragraph with embedded step markers like "Step 1:"

    Implements AC1 requirements.
    """

    # Patterns for detecting steps
    NUMBERED_PATTERN = r"^\s*(\d+)\s*[\.\)]\s+(.+?)$"
    BULLET_PATTERNS = [
        r"^\s*[\-\*•]\s+(.+?)$",  # - or * or •
        r"^\s*▪\s+(.+?)$",  # Bullet
    ]
    STEP_KEYWORD_PATTERN = r"(?:step|phase|stage)\s+(\d+)[\s:]*(.+?)$"

    # Actionable keyword detection (AC1 validation)
    ACTIONABLE_VERBS = {
        "create",
        "add",
        "implement",
        "write",
        "build",
        "setup",
        "configure",
        "install",
        "run",
        "execute",
        "test",
        "verify",
        "validate",
        "check",
        "update",
        "modify",
        "change",
        "refactor",
        "remove",
        "delete",
        "import",
        "export",
        "deploy",
        "commit",
        "push",
        "review",
        "merge",
        "handle",
        "catch",
        "throw",
        "raise",
        "fix",
        "debug",
        "optimize",
        "analyze",
        "generate",
        "parse",
        "extract",
        "connect",
        "integrate",
        "sync",
        "authenticate",
        "authorize",
        "encrypt",
        "decrypt",
        "hash",
        "validate",
    }

    # Dependency keywords
    DEPENDENCY_KEYWORDS = {
        "after",
        "before",
        "once",
        "first",
        "then",
        "next",
        "finally",
        "subsequently",
        "following",
        "upon",
        "dependent on",
        "requires",
    }

    def __init__(self):
        """Initialize step extractor."""
        logger.debug("Initialized StepExtractor")

    def extract_steps(self, llm_response: str) -> ExtractedSteps:
        """
        Extract implementation steps from LLM response.

        AC1: Extract steps in various formats

        Args:
            llm_response: LLM-generated enhancement response

        Returns:
            ExtractedSteps with parsed steps and metadata
        """
        logger.info(
            f"Extracting implementation steps from response ({len(llm_response)} chars)"
        )

        if not llm_response or not llm_response.strip():
            logger.warning("Empty response provided to step extractor")
            return ExtractedSteps(
                steps=[],
                step_groups=[],
                format_detected=StepFormat.UNKNOWN,
                total_steps=0,
                has_dependencies=False,
                original_response=llm_response,
            )

        # Try different extraction methods in order of specificity
        steps = self._extract_numbered_steps(llm_response)
        format_type = StepFormat.NUMBERED

        if not steps:
            steps = self._extract_bullet_steps(llm_response)
            format_type = StepFormat.BULLETS

        if not steps:
            steps = self._extract_keyword_steps(llm_response)
            format_type = StepFormat.PROSE

        if not steps:
            # Fallback: treat response as single step
            logger.warning(
                "Could not extract structured steps, treating as single step"
            )
            steps = [
                ImplementationStep(
                    number=1,
                    content=llm_response.strip(),
                    original_text=llm_response.strip(),
                    format_detected=StepFormat.UNKNOWN,
                    is_actionable=self._is_actionable(llm_response),
                )
            ]
            format_type = StepFormat.UNKNOWN

        # Post-processing
        steps = self._validate_and_clean_steps(steps)
        steps = self._detect_dependencies(steps)
        steps = self._estimate_complexity(steps)

        # Group steps
        step_groups = self._group_steps(steps)

        has_dependencies = any(step.dependencies for step in steps)

        result = ExtractedSteps(
            steps=steps,
            step_groups=step_groups,
            format_detected=format_type,
            total_steps=len(steps),
            has_dependencies=has_dependencies,
            original_response=llm_response,
        )

        logger.info(
            f"Extracted {len(steps)} steps in {format_type.value} format, "
            f"{len(step_groups)} groups, "
            f"dependencies={'yes' if has_dependencies else 'no'}"
        )

        return result

    def _extract_numbered_steps(self, response: str) -> List[ImplementationStep]:
        """Extract numbered steps (1. Step, 2. Step)."""
        steps = []
        lines = response.split("\n")

        for line in lines:
            match = re.match(self.NUMBERED_PATTERN, line, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                content = match.group(2).strip()
                if content:
                    steps.append(
                        ImplementationStep(
                            number=number,
                            content=content,
                            original_text=line.strip(),
                            format_detected=StepFormat.NUMBERED,
                        )
                    )

        # Sort by number and renumber sequentially
        if steps:
            steps.sort(key=lambda s: s.number)
            for i, step in enumerate(steps, 1):
                step.number = i

        return steps

    def _extract_bullet_steps(self, response: str) -> List[ImplementationStep]:
        """Extract bullet steps (-, *, •)."""
        steps = []
        lines = response.split("\n")
        step_num = 0

        for line in lines:
            for pattern in self.BULLET_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    content = match.group(1).strip()
                    if content:
                        step_num += 1
                        steps.append(
                            ImplementationStep(
                                number=step_num,
                                content=content,
                                original_text=line.strip(),
                                format_detected=StepFormat.BULLETS,
                            )
                        )
                    break

        return steps

    def _extract_keyword_steps(self, response: str) -> List[ImplementationStep]:
        """Extract steps marked with keywords (Step 1:, Phase 2:, etc)."""
        steps = []

        # Find all step-like patterns
        for match in re.finditer(
            self.STEP_KEYWORD_PATTERN, response, re.IGNORECASE | re.MULTILINE
        ):
            number = int(match.group(1))
            content = match.group(2).strip()

            if content:
                steps.append(
                    ImplementationStep(
                        number=number,
                        content=content,
                        original_text=match.group(0),
                        format_detected=StepFormat.PROSE,
                    )
                )

        # Sort and renumber
        if steps:
            steps.sort(key=lambda s: s.number)
            for i, step in enumerate(steps, 1):
                step.number = i

        return steps

    def _validate_and_clean_steps(
        self, steps: List[ImplementationStep]
    ) -> List[ImplementationStep]:
        """Validate and clean extracted steps."""
        cleaned = []

        for step in steps:
            # Clean up whitespace
            step.content = step.content.strip()
            step.content = re.sub(r"\s+", " ", step.content)

            # Check if actionable
            step.is_actionable = self._is_actionable(step.content)

            # Only keep non-empty steps
            if step.content:
                cleaned.append(step)

        return cleaned

    def _is_actionable(self, text: str) -> bool:
        """Check if text contains actionable guidance (AC1 validation)."""
        # Look for verbs that indicate action
        words = text.lower().split()

        # Check for actionable verbs in first few words
        for word in words[:5]:
            # Remove punctuation
            clean_word = word.rstrip(".,!?;:")
            if clean_word in self.ACTIONABLE_VERBS:
                return True

        # Fallback: check if text is not just generic advice
        generic_phrases = {
            "note",
            "remember",
            "consider",
            "think about",
            "be aware of",
            "bear in mind",
        }

        if any(phrase in text.lower() for phrase in generic_phrases):
            return True  # At least it's guidance

        return len(text) > 20  # Non-empty is better than empty

    def _detect_dependencies(
        self, steps: List[ImplementationStep]
    ) -> List[ImplementationStep]:
        """Detect step dependencies based on keywords and ordering (AC1)."""
        for i, step in enumerate(steps):
            content_lower = step.content.lower()

            # Check for dependency keywords
            for keyword in self.DEPENDENCY_KEYWORDS:
                if keyword in content_lower:
                    # Look for step references like "after step 1"
                    match = re.search(r"step\s+(\d+)", content_lower)
                    if match:
                        dep_num = int(match.group(1))
                        if dep_num < step.number and dep_num not in step.dependencies:
                            step.dependencies.append(dep_num)
                    break

            # Check for implicit dependency (if step mentions "then" or "next")
            if any(word in content_lower for word in ["then", "next", "after that"]):
                if i > 0:
                    # Depends on previous step
                    step.dependencies.append(steps[i - 1].number)

        return steps

    def _estimate_complexity(
        self, steps: List[ImplementationStep]
    ) -> List[ImplementationStep]:
        """Estimate complexity of each step."""
        for step in steps:
            content_lower = step.content.lower()

            # Complex indicators
            complex_words = {
                "refactor",
                "optimize",
                "architecture",
                "design",
                "algorithm",
                "complex",
            }
            if any(word in content_lower for word in complex_words):
                step.complexity = "complex"
            # Simple indicators
            elif any(
                word in content_lower for word in ["add", "change", "update", "fix"]
            ):
                step.complexity = "simple"
            else:
                step.complexity = "moderate"

        return steps

    def _group_steps(self, steps: List[ImplementationStep]) -> List[StepGroup]:
        """Group related steps together (AC1)."""
        groups: Dict[str, List[ImplementationStep]] = {}

        # Simple grouping: by content similarity
        current_group = "Implementation"

        for step in steps:
            content_lower = step.content.lower()

            # Detect group by keywords
            if any(
                word in content_lower
                for word in ["test", "verify", "check", "validate"]
            ):
                group_name = "Testing"
            elif any(
                word in content_lower for word in ["deploy", "release", "publish"]
            ):
                group_name = "Deployment"
            elif any(
                word in content_lower for word in ["document", "comment", "docstring"]
            ):
                group_name = "Documentation"
            else:
                group_name = current_group

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append(step)
            current_group = group_name

        # Create group objects
        result = []
        for group_name in ["Implementation", "Testing", "Documentation", "Deployment"]:
            if group_name in groups:
                result.append(
                    StepGroup(
                        name=group_name,
                        steps=groups[group_name],
                        description=f"{group_name} phase",
                    )
                )

        return result
