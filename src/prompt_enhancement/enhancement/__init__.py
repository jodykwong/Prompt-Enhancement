"""
Enhancement module - Project-aware prompt enhancement generation.

This module implements Story 3.1: Build Enhancement Prompt - Collect Project Context.

Main components:
- ProjectContext: Data structure holding all project information
- ProjectContextCollector: Collects context from analysis results
- PromptBuilder: Builds structured LLM prompts
- SensitiveDataValidator: Ensures no sensitive data in prompts
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

__all__ = [
    "ProjectContext",
    "StandardsDetectionResult",
    "CollectionMetadata",
    "GitHistoryContext",
    "Dependency",
    "ProjectContextCollector",
    "PromptBuilder",
    "SensitiveDataValidator",
]
