"""
Phase 4: AGENTS.md Auto-Generation System

Automatically generates AGENTS.md files for projects to provide AI agents
with project-specific context, constraints, and development guidelines.

Key Components:
- TemplateRegistry: Manages language-specific AGENTS.md templates
- ContentExtractor: Extracts project information for template filling
- AgentsTemplateGenerator: Generates AGENTS.md content
- AgentsWriter: Writes AGENTS.md to project root
- AgentsGenerator: Main entry point for complete workflow
"""

from .template_registry import TemplateRegistry, TemplateType
from .content_extractor import ContentExtractor
from .template_generator import AgentsTemplateGenerator
from .agents_writer import AgentsWriter
from .agents_generator import AgentsGenerator, generate_agents_md

__all__ = [
    "TemplateRegistry",
    "TemplateType",
    "ContentExtractor",
    "AgentsTemplateGenerator",
    "AgentsWriter",
    "AgentsGenerator",
    "generate_agents_md",
]
