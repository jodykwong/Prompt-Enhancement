"""
Project context collector for LLM enhancement.

Collects and organizes project information from analysis results
to create a comprehensive context for enhancement generation (AC1).
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from .context import (
    ProjectContext,
    StandardsDetectionResult,
    CollectionMetadata,
    GitHistoryContext,
    Dependency,
)
from ..symbol_indexer import SymbolIndexer

logger = logging.getLogger(__name__)


class ProjectContextCollector:
    """
    Collects project context information for LLM enhancement.

    Integrates results from Epic 2 analysis (project detection,
    standards detection, git history) into a unified ProjectContext
    object suitable for LLM consumption.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize context collector.

        Args:
            project_root: Root directory of project (defaults to cwd)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.symbol_indexer = SymbolIndexer(str(self.project_root))
        logger.debug(f"Initialized ProjectContextCollector for {self.project_root}")

    def collect_context(
        self,
        analysis_result: Optional[Dict[str, Any]] = None,
        collection_mode: str = "full",
        user_overrides: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
    ) -> ProjectContext:
        """
        Collect complete project context.

        Args:
            analysis_result: Results from ProjectAnalyzer (Epic 2)
            collection_mode: "full", "partial", or "minimal"
            user_overrides: User-specified standard overrides
            template_name: Name of template being used (if any)

        Returns:
            ProjectContext with all collected information
        """
        logger.info(f"Collecting project context (mode={collection_mode})")

        context = ProjectContext(
            project_name=self._extract_project_name(),
            language=self._extract_language(analysis_result),
            framework=self._extract_framework(analysis_result),
            framework_version=self._extract_framework_version(analysis_result),
            project_fingerprint=self._extract_fingerprint(analysis_result),
            user_overrides=user_overrides or {},
            template_name=template_name,
        )

        # Collect detected standards
        if analysis_result and "confidence_report" in analysis_result:
            context.detected_standards = self._extract_standards(
                analysis_result["confidence_report"]
            )

        # Collect Git history
        if analysis_result and "git_history" in analysis_result:
            context.git_context = self._extract_git_context(analysis_result["git_history"])

        # Collect dependencies
        if analysis_result and "indicator_files" in analysis_result:
            context.dependencies = self._extract_dependencies(
                analysis_result["indicator_files"]
            )

        # Collect project organization
        if analysis_result and "confidence_report" in analysis_result:
            context.project_organization = self._extract_project_organization(
                analysis_result["confidence_report"]
            )

        # Generate collection metadata
        context.collection_metadata = self._create_collection_metadata(
            context, collection_mode
        )

        logger.debug(f"Context collected: size={context.get_size_bytes()} bytes")
        return context

    def _extract_project_name(self) -> str:
        """Extract project name from directory or config."""
        # Try to get from pyproject.toml or package.json
        try:
            # Simple approach: use directory name
            return self.project_root.name
        except Exception as e:
            logger.warning(f"Could not extract project name: {e}")
            return "unknown-project"

    def _extract_language(self, analysis_result: Optional[Dict[str, Any]]) -> str:
        """
        Extract primary programming language.

        AC1: Required field
        """
        if analysis_result and "tech_stack" in analysis_result:
            try:
                tech_stack = analysis_result["tech_stack"]
                if hasattr(tech_stack, "primary_language"):
                    lang = tech_stack.primary_language
                    return lang.value if hasattr(lang, "value") else str(lang)
            except Exception as e:
                logger.warning(f"Error extracting language: {e}")

        return "unknown"

    def _extract_framework(self, analysis_result: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract framework information."""
        if analysis_result and "tech_stack" in analysis_result:
            try:
                tech_stack = analysis_result["tech_stack"]
                if hasattr(tech_stack, "frameworks") and tech_stack.frameworks:
                    # Return primary framework
                    return tech_stack.frameworks[0] if tech_stack.frameworks else None
            except Exception as e:
                logger.warning(f"Error extracting framework: {e}")

        return None

    def _extract_framework_version(
        self, analysis_result: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract framework version."""
        if analysis_result and "tech_stack" in analysis_result:
            try:
                tech_stack = analysis_result["tech_stack"]
                if hasattr(tech_stack, "framework_versions") and tech_stack.framework_versions:
                    return tech_stack.framework_versions.get("primary")
            except Exception as e:
                logger.warning(f"Error extracting framework version: {e}")

        return None

    def _extract_fingerprint(self, analysis_result: Optional[Dict[str, Any]]) -> str:
        """Extract project fingerprint for caching."""
        if analysis_result and "fingerprint" in analysis_result:
            return analysis_result["fingerprint"]

        # Generate simple fingerprint if not provided
        try:
            import hashlib
            files = list(self.project_root.glob("**/*.py"))[:100]
            file_str = "".join(str(f) for f in sorted(files))
            return hashlib.md5(file_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Error generating fingerprint: {e}")
            return "unknown"

    def _extract_standards(self, confidence_report: Optional[Any]) -> Dict[str, StandardsDetectionResult]:
        """
        Extract detected standards from confidence report.

        AC1: Collect detected standards
        AC3: Handle low-confidence standards
        """
        standards = {}

        if not confidence_report:
            return standards

        try:
            # Map from confidence report to StandardsDetectionResult
            report_dict = (
                confidence_report.to_dict()
                if hasattr(confidence_report, "to_dict")
                else confidence_report
            )

            for standard_name, standard_data in report_dict.items():
                if standard_name in ["naming_convention", "test_framework", "documentation_style",
                                    "code_organization", "module_naming"]:
                    try:
                        result = StandardsDetectionResult(
                            standard_name=standard_name,
                            detected_value=standard_data.get("detected_value", "unknown"),
                            confidence=float(standard_data.get("confidence", 0.0)),
                            sample_size=int(standard_data.get("sample_size", 0)),
                            evidence=standard_data.get("evidence", []),
                            exceptions=standard_data.get("exceptions"),
                        )
                        standards[standard_name] = result
                        logger.debug(f"Extracted standard: {standard_name} ({result.confidence:.0%})")
                    except Exception as e:
                        logger.warning(f"Error extracting standard {standard_name}: {e}")

        except Exception as e:
            logger.warning(f"Error extracting standards: {e}")

        return standards

    def _extract_git_context(self, git_history: Optional[Any]) -> GitHistoryContext:
        """Extract Git history context."""
        context = GitHistoryContext()

        if not git_history:
            return context

        try:
            git_dict = (
                git_history.to_dict()
                if hasattr(git_history, "to_dict")
                else git_history
            )

            context.current_branch = git_dict.get("current_branch")
            context.total_commits = git_dict.get("total_commits")
            context.recent_commit_count = git_dict.get("recent_commit_count")
            context.first_commit_date = git_dict.get("first_commit_date")
            context.last_commit_date = git_dict.get("last_commit_date")
            context.active_days = git_dict.get("active_days")

            logger.debug(f"Extracted git context: {context.total_commits} commits")
        except Exception as e:
            logger.warning(f"Error extracting git context: {e}")

        return context

    def _extract_dependencies(self, indicator_files: Optional[Any]) -> List[Dependency]:
        """Extract dependencies from indicator files."""
        dependencies = []

        if not indicator_files:
            return dependencies

        try:
            indicator_dict = (
                indicator_files.to_dict()
                if hasattr(indicator_files, "to_dict")
                else indicator_files
            )

            # Extract from dependencies dict if available
            if "dependencies" in indicator_dict:
                deps = indicator_dict["dependencies"]
                if isinstance(deps, dict):
                    for name, version in deps.items():
                        dependencies.append(
                            Dependency(
                                name=name,
                                version=version,
                                package_manager=self._infer_package_manager(name),
                            )
                        )

            logger.debug(f"Extracted {len(dependencies)} dependencies")
        except Exception as e:
            logger.warning(f"Error extracting dependencies: {e}")

        return dependencies

    def _infer_package_manager(self, package_name: str) -> Optional[str]:
        """Infer package manager from package name patterns."""
        if any(ext in package_name for ext in ["-py", "py-"]):
            return "pip"
        if package_name.startswith("@"):
            return "npm"
        if package_name.endswith("-rs"):
            return "cargo"
        return None

    def _extract_project_organization(self, confidence_report: Optional[Any]) -> Optional[str]:
        """Extract project organization pattern."""
        try:
            report_dict = (
                confidence_report.to_dict()
                if hasattr(confidence_report, "to_dict")
                else confidence_report
            )

            if "code_organization" in report_dict:
                return report_dict["code_organization"].get("detected_value")
        except Exception as e:
            logger.warning(f"Error extracting project organization: {e}")

        return None

    def _create_collection_metadata(
        self,
        context: ProjectContext,
        collection_mode: str,
    ) -> CollectionMetadata:
        """
        Create collection metadata for transparency.

        AC8: Context transparency
        """
        fields_collected = []
        fields_skipped = []

        # Track which fields were collected
        if context.language and context.language != "unknown":
            fields_collected.append("language")
        else:
            fields_skipped.append("language")

        if context.framework:
            fields_collected.append("framework")
        else:
            fields_skipped.append("framework")

        if context.detected_standards:
            fields_collected.append("detected_standards")
        else:
            fields_skipped.append("detected_standards")

        if context.git_context.total_commits:
            fields_collected.append("git_history")
        else:
            fields_skipped.append("git_history")

        if context.dependencies:
            fields_collected.append("dependencies")
        else:
            fields_skipped.append("dependencies")

        # Build standards confidence map
        standards_confidence = {
            name: result.confidence
            for name, result in context.detected_standards.items()
        }

        return CollectionMetadata(
            collected_at=datetime.utcnow().isoformat() + "Z",
            collection_mode=collection_mode,
            standards_confidence=standards_confidence,
            fields_collected=fields_collected,
            fields_skipped=fields_skipped,
            warnings=self._generate_warnings(context, collection_mode),
        )

    def _generate_warnings(self, context: ProjectContext, collection_mode: str) -> List[str]:
        """Generate warnings about collection issues."""
        warnings = []

        # Check confidence levels
        for name, result in context.detected_standards.items():
            if result.confidence < 0.60:
                warnings.append(
                    f"Low confidence in {name}: {result.confidence:.0%} "
                    f"(consider using --override)"
                )

        # Check if collection mode is degraded
        if collection_mode in ["partial", "minimal"]:
            warnings.append(f"Collection mode is {collection_mode} - some context unavailable")

        return warnings

    def get_file_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get symbol index for a file (functions, classes, methods).

        Phase 2 Feature: Reduces token usage by replacing full file content
        with symbol signatures.

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of symbol dictionaries with name, type, signature, line number
        """
        try:
            symbols = self.symbol_indexer.get_file_symbols(file_path)
            return [self._symbol_to_dict(s) for s in symbols]
        except Exception as e:
            logger.warning(f"Error getting file symbols for {file_path}: {e}")
            return []

    def _symbol_to_dict(self, symbol: Any) -> Dict[str, Any]:
        """
        Convert ExtractedSymbol to dictionary format.

        Args:
            symbol: ExtractedSymbol object

        Returns:
            Dictionary representation of symbol
        """
        return {
            'name': symbol.name,
            'type': symbol.symbol_type,
            'signature': symbol.signature,
            'line': symbol.line_number,
            'parent_class': symbol.parent_class,
            'decorators': symbol.decorators if symbol.decorators else [],
            'docstring': symbol.docstring,
        }
