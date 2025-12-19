"""
Enhancement module - Project-aware prompt enhancement generation.

This module implements:
- Story 3.1: Build Enhancement Prompt - Collect Project Context
- Story 3.2: Call LLM to Generate Project-Aware Enhancement
- Story 3.3: Generate Project-Specific Implementation Steps and Verification Criteria

Main components:
- ProjectContext: Data structure holding all project information
- ProjectContextCollector: Collects context from analysis results
- PromptBuilder: Builds structured LLM prompts
- SensitiveDataValidator: Ensures no sensitive data in prompts
- EnhancementGenerator: Orchestrates LLM-based enhancement
- StepExtractor: Parses LLM responses to extract steps
- CriteriaGenerator: Generates verification criteria
- GuideBuilder: Creates comprehensive implementation guides
"""

from .context import (
    ProjectContext,
    StandardsDetectionResult,
    CollectionMetadata,
    GitHistoryContext,
    Dependency,
)
from .context_collector import ProjectContextCollector
from .prompt_builder import PromptBuilder
from .sensitive_validator import SensitiveDataValidator
from .generator import EnhancementGenerator, EnhancementResult
from .step_extractor import (
    StepExtractor,
    ImplementationStep,
    StepFormat,
    ExtractedSteps,
    StepGroup,
)
from .criteria_generator import (
    CriteriaGenerator,
    VerificationCriterion,
    CodeExample,
    TestingGuidance,
    GeneratedCriteria,
    ArtifactType,
)
from .guide_builder import (
    GuideBuilder,
    ImplementationGuide,
    ImplementationPath,
    PathAlternative,
    ImplementationGuideSection,
    ValidationResult,
)

__all__ = [
    # Story 3.1 exports
    "ProjectContext",
    "StandardsDetectionResult",
    "CollectionMetadata",
    "GitHistoryContext",
    "Dependency",
    "ProjectContextCollector",
    "PromptBuilder",
    "SensitiveDataValidator",
    # Story 3.2 exports
    "EnhancementGenerator",
    "EnhancementResult",
    # Story 3.3 exports
    "StepExtractor",
    "ImplementationStep",
    "StepFormat",
    "ExtractedSteps",
    "StepGroup",
    "CriteriaGenerator",
    "VerificationCriterion",
    "CodeExample",
    "TestingGuidance",
    "GeneratedCriteria",
    "ArtifactType",
    "GuideBuilder",
    "ImplementationGuide",
    "ImplementationPath",
    "PathAlternative",
    "ImplementationGuideSection",
    "ValidationResult",
]
