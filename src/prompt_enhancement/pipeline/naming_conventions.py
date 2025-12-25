"""
Naming Convention Detector - Story 2.5.

Analyzes source files to detect naming convention patterns.
Supports multiple languages and categorizes conventions by frequency.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from .tech_stack import ProjectLanguage, ProjectTypeDetectionResult
from .project_files import ProjectIndicatorResult
from ..cli.performance import PerformanceTracker  # FIX HIGH #3


logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================


class NamingConventionType(Enum):
    """Supported naming convention types."""

    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"
    KEBAB_CASE = "kebab-case"
    UPPER_SNAKE_CASE = "UPPER_SNAKE_CASE"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class IdentifierCategory(Enum):
    """Categories of identifiers to analyze."""

    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    CONSTANT = "constant"
    MODULE = "module"
    PRIVATE = "private"


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ConventionOccurrence:
    """Single occurrence of a naming convention."""

    convention_type: NamingConventionType
    identifier: str
    category: IdentifierCategory
    file_path: str
    line_number: Optional[int] = None


@dataclass
class ConventionFrequency:
    """Frequency analysis for a single convention."""

    convention_type: NamingConventionType
    count: int
    percentage: float
    confidence: float
    examples: List[str] = field(default_factory=list)
    category: Optional[IdentifierCategory] = None


@dataclass
class NamingConventionResult:
    """Complete naming convention analysis result."""

    overall_dominant_convention: NamingConventionType
    overall_conventions: List[ConventionFrequency]
    overall_confidence: float
    function_conventions: List[ConventionFrequency]
    class_conventions: List[ConventionFrequency]
    variable_conventions: List[ConventionFrequency]
    constant_conventions: List[ConventionFrequency]
    sample_size: int
    files_analyzed: int
    identifiers_analyzed: int
    timestamp: str
    version: int = 1
    coverage_percentage: float = 0.0
    consistency_score: float = 0.0


# ============================================================================
# NamingConventionDetector Class
# ============================================================================


class NamingConventionDetector:
    """
    Detects and categorizes naming conventions in source code.

    Analyzes naming patterns for functions, classes, variables, and constants.
    Provides frequency analysis and confidence scoring.

    Attributes:
        project_root: Root directory of the project
        timeout_sec: Timeout for detection (default 2.0)
        max_files: Maximum files to analyze (default 100)
    """

    DEFAULT_TIMEOUT_SEC = 2.0
    MAX_FILES = 100
    NAMING_VERSION = 1

    # Regex patterns for convention classification
    SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
    # FIX HIGH #1: camelCase must have at least one uppercase letter
    # Old pattern matched pure lowercase like "get" incorrectly as camelCase
    CAMEL_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*$")
    PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
    KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9\-]*$")
    UPPER_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

    # Language-specific extraction patterns
    PYTHON_FUNCTION_PATTERN = re.compile(r"^\s*(?:def|async def)\s+([a-zA-Z_][a-zA-Z0-9_]*)")
    PYTHON_CLASS_PATTERN = re.compile(r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)")
    PYTHON_VARIABLE_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=")

    JS_FUNCTION_PATTERN = re.compile(r"(?:function)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)")
    JS_VAR_PATTERN = re.compile(r"(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[=]")
    JS_CLASS_PATTERN = re.compile(r"class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)")

    GO_PATTERN = re.compile(r"func\s+(?:\([^)]*\))?\s*([a-zA-Z_][a-zA-Z0-9_]*)")
    GO_STRUCT_PATTERN = re.compile(r"type\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+struct")

    JAVA_PATTERN = re.compile(r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*\w+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[({]")
    JAVA_CLASS_PATTERN = re.compile(r"(?:public|private)?\s*(?:final)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)")

    def __init__(
        self,
        project_root: Path,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        max_files: int = MAX_FILES,
        performance_tracker: Optional[PerformanceTracker] = None,  # FIX HIGH #3
    ):
        """
        Initialize naming convention detector.

        Args:
            project_root: Root directory to analyze
            timeout_sec: Timeout for detection (default 2.0 seconds)
            max_files: Maximum files to process (default 100)
            performance_tracker: Optional PerformanceTracker from Story 1.4 (FIX HIGH #3)
        """
        self.project_root = Path(project_root)
        self.timeout_sec = timeout_sec
        self.max_files = max_files
        self.performance_tracker = performance_tracker  # FIX HIGH #3
        self.start_time = time.perf_counter()

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def detect_naming_conventions(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
    ) -> Optional[NamingConventionResult]:
        """
        Detect naming conventions in project source files.

        Args:
            tech_result: Tech stack detection result (Story 2.1)
            files_result: Project indicator result (Story 2.2)

        Returns:
            NamingConventionResult with detected patterns, or None on failure
        """
        # FIX HIGH #3: Start performance tracking
        if self.performance_tracker:
            self.performance_tracker.start_phase("naming_conventions")

        try:
            if self._is_timeout():
                logger.warning("Naming convention detection timeout")
                if self.performance_tracker:
                    self.performance_tracker.end_phase("naming_conventions")
                return None

            # Sample representative files
            sampled_files = self._sample_files(files_result, self.max_files, tech_result)
            if not sampled_files:
                logger.warning("No files to sample for naming convention detection")
                return None

            # Extract patterns from sampled files
            all_occurrences: List[ConventionOccurrence] = []

            for file_path in sampled_files:
                if self._is_timeout():
                    logger.warning("Naming convention detection timeout during file processing")
                    break

                try:
                    patterns = self._extract_patterns_from_file(
                        file_path, tech_result.primary_language
                    )
                    all_occurrences.extend(patterns)
                except Exception as e:
                    logger.debug(f"Error extracting patterns from {file_path}: {e}")
                    continue

            if not all_occurrences:
                logger.warning("No identifiers found in sampled files")
                return self._create_empty_result(len(sampled_files), files_result)

            # Categorize conventions
            result = self._create_result_from_occurrences(
                all_occurrences,
                len(sampled_files),
                len(files_result.files_found) if files_result.files_found else 0,
            )

            # FIX HIGH #3: End performance tracking
            if self.performance_tracker:
                self.performance_tracker.end_phase("naming_conventions")

            return result

        except Exception as e:
            logger.error(f"Error detecting naming conventions: {e}", exc_info=True)
            # FIX HIGH #3: End performance tracking even on error
            if self.performance_tracker:
                self.performance_tracker.end_phase("naming_conventions")
            return None

    # ========================================================================
    # File Sampling
    # ========================================================================

    def _sample_files(
        self,
        files_result: ProjectIndicatorResult,
        max_samples: int,
        tech_result: Optional[ProjectTypeDetectionResult] = None,
    ) -> List[Path]:
        """
        Sample representative source files with multilingual support.

        FIX MEDIUM #4: Adds multilingual file sampling to ensure representative
        coverage when multiple languages are present in the project.

        Args:
            files_result: Project indicator result with file list
            max_samples: Maximum number of files to sample
            tech_result: Optional tech stack result for language detection

        Returns:
            List of sampled file paths
        """
        if not files_result.files_found:
            return []

        try:
            # Filter to source files only (exclude test, vendor, etc.)
            source_files = []
            for file_path in files_result.files_found:
                file_lower = str(file_path).lower()

                # Exclude test, vendor, and build directories
                # Be more precise: match directory separators or start of string
                skip_patterns = [
                    "/test/", "/tests/", "\\test\\", "\\tests\\",
                    "/vendor/", "\\vendor\\",
                    "/node_modules/", "\\node_modules\\",
                    "/.git/", "\\.git\\",
                    "/build/", "\\build\\",
                    "/dist/", "\\dist\\",
                    "/__pycache__/", "\\__pycache__\\",
                ]

                if any(pattern in file_lower for pattern in skip_patterns):
                    continue

                source_files.append(file_path)

            # FIX MEDIUM #4: Multilingual file sampling
            # If project has multiple languages, sample proportionally from each
            if tech_result and tech_result.secondary_languages:
                sampled = self._sample_multilingual(
                    source_files, max_samples, tech_result
                )
            else:
                # Single language: simple sampling
                sampled = source_files[:max_samples]

            # Convert to full paths (handle both strings and Path objects)
            result = []
            for f in sampled:
                if isinstance(f, Path):
                    full_path = self.project_root / f
                else:
                    full_path = self.project_root / Path(f)
                result.append(full_path)

            return result

        except Exception as e:
            logger.debug(f"Error sampling files: {e}")
            return []

    def _sample_multilingual(
        self,
        source_files: List,
        max_samples: int,
        tech_result: ProjectTypeDetectionResult,
    ) -> List:
        """
        Sample files from multiple languages proportionally.

        FIX MEDIUM #4: Ensures representative sampling across all languages
        in a multilingual project (AC5: "Includes multiple file types if multilingual").

        Strategy:
        - Primary language: 60% of samples
        - Secondary languages: 40% split equally

        Args:
            source_files: List of source files to sample from
            max_samples: Maximum number of files to sample
            tech_result: Tech stack result with language information

        Returns:
            List of sampled files with representation from all languages
        """
        # Language extension mapping
        lang_extensions = {
            ProjectLanguage.PYTHON: {'.py'},
            ProjectLanguage.NODEJS: {'.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs'},
            ProjectLanguage.GO: {'.go'},
            ProjectLanguage.RUST: {'.rs'},
            ProjectLanguage.JAVA: {'.java'},
            ProjectLanguage.CSHARP: {'.cs'},
        }

        # Group files by language
        files_by_lang: Dict[ProjectLanguage, List] = {
            tech_result.primary_language: []
        }
        for lang in tech_result.secondary_languages:
            files_by_lang[lang] = []

        # Classify files by language
        unclassified = []
        for file_path in source_files:
            file_str = str(file_path)
            suffix = Path(file_str).suffix.lower()

            classified = False
            for lang, extensions in lang_extensions.items():
                if suffix in extensions and lang in files_by_lang:
                    files_by_lang[lang].append(file_path)
                    classified = True
                    break

            if not classified:
                unclassified.append(file_path)

        # Calculate sampling quotas
        primary_quota = int(max_samples * 0.6)
        num_secondary = len(tech_result.secondary_languages)
        secondary_quota_per_lang = int((max_samples * 0.4) / num_secondary) if num_secondary > 0 else 0

        # Sample from each language
        sampled = []

        # Primary language
        primary_files = files_by_lang.get(tech_result.primary_language, [])
        sampled.extend(primary_files[:primary_quota])

        # Secondary languages
        for lang in tech_result.secondary_languages:
            lang_files = files_by_lang.get(lang, [])
            sampled.extend(lang_files[:secondary_quota_per_lang])

        # Fill remaining quota with unclassified files
        remaining = max_samples - len(sampled)
        if remaining > 0:
            sampled.extend(unclassified[:remaining])

        # If we didn't reach max_samples, top up from any remaining files
        if len(sampled) < max_samples:
            remaining = max_samples - len(sampled)
            all_remaining = []
            for lang_files in files_by_lang.values():
                all_remaining.extend(lang_files[secondary_quota_per_lang:])
            sampled.extend(all_remaining[:remaining])

        return sampled[:max_samples]

    # ========================================================================
    # Pattern Extraction
    # ========================================================================

    def _extract_patterns_from_file(
        self,
        file_path: Path,
        language: ProjectLanguage,
    ) -> List[ConventionOccurrence]:
        """
        Extract naming patterns from a single file.

        Args:
            file_path: Path to file to analyze
            language: Programming language of the file

        Returns:
            List of identified naming patterns
        """
        patterns: List[ConventionOccurrence] = []

        try:
            if not file_path.exists():
                return patterns

            # Read file (first 100 lines to avoid large files)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    lines.append(line)

            content = "\n".join(lines)

            # Extract based on language
            if language == ProjectLanguage.PYTHON:
                patterns = self._extract_python_patterns(content, file_path)
            elif language == ProjectLanguage.NODEJS:
                patterns = self._extract_javascript_patterns(content, file_path)
            elif language == ProjectLanguage.GO:
                patterns = self._extract_go_patterns(content, file_path)
            elif language == ProjectLanguage.JAVA:
                patterns = self._extract_java_patterns(content, file_path)
            else:
                # Generic extraction for other languages
                patterns = self._extract_generic_patterns(content, file_path)

            return patterns

        except Exception as e:
            logger.debug(f"Error extracting patterns from {file_path}: {e}")
            return []

    def _extract_python_patterns(
        self,
        content: str,
        file_path: Path,
    ) -> List[ConventionOccurrence]:
        """Extract patterns from Python file."""
        patterns: List[ConventionOccurrence] = []

        for line_num, line in enumerate(content.split("\n"), 1):
            # Functions
            match = self.PYTHON_FUNCTION_PATTERN.match(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    if not identifier.startswith("_"):
                        convention = self._classify_convention(identifier)
                        patterns.append(
                            ConventionOccurrence(
                                convention_type=convention,
                                identifier=identifier,
                                category=IdentifierCategory.FUNCTION,
                                file_path=str(file_path),
                                line_number=line_num,
                            )
                        )
                    else:
                        convention = self._classify_convention(identifier)
                        patterns.append(
                            ConventionOccurrence(
                                convention_type=convention,
                                identifier=identifier,
                                category=IdentifierCategory.PRIVATE,
                                file_path=str(file_path),
                                line_number=line_num,
                            )
                        )

            # Classes
            match = self.PYTHON_CLASS_PATTERN.match(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.CLASS,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

            # Variables/Constants (at module level, not indented)
            if not line.startswith(" ") and not line.startswith("\t"):
                match = self.PYTHON_VARIABLE_PATTERN.match(line)
                if match:
                    identifier = match.group(1)
                    if identifier and len(identifier) > 1:  # Skip single letters
                        convention = self._classify_convention(identifier)
                        # Determine if it's a constant (UPPER_SNAKE_CASE)
                        category = (
                            IdentifierCategory.CONSTANT
                            if convention == NamingConventionType.UPPER_SNAKE_CASE
                            else IdentifierCategory.VARIABLE
                        )
                        patterns.append(
                            ConventionOccurrence(
                                convention_type=convention,
                                identifier=identifier,
                                category=category,
                                file_path=str(file_path),
                                line_number=line_num,
                            )
                        )

        return patterns

    def _extract_javascript_patterns(
        self,
        content: str,
        file_path: Path,
    ) -> List[ConventionOccurrence]:
        """Extract patterns from JavaScript/TypeScript file."""
        patterns: List[ConventionOccurrence] = []

        for line_num, line in enumerate(content.split("\n"), 1):
            # Functions
            match = self.JS_FUNCTION_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1 and not identifier.startswith("_"):
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.FUNCTION,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

            # Variables/Constants
            match = self.JS_VAR_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    # Determine if it's a constant (UPPER_SNAKE_CASE)
                    category = (
                        IdentifierCategory.CONSTANT
                        if convention == NamingConventionType.UPPER_SNAKE_CASE
                        else IdentifierCategory.VARIABLE
                    )
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=category,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

            # Classes
            match = self.JS_CLASS_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.CLASS,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

        return patterns

    def _extract_go_patterns(
        self,
        content: str,
        file_path: Path,
    ) -> List[ConventionOccurrence]:
        """Extract patterns from Go file."""
        patterns: List[ConventionOccurrence] = []

        for line_num, line in enumerate(content.split("\n"), 1):
            # Functions
            match = self.GO_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    is_exported = identifier[0].isupper()
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.FUNCTION,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

            # Structs
            match = self.GO_STRUCT_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.CLASS,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

        return patterns

    def _extract_java_patterns(
        self,
        content: str,
        file_path: Path,
    ) -> List[ConventionOccurrence]:
        """Extract patterns from Java file."""
        patterns: List[ConventionOccurrence] = []

        for line_num, line in enumerate(content.split("\n"), 1):
            # Classes
            match = self.JAVA_CLASS_PATTERN.search(line)
            if match:
                identifier = match.group(1)
                # FIX MEDIUM #5: Skip single-letter identifiers
                if identifier and len(identifier) > 1:
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.CLASS,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

        return patterns

    def _extract_generic_patterns(
        self,
        content: str,
        file_path: Path,
    ) -> List[ConventionOccurrence]:
        """Generic pattern extraction for unsupported languages."""
        patterns: List[ConventionOccurrence] = []

        # Simple heuristic: find identifiers in variable assignments
        var_pattern = re.compile(r"^([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[=:]")

        for line_num, line in enumerate(content.split("\n"), 1):
            match = var_pattern.match(line.strip())
            if match:
                identifier = match.group(1)
                if identifier and len(identifier) > 1:  # Skip single letters
                    convention = self._classify_convention(identifier)
                    patterns.append(
                        ConventionOccurrence(
                            convention_type=convention,
                            identifier=identifier,
                            category=IdentifierCategory.VARIABLE,
                            file_path=str(file_path),
                            line_number=line_num,
                        )
                    )

        return patterns

    # ========================================================================
    # Convention Classification
    # ========================================================================

    def _classify_convention(self, identifier: str) -> NamingConventionType:
        """
        Classify naming convention for an identifier.

        Args:
            identifier: Identifier name to classify

        Returns:
            NamingConventionType classification
        """
        if not identifier:
            return NamingConventionType.UNKNOWN

        # Check for UPPER_SNAKE_CASE
        if self.UPPER_SNAKE_CASE_PATTERN.match(identifier):
            return NamingConventionType.UPPER_SNAKE_CASE

        # Check for PascalCase
        if self.PASCAL_CASE_PATTERN.match(identifier):
            return NamingConventionType.PASCAL_CASE

        # Check for camelCase
        if self.CAMEL_CASE_PATTERN.match(identifier):
            return NamingConventionType.CAMEL_CASE

        # Check for snake_case
        if self.SNAKE_CASE_PATTERN.match(identifier):
            return NamingConventionType.SNAKE_CASE

        # Check for kebab-case
        if self.KEBAB_CASE_PATTERN.match(identifier):
            return NamingConventionType.KEBAB_CASE

        return NamingConventionType.UNKNOWN

    # ========================================================================
    # Result Creation
    # ========================================================================

    def _create_result_from_occurrences(
        self,
        occurrences: List[ConventionOccurrence],
        files_analyzed: int,
        total_files: int,
    ) -> NamingConventionResult:
        """Create result from collected occurrences."""
        # Categorize by type
        function_occurrences = [o for o in occurrences if o.category == IdentifierCategory.FUNCTION]
        class_occurrences = [o for o in occurrences if o.category == IdentifierCategory.CLASS]
        variable_occurrences = [o for o in occurrences if o.category == IdentifierCategory.VARIABLE]
        # FIX HIGH #2: Use category field, not convention_type (AC4 context-aware detection)
        constant_occurrences = [o for o in occurrences if o.category == IdentifierCategory.CONSTANT]

        # Compute frequencies
        overall_frequencies = self._compute_frequencies(occurrences)
        function_frequencies = self._compute_frequencies(function_occurrences)
        class_frequencies = self._compute_frequencies(class_occurrences)
        variable_frequencies = self._compute_frequencies(variable_occurrences)
        constant_frequencies = self._compute_frequencies(constant_occurrences)

        # Get dominant convention
        overall_dominant = (
            overall_frequencies[0].convention_type
            if overall_frequencies
            else NamingConventionType.UNKNOWN
        )

        # Compute confidence
        consistency = self._compute_consistency(occurrences) if occurrences else 0.0
        overall_confidence = self._calculate_confidence(len(occurrences), consistency)

        coverage_percentage = (files_analyzed / total_files * 100) if total_files > 0 else 0.0

        return NamingConventionResult(
            overall_dominant_convention=overall_dominant,
            overall_conventions=overall_frequencies,
            overall_confidence=overall_confidence,
            function_conventions=function_frequencies,
            class_conventions=class_frequencies,
            variable_conventions=variable_frequencies,
            constant_conventions=constant_frequencies,
            sample_size=len(occurrences),
            files_analyzed=files_analyzed,
            identifiers_analyzed=len(occurrences),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=self.NAMING_VERSION,
            coverage_percentage=coverage_percentage,
            consistency_score=consistency,
        )

    def _create_empty_result(self, files_analyzed: int, files_result: ProjectIndicatorResult) -> NamingConventionResult:
        """Create empty result when no identifiers found."""
        total_files = len(files_result.files_found) if files_result.files_found else 0

        return NamingConventionResult(
            overall_dominant_convention=NamingConventionType.UNKNOWN,
            overall_conventions=[],
            overall_confidence=0.0,
            function_conventions=[],
            class_conventions=[],
            variable_conventions=[],
            constant_conventions=[],
            sample_size=0,
            files_analyzed=files_analyzed,
            identifiers_analyzed=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=self.NAMING_VERSION,
            coverage_percentage=0.0,
            consistency_score=0.0,
        )

    def _compute_frequencies(self, occurrences: List[ConventionOccurrence]) -> List[ConventionFrequency]:
        """Compute convention frequencies."""
        if not occurrences:
            return []

        # Count occurrences
        counts: Dict[NamingConventionType, int] = {}
        examples: Dict[NamingConventionType, Set[str]] = {}

        for occurrence in occurrences:
            if occurrence.convention_type not in counts:
                counts[occurrence.convention_type] = 0
                examples[occurrence.convention_type] = set()

            counts[occurrence.convention_type] += 1
            examples[occurrence.convention_type].add(occurrence.identifier)

        # Compute percentages
        total = sum(counts.values())
        frequencies: List[ConventionFrequency] = []

        for convention_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0.0
            confidence = min(percentage / 100.0, 1.0)  # Confidence based on percentage

            frequencies.append(
                ConventionFrequency(
                    convention_type=convention_type,
                    count=count,
                    percentage=percentage,
                    confidence=confidence,
                    examples=list(examples[convention_type])[:5],  # Top 5 examples
                )
            )

        return frequencies

    def _compute_consistency(self, occurrences: List[ConventionOccurrence]) -> float:
        """
        Compute consistency score (0.0-1.0).

        Higher score means naming conventions are more consistent.
        """
        if not occurrences:
            return 0.0

        # Count occurrences
        total = len(occurrences)
        frequencies = self._compute_frequencies(occurrences)

        if not frequencies:
            return 0.0

        # Consistency is based on how dominant the top convention is
        top_percentage = frequencies[0].percentage if frequencies else 0.0
        consistency = top_percentage / 100.0

        return min(consistency, 1.0)

    def _calculate_confidence(self, sample_size: int, consistency_percentage: float) -> float:
        """
        Calculate confidence score (0.0-1.0).

        Args:
            sample_size: Number of identifiers analyzed
            consistency_percentage: Consistency score (0.0-1.0)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Larger sample = higher confidence (but not capped at 100)
        # Use logarithmic scaling: log(sample_size + 1) / log(101) to reach ~1.0 at 100
        if sample_size > 0:
            import math
            sample_score = min(math.log(sample_size + 1) / math.log(101), 1.0) * 0.5
        else:
            sample_score = 0.0

        # More consistency = higher confidence
        consistency_score = consistency_percentage * 0.5

        confidence = sample_score + consistency_score
        return min(confidence, 1.0)

    # ========================================================================
    # Timeout Management
    # ========================================================================

    def _is_timeout(self) -> bool:
        """
        Check if timeout has been exceeded.

        FIX MEDIUM #7: Use PerformanceTracker if available for consistent timeout checking.
        """
        if self.performance_tracker:
            return self.performance_tracker.check_soft_timeout(self.timeout_sec)
        else:
            elapsed = time.perf_counter() - self.start_time
            return elapsed > self.timeout_sec
