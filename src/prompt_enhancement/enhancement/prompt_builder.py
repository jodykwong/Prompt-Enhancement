"""
LLM prompt builder for project-aware enhancement.

Constructs structured prompts for LLM that include project context
and detected standards (AC2, AC6, AC8).
"""

import logging
from typing import Optional
from .context import ProjectContext

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds structured LLM prompts with project context.

    Takes a ProjectContext and original user prompt, and creates
    a structured message for the LLM that includes project metadata,
    detected standards, and user preferences.
    """

    def __init__(self, show_confidence: bool = True):
        """
        Initialize prompt builder.

        Args:
            show_confidence: Whether to include confidence scores
        """
        self.show_confidence = show_confidence
        logger.debug("Initialized PromptBuilder")

    def build_prompt(
        self,
        user_prompt: str,
        project_context: ProjectContext,
    ) -> str:
        """
        Build structured LLM prompt.

        AC2: Build structured enhancement prompt
        AC6: Format context for different use cases

        Args:
            user_prompt: Original user prompt (preserved unchanged)
            project_context: Collected project context

        Returns:
            Structured prompt for LLM
        """
        mode = "unknown"
        if project_context.collection_metadata:
            mode = project_context.collection_metadata.collection_mode
        logger.debug(f"Building LLM prompt (mode={mode})")

        sections = []

        # Section 1: Original prompt (always included, unchanged)
        sections.append(self._build_original_prompt_section(user_prompt))

        # Section 2: Project metadata
        sections.append(self._build_project_metadata_section(project_context))

        # Section 3: Detected standards
        sections.append(self._build_detected_standards_section(project_context))

        # Section 4: Project organization
        if project_context.project_organization:
            sections.append(self._build_organization_section(project_context))

        # Section 5: Git history
        if project_context.git_context:
            sections.append(self._build_git_section(project_context))

        # Section 6: Dependencies
        if project_context.dependencies:
            sections.append(self._build_dependencies_section(project_context))

        # Section 7: User overrides
        if project_context.user_overrides:
            sections.append(self._build_overrides_section(project_context))

        # Section 8: Template guidance
        if project_context.template_name:
            sections.append(self._build_template_section(project_context))

        prompt = "\n\n".join(sections)
        logger.debug(f"Built prompt with {len(sections)} sections ({len(prompt)} chars)")
        return prompt

    def _build_original_prompt_section(self, user_prompt: str) -> str:
        """Build section with original user prompt (AC2, unchanged)."""
        return f"<ORIGINAL_PROMPT>\n{user_prompt}\n</ORIGINAL_PROMPT>"

    def _build_project_metadata_section(self, context: ProjectContext) -> str:
        """Build section with project metadata."""
        lines = ["<PROJECT_METADATA>"]
        lines.append(f"Project: {context.project_name}")
        lines.append(f"Language: {context.language}")

        if context.framework:
            lines.append(f"Framework: {context.framework}")
        if context.framework_version:
            lines.append(f"Framework Version: {context.framework_version}")

        lines.append("</PROJECT_METADATA>")
        return "\n".join(lines)

    def _build_detected_standards_section(self, context: ProjectContext) -> str:
        """
        Build section with detected coding standards.

        AC3: Handle low-confidence standards
        """
        if not context.detected_standards:
            return ""

        lines = ["<DETECTED_STANDARDS>"]

        for standard_name, standard in sorted(context.detected_standards.items()):
            # Include standard name and detected value
            confidence_str = f"{standard.confidence:.0%}"
            lines.append(f"• {standard_name}: {standard.detected_value} ({confidence_str})")

            # AC3: Mark low-confidence standards explicitly
            if standard.confidence < 0.60:
                lines.append(f"  ⚠️ LOW CONFIDENCE - Please verify")

            # Include evidence
            if standard.evidence:
                evidence_text = ", ".join(standard.evidence[:3])  # First 3 examples
                if len(standard.evidence) > 3:
                    evidence_text += f", ... ({len(standard.evidence)} total)"
                lines.append(f"  Evidence: {evidence_text}")

            # Include exceptions (inconsistencies)
            if standard.exceptions:
                lines.append(f"  Exceptions: {standard.exceptions}")

            # Sample size info
            if standard.sample_size > 0:
                lines.append(f"  Sample: {standard.sample_size} files analyzed")

        lines.append("</DETECTED_STANDARDS>")
        return "\n".join(lines)

    def _build_organization_section(self, context: ProjectContext) -> str:
        """Build section with project organization pattern."""
        if not context.project_organization:
            return ""

        return (
            f"<PROJECT_ORGANIZATION>\n"
            f"Pattern: {context.project_organization}\n"
            f"</PROJECT_ORGANIZATION>"
        )

    def _build_git_section(self, context: ProjectContext) -> str:
        """Build section with Git history context."""
        if not context.git_context:
            return ""

        lines = ["<GIT_HISTORY>"]

        if context.git_context.total_commits:
            lines.append(f"Total commits: {context.git_context.total_commits}")

        if context.git_context.current_branch:
            lines.append(f"Current branch: {context.git_context.current_branch}")

        if context.git_context.active_days:
            lines.append(f"Development duration: {context.git_context.active_days} days")

        lines.append("</GIT_HISTORY>")
        return "\n".join(lines)

    def _build_dependencies_section(self, context: ProjectContext) -> str:
        """Build section with dependencies."""
        if not context.dependencies:
            return ""

        lines = ["<DEPENDENCIES>"]
        for dep in context.dependencies[:10]:  # Limit to first 10
            if dep.version:
                lines.append(f"• {dep.name} ({dep.version})")
            else:
                lines.append(f"• {dep.name}")

        if len(context.dependencies) > 10:
            lines.append(f"... and {len(context.dependencies) - 10} more")

        lines.append("</DEPENDENCIES>")
        return "\n".join(lines)

    def _build_overrides_section(self, context: ProjectContext) -> str:
        """Build section with user-specified overrides."""
        if not context.user_overrides:
            return ""

        lines = ["<USER_OVERRIDES>"]
        for key, value in context.user_overrides.items():
            lines.append(f"• {key}: {value}")

        lines.append("</USER_OVERRIDES>")
        return "\n".join(lines)

    def _build_template_section(self, context: ProjectContext) -> str:
        """Build section with template-specific guidance."""
        return (
            f"<TEMPLATE_INFO>\n"
            f"Using template: {context.template_name}\n"
            f"Apply template-specific rules and conventions\n"
            f"</TEMPLATE_INFO>"
        )

    def build_system_prompt(self) -> str:
        """
        Build system prompt for LLM.

        Returns:
            System prompt with instructions for enhancement generation
        """
        return (
            "You are an AI assistant specializing in prompt enhancement for software development. "
            "Your task is to improve and expand user prompts to include:\n"
            "1. More specific and clear requirements\n"
            "2. Implementation guidance that respects the project's detected coding standards\n"
            "3. Verification criteria to validate the solution\n"
            "4. Edge cases and error handling considerations\n\n"
            "The following project context has been provided to help you generate project-aware enhancements:\n"
            "- Detected coding standards (naming conventions, testing frameworks, documentation style)\n"
            "- Project organization patterns\n"
            "- Git history and development context\n"
            "- Key dependencies\n\n"
            "Apply the detected standards and patterns consistently throughout your enhancement."
        )
