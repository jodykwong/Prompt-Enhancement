"""
Project context data structures for LLM enhancement.

Contains dataclasses that represent collected project information
used for building project-aware enhancement prompts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class StandardsDetectionResult:
    """Result of detecting a single coding standard."""

    standard_name: str
    detected_value: str
    confidence: float  # 0.0-1.0
    sample_size: int
    evidence: List[str]  # Example file names or patterns
    exceptions: Optional[str] = None  # Notes about inconsistencies


@dataclass
class CollectionMetadata:
    """Metadata about what context was collected."""

    collected_at: str  # ISO 8601 timestamp
    collection_mode: str  # "full", "partial", "minimal"
    standards_confidence: Dict[str, float]  # Confidence for each standard
    fields_collected: List[str]  # Which fields were successfully collected
    fields_skipped: List[str]  # Which optional fields were skipped
    warnings: List[str] = field(default_factory=list)  # Any issues during collection


@dataclass
class GitHistoryContext:
    """Git history information for project context."""

    current_branch: Optional[str] = None
    total_commits: Optional[int] = None
    recent_commit_count: Optional[int] = None  # e.g., last 30 days
    first_commit_date: Optional[str] = None  # ISO 8601
    last_commit_date: Optional[str] = None  # ISO 8601
    active_days: Optional[int] = None  # Days between first and last commit


@dataclass
class Dependency:
    """Information about a project dependency."""

    name: str
    version: Optional[str] = None
    package_manager: Optional[str] = None  # npm, pip, cargo, etc.


@dataclass
class ProjectContext:
    """
    Complete collected project information for LLM enhancement.

    This is the primary output of ProjectContextCollector and is used
    by PromptBuilder to create the structured LLM prompt.
    """

    # Basic project metadata
    project_name: str
    language: str  # Primary programming language
    framework: Optional[str] = None
    framework_version: Optional[str] = None

    # Detected coding standards (from Story 2.5-2.9)
    detected_standards: Dict[str, StandardsDetectionResult] = field(
        default_factory=dict
    )

    # Project structure and organization
    project_organization: Optional[str] = (
        None  # "by-feature", "by-layer", "by-type", etc.
    )

    # Git history context
    git_context: Optional[GitHistoryContext] = field(default_factory=GitHistoryContext)

    # Dependencies and libraries
    dependencies: List[Dependency] = field(default_factory=list)

    # Cache and fingerprint
    project_fingerprint: str = ""  # From Story 2.4

    # User customizations
    user_overrides: Dict[str, Any] = field(default_factory=dict)
    template_name: Optional[str] = None

    # Collection transparency
    collection_metadata: Optional[CollectionMetadata] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary (JSON-serializable).

        Returns:
            Dictionary representation of ProjectContext
        """
        return {
            "project_name": self.project_name,
            "language": self.language,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "detected_standards": {
                k: {
                    "standard_name": v.standard_name,
                    "detected_value": v.detected_value,
                    "confidence": v.confidence,
                    "sample_size": v.sample_size,
                    "evidence": v.evidence,
                    "exceptions": v.exceptions,
                }
                for k, v in self.detected_standards.items()
            },
            "project_organization": self.project_organization,
            "git_context": (
                {
                    "current_branch": self.git_context.current_branch,
                    "total_commits": self.git_context.total_commits,
                    "recent_commit_count": self.git_context.recent_commit_count,
                    "first_commit_date": self.git_context.first_commit_date,
                    "last_commit_date": self.git_context.last_commit_date,
                    "active_days": self.git_context.active_days,
                }
                if self.git_context
                else None
            ),
            "dependencies": [
                {
                    "name": d.name,
                    "version": d.version,
                    "package_manager": d.package_manager,
                }
                for d in self.dependencies
            ],
            "project_fingerprint": self.project_fingerprint,
            "user_overrides": self.user_overrides,
            "template_name": self.template_name,
            "collection_metadata": (
                {
                    "collected_at": self.collection_metadata.collected_at,
                    "collection_mode": self.collection_metadata.collection_mode,
                    "standards_confidence": self.collection_metadata.standards_confidence,
                    "fields_collected": self.collection_metadata.fields_collected,
                    "fields_skipped": self.collection_metadata.fields_skipped,
                    "warnings": self.collection_metadata.warnings,
                }
                if self.collection_metadata
                else None
            ),
        }

    def get_size_bytes(self) -> int:
        """
        Estimate size of context in bytes (for AC7 validation).

        Returns:
            Approximate size in bytes
        """
        import json

        return len(json.dumps(self.to_dict()).encode("utf-8"))
