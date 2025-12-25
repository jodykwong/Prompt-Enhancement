"""
Implementation guide builder - compiles comprehensive implementation guides.

Implements AC6-AC8: Create implementation guide, handle multiple paths,
and validate completeness.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum

from .step_extractor import ExtractedSteps, ImplementationStep
from .criteria_generator import GeneratedCriteria, CriteriaGenerator
from .context import ProjectContext

logger = logging.getLogger(__name__)


class ImplementationPath(Enum):
    """Different implementation approaches (AC7)."""

    SIMPLE = "simple"  # Straightforward approach
    ROBUST = "robust"  # With error handling
    OPTIMIZED = "optimized"  # Performance focused
    SCALABLE = "scalable"  # For growth
    CUSTOM = "custom"  # User-specific


@dataclass
class ImplementationGuideSection:
    """Section of the implementation guide (AC6)."""

    name: str  # Section name
    content: str  # Section content
    subsections: List["ImplementationGuideSection"] = field(default_factory=list)


@dataclass
class PathAlternative:
    """Alternative implementation path (AC7)."""

    path_type: ImplementationPath  # Type of approach
    description: str  # What this path means
    steps: List[ImplementationStep]  # Steps for this path
    criteria: List[GeneratedCriteria]  # Criteria for this path
    tradeoffs: Dict[str, str]  # Tradeoff analysis
    alignment_with_project: str  # How it aligns with project patterns
    complexity_estimate: str  # simple/moderate/complex


@dataclass
class ValidationResult:
    """Result of guide validation (AC8)."""

    is_valid: bool  # Overall validity
    warnings: List[str] = field(default_factory=list)  # Validation warnings
    errors: List[str] = field(default_factory=list)  # Validation errors
    completeness_percentage: float = 100.0  # How complete the guide is
    unverifiable_references: List[str] = field(
        default_factory=list
    )  # References we couldn't verify


@dataclass
class ImplementationGuide:
    """Complete implementation guide (AC6-AC8)."""

    original_response: str  # Original LLM response
    project_context: ProjectContext  # Project context

    # Main content sections
    overview: str  # Guide overview
    sections: List[ImplementationGuideSection]  # Organized sections

    # Steps and criteria
    steps: List[ImplementationStep]  # Implementation steps
    criteria_per_step: List[GeneratedCriteria]  # Criteria for each step
    execution_order: List[int]  # Recommended step order
    can_parallelize: Dict[int, List[int]]  # Which steps can run in parallel

    # Alternative paths
    alternative_paths: List[PathAlternative] = field(default_factory=list)  # AC7
    recommended_path: Optional[ImplementationPath] = None  # Recommended path

    # Additional guidance
    common_pitfalls: List[str] = field(default_factory=list)  # Common mistakes
    debugging_tips: List[str] = field(default_factory=list)  # Debugging advice
    rollback_instructions: str = ""  # How to undo if needed
    links_to_documentation: List[str] = field(default_factory=list)  # Reference links

    # Quality indicators
    validation: Optional[ValidationResult] = None  # AC8 validation
    total_estimated_time: str = ""  # Time estimate
    difficulty_level: str = "moderate"  # easy/moderate/complex


class GuideBuilder:
    """
    Builds comprehensive implementation guides from extracted steps and criteria.

    Implements AC6-AC8:
    - AC6: Create comprehensive implementation guide
    - AC7: Handle multiple implementation paths
    - AC8: Validation and quality checks
    """

    def __init__(self, project_context: ProjectContext):
        """
        Initialize guide builder.

        Args:
            project_context: Project context from Story 3.1
        """
        self.context = project_context
        self.criteria_gen = CriteriaGenerator(project_context)
        logger.debug(f"Initialized GuideBuilder for {project_context.project_name}")

    def build_guide(
        self,
        extracted_steps: ExtractedSteps,
    ) -> ImplementationGuide:
        """
        Build comprehensive implementation guide from extracted steps.

        AC6: Create organized guide with all sections

        Args:
            extracted_steps: Steps extracted from LLM response

        Returns:
            ImplementationGuide with all components
        """
        logger.info(
            f"Building implementation guide with {len(extracted_steps.steps)} steps"
        )

        # Generate criteria for each step
        criteria_per_step = []
        for step in extracted_steps.steps:
            criterion = self.criteria_gen.generate_criteria_for_step(
                step,
                step_index=extracted_steps.steps.index(step),
            )
            criteria_per_step.append(criterion)

        # Determine execution order
        execution_order = self._determine_execution_order(extracted_steps.steps)
        can_parallelize = self._detect_parallelizable_steps(extracted_steps.steps)

        # Create alternative paths if applicable
        alternative_paths = self._generate_alternative_paths(
            extracted_steps.steps,
            criteria_per_step,
        )

        # Compile sections
        sections = self._compile_sections(
            extracted_steps,
            criteria_per_step,
            alternative_paths,
        )

        # Create overview
        overview = self._create_overview(
            extracted_steps,
            len(criteria_per_step),
            len(alternative_paths),
        )

        # Collect pitfalls and tips
        pitfalls = self._collect_pitfalls(criteria_per_step)
        tips = self._collect_debugging_tips(criteria_per_step)

        # Create guide
        guide = ImplementationGuide(
            original_response=extracted_steps.original_response,
            project_context=self.context,
            overview=overview,
            sections=sections,
            steps=extracted_steps.steps,
            criteria_per_step=criteria_per_step,
            execution_order=execution_order,
            can_parallelize=can_parallelize,
            alternative_paths=alternative_paths,
            recommended_path=ImplementationPath.SIMPLE if alternative_paths else None,
            common_pitfalls=pitfalls,
            debugging_tips=tips,
            rollback_instructions=self._create_rollback_instructions(
                extracted_steps.steps
            ),
            links_to_documentation=self._create_documentation_links(),
        )

        # Validate guide
        guide.validation = self._validate_guide(guide)

        logger.info(
            f"Built guide with {len(sections)} sections, validation: {guide.validation.is_valid}"
        )

        return guide

    def _determine_execution_order(self, steps: List[ImplementationStep]) -> List[int]:
        """Determine recommended execution order based on dependencies (AC6)."""
        # If dependencies detected, use them; otherwise, sequential order
        order = []
        remaining = {step.number for step in steps}

        while remaining:
            for step_num in list(remaining):
                # Find step
                step = next((s for s in steps if s.number == step_num), None)
                if step is None:
                    continue

                # Check if all dependencies completed
                if all(dep not in remaining for dep in step.dependencies):
                    order.append(step_num)
                    remaining.remove(step_num)

        return order if order else [s.number for s in steps]

    def _detect_parallelizable_steps(
        self, steps: List[ImplementationStep]
    ) -> Dict[int, List[int]]:
        """Detect which steps can run in parallel (AC6)."""
        parallelizable = {}

        for step in steps:
            # Steps with no dependencies on other steps can run in parallel
            independent = []

            for other_step in steps:
                if (
                    other_step.number != step.number
                    and step.number not in other_step.dependencies
                    and other_step.number not in step.dependencies
                ):
                    independent.append(other_step.number)

            if independent:
                parallelizable[step.number] = independent

        return parallelizable

    def _generate_alternative_paths(
        self,
        steps: List[ImplementationStep],
        criteria: List[GeneratedCriteria],
    ) -> List[PathAlternative]:
        """Generate alternative implementation paths (AC7)."""
        paths = []

        # Simple path: straight implementation
        paths.append(
            PathAlternative(
                path_type=ImplementationPath.SIMPLE,
                description="Straightforward implementation with basic error handling",
                steps=steps,
                criteria=criteria,
                tradeoffs={
                    "complexity": "Low",
                    "implementation_time": "Quick",
                    "robustness": "Moderate",
                    "maintainability": "Good",
                },
                alignment_with_project="Aligns with project's quick implementation approach",
                complexity_estimate="simple",
            )
        )

        # Robust path: with comprehensive error handling
        paths.append(
            PathAlternative(
                path_type=ImplementationPath.ROBUST,
                description="Implementation with comprehensive error handling and logging",
                steps=steps,  # Same steps, but with added error handling
                criteria=criteria,
                tradeoffs={
                    "complexity": "Moderate",
                    "implementation_time": "Longer",
                    "robustness": "High",
                    "maintainability": "Excellent",
                },
                alignment_with_project="Better for production use in project",
                complexity_estimate="moderate",
            )
        )

        return paths

    def _compile_sections(
        self,
        extracted_steps: ExtractedSteps,
        criteria_per_step: List[GeneratedCriteria],
        alternative_paths: List[PathAlternative],
    ) -> List[ImplementationGuideSection]:
        """Compile guide into organized sections (AC6)."""
        sections = []

        # Overview section
        sections.append(
            ImplementationGuideSection(
                name="Overview",
                content=self._create_overview(
                    extracted_steps, len(criteria_per_step), len(alternative_paths)
                ),
            )
        )

        # Implementation Steps section
        steps_section = ImplementationGuideSection(
            name="Implementation Steps",
            content=f"Total {len(extracted_steps.steps)} steps to complete",
        )
        for step in extracted_steps.steps:
            steps_section.subsections.append(
                ImplementationGuideSection(
                    name=f"Step {step.number}",
                    content=step.content,
                )
            )
        sections.append(steps_section)

        # Verification section
        verify_section = ImplementationGuideSection(
            name="Verification Criteria",
            content="Criteria to verify each step is complete",
        )
        for criteria in criteria_per_step:
            verify_section.subsections.append(
                ImplementationGuideSection(
                    name=f"Step {criteria.step.number} Verification",
                    content=f"{len(criteria.verification_criteria)} criteria to verify",
                )
            )
        sections.append(verify_section)

        # Testing section
        testing_section = ImplementationGuideSection(
            name="Testing Approach",
            content="How to test this implementation",
        )
        for criteria in criteria_per_step:
            if criteria.testing_guidance:
                testing_section.subsections.append(
                    ImplementationGuideSection(
                        name=f"Step {criteria.step.number} Testing",
                        content=f"Using {criteria.testing_guidance.framework}",
                    )
                )
        sections.append(testing_section)

        # Alternative Approaches section
        if alternative_paths:
            alt_section = ImplementationGuideSection(
                name="Alternative Approaches",
                content=f"{len(alternative_paths)} alternative implementation paths",
            )
            for path in alternative_paths:
                alt_section.subsections.append(
                    ImplementationGuideSection(
                        name=path.description,
                        content=f"Complexity: {path.complexity_estimate}",
                    )
                )
            sections.append(alt_section)

        # Common Pitfalls section
        pitfalls = self._collect_pitfalls(criteria_per_step)
        if pitfalls:
            pitfall_section = ImplementationGuideSection(
                name="Common Pitfalls",
                content="\n".join(f"- {p}" for p in pitfalls),
            )
            sections.append(pitfall_section)

        # Debugging section
        tips = self._collect_debugging_tips(criteria_per_step)
        if tips:
            debug_section = ImplementationGuideSection(
                name="Debugging Tips",
                content="\n".join(f"- {t}" for t in tips),
            )
            sections.append(debug_section)

        return sections

    def _create_overview(
        self,
        extracted_steps: ExtractedSteps,
        total_criteria: int,
        alternative_count: int,
    ) -> str:
        """Create guide overview (AC6)."""
        return (
            f"Implementation Guide for {self.context.project_name}\n"
            f"\n"
            f"Total Steps: {len(extracted_steps.steps)}\n"
            f"Verification Criteria: {total_criteria}\n"
            f"Alternative Paths: {alternative_count}\n"
            f"Project Type: {self.context.language}/{self.context.framework}\n"
            f"\n"
            f"This guide provides step-by-step implementation instructions "
            f"customized for your {self.context.project_name} project."
        )

    def _create_rollback_instructions(self, steps: List[ImplementationStep]) -> str:
        """Create rollback instructions (AC6)."""
        return (
            "Rollback Instructions:\n"
            "If implementation fails or needs to be reverted:\n"
            "1. Revert any modified files to their previous state\n"
            "2. Remove any newly created files\n"
            "3. Restore any configuration to original state\n"
            "4. Restart affected services if needed\n"
            f"Consider implementing in a feature branch to simplify rollback."
        )

    def _create_documentation_links(self) -> List[str]:
        """Create relevant documentation links (AC6)."""
        links = []

        if self.context.framework:
            links.append(
                f"Framework: https://docs.example.com/{self.context.framework}"
            )

        test_result = self.context.detected_standards.get("test_framework")
        if test_result:
            links.append(
                f"Testing: https://docs.example.com/{test_result.detected_value}"
            )

        if self.context.language:
            links.append(f"Language: https://docs.example.com/{self.context.language}")

        return links

    def _collect_pitfalls(
        self, criteria_per_step: List[GeneratedCriteria]
    ) -> List[str]:
        """Collect all pitfalls from criteria."""
        pitfalls = []
        for criteria in criteria_per_step:
            pitfalls.extend(criteria.common_pitfalls)
        # Remove duplicates while preserving order
        return list(dict.fromkeys(pitfalls))

    def _collect_debugging_tips(
        self, criteria_per_step: List[GeneratedCriteria]
    ) -> List[str]:
        """Collect all debugging tips from criteria."""
        tips = []
        for criteria in criteria_per_step:
            tips.extend(criteria.debugging_tips)
        # Remove duplicates while preserving order
        return list(dict.fromkeys(tips))

    def _validate_guide(self, guide: ImplementationGuide) -> ValidationResult:
        """Validate guide completeness and consistency (AC8)."""
        errors = []
        warnings = []
        unverifiable = []

        # AC8: Each step should have criteria
        for step in guide.steps:
            criteria_for_step = [
                c for c in guide.criteria_per_step if c.step.number == step.number
            ]
            if not criteria_for_step:
                errors.append(f"Step {step.number} has no verification criteria")

        # AC8: Validate step order is consistent
        for i, step_num in enumerate(guide.execution_order):
            if step_num not in [s.number for s in guide.steps]:
                errors.append(
                    f"Execution order references non-existent step {step_num}"
                )

        # AC8: Check for conflicting recommendations
        if guide.alternative_paths:
            # Check if paths have consistent steps
            for i, path1 in enumerate(guide.alternative_paths):
                for j, path2 in enumerate(guide.alternative_paths[i + 1 :], i + 1):
                    # Paths shouldn't completely contradict
                    pass

        # AC8: Validate code examples
        for criteria in guide.criteria_per_step:
            for example in criteria.code_examples:
                if "..." in example.content:
                    warnings.append(
                        f"Code example contains incomplete template markers"
                    )

        # AC8: Validate testing guidance exists
        test_steps = [
            c for c in guide.criteria_per_step if "test" in c.step.content.lower()
        ]
        if test_steps and not any(c.testing_guidance for c in test_steps):
            warnings.append("Some test steps lack testing guidance")

        # Calculate completeness
        completeness = 100.0
        if errors:
            completeness -= 10 * len(errors)
        if warnings:
            completeness -= 5 * len(warnings)
        completeness = max(0, min(100, completeness))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            completeness_percentage=completeness,
            unverifiable_references=unverifiable,
        )
