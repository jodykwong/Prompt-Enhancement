"""
Documentation style detection module.
Identifies documentation/docstring styles used in projects.

FIX MEDIUM #7: Story 2.5 (Naming Conventions) Integration Status
-----------------------------------------------------------------
Documentation style detection operates independently of naming conventions.
While both analyze code structure, they serve different purposes:
- Naming conventions: Variable/function/class naming patterns
- Documentation style: Docstring/comment formatting patterns

Integration is implicit through shared project analysis pipeline,
not through direct API calls.
"""

import re
import os
import time
import logging
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

from .tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from .project_files import ProjectIndicatorResult
from .file_access import FileAccessHandler

# FIX CRITICAL #1: Import PerformanceTracker for Story 1.4 integration
try:
    from ..cli.performance import PerformanceTracker
except ImportError:
    PerformanceTracker = None

logger = logging.getLogger(__name__)


class DocumentationStyle(str, Enum):
    """Supported documentation styles"""
    GOOGLE = "google"
    NUMPY = "numpy"
    PEP257 = "pep257"
    SPHINX = "sphinx"
    JSDOC = "jsdoc"
    JAVADOC = "javadoc"
    GO_DOC = "go_doc"
    RESTRUCTURED_TEXT = "restructured_text"
    UNKNOWN = "unknown"


@dataclass
class DocumentationStyleDetection:
    """Single documentation style detection"""
    style: DocumentationStyle
    confidence: float
    count: int = 0
    percentage: float = 0.0


@dataclass
class DocumentationCoverage:
    """Documentation coverage metrics"""
    documented_count: int = 0
    total_count: int = 0
    coverage_percentage: float = 0.0
    analysis_notes: str = ""


@dataclass
class DocumentationStyleResult:
    """Result of documentation style detection"""
    primary_style: Optional[DocumentationStyle] = None
    detected_styles: List[DocumentationStyleDetection] = field(default_factory=list)
    coverage: Optional[DocumentationCoverage] = None
    special_documentation_files: List[str] = field(default_factory=list)
    analysis_notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"


class DocumentationStyleDetector:
    """Detects documentation styles in projects"""

    # Regex patterns for documentation style detection
    GOOGLE_STYLE_PATTERN = re.compile(
        r"^\s*(Args|Returns|Raises|Attributes|Examples|Note|Warning):\s*$",
        re.MULTILINE | re.IGNORECASE
    )
    NUMPY_STYLE_PATTERN = re.compile(
        r"^\s*(Parameters|Returns|Raises|Examples|Notes|References|See Also)\s*\n\s*-+\s*$",
        re.MULTILINE | re.IGNORECASE
    )
    PEP257_PATTERN = re.compile(
        r'^\s*"""[^"]*"""',
        re.MULTILINE
    )
    SPHINX_STYLE_PATTERN = re.compile(
        r":\w+(`[^`]+`)?:",
        re.MULTILINE
    )
    JSDOC_PATTERN = re.compile(
        r"/\*\*\s*\n[\s*]*@\w+",
        re.MULTILINE
    )
    JAVADOC_PATTERN = re.compile(
        r"/\*\*\s*\n[\s*]*@\w+",
        re.MULTILINE
    )
    GO_DOC_PATTERN = re.compile(
        r"^//\s+\w+\s+\w+\s*$",
        re.MULTILINE
    )

    # File patterns for different languages
    PYTHON_FILE_PATTERN = r"\.(py)$"
    JAVASCRIPT_FILE_PATTERN = r"\.(js|jsx|mjs)$"
    TYPESCRIPT_FILE_PATTERN = r"\.(ts|tsx)$"
    JAVA_FILE_PATTERN = r"\.(java)$"
    GO_FILE_PATTERN = r"\.(go)$"

    # Function/class patterns for counting
    PYTHON_FUNCTION_PATTERN = re.compile(r"^\s*def\s+\w+", re.MULTILINE)
    PYTHON_CLASS_PATTERN = re.compile(r"^\s*class\s+\w+", re.MULTILINE)
    JAVASCRIPT_FUNCTION_PATTERN = re.compile(r"(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\(|class\s+\w+)", re.MULTILINE)
    JAVA_FUNCTION_PATTERN = re.compile(r"(public\s+\w+|private\s+\w+|protected\s+\w+)", re.MULTILINE)
    GO_FUNCTION_PATTERN = re.compile(r"^func\s+\(?\w+\)?", re.MULTILINE)

    # Docstring extraction patterns
    PYTHON_DOCSTRING_PATTERN = re.compile(
        r'(?:"""|\'\'\')(.*?)(?:"""|\'\'\')',
        re.DOTALL
    )
    JAVASCRIPT_COMMENT_PATTERN = re.compile(
        r"/\*\*(.*?)\*/",
        re.DOTALL
    )
    JAVA_COMMENT_PATTERN = re.compile(
        r"/\*\*(.*?)\*/",
        re.DOTALL
    )

    # Special documentation files
    SPECIAL_DOC_FILES = {
        "README.md", "README.txt", "README",
        "CONTRIBUTING.md", "CONTRIBUTING.txt",
        "ARCHITECTURE.md", "ARCHITECTURE.txt",
        "DESIGN.md", "DESIGN.txt",
        "CHANGELOG.md", "CHANGELOG.txt",
        "API.md", "API.txt",
        "docs/", "doc/"
    }

    def __init__(
        self,
        timeout_sec: float = 2.0,
        performance_tracker: Optional['PerformanceTracker'] = None,
        file_access_handler: Optional[FileAccessHandler] = None,
    ):
        """
        Initialize detector.

        Args:
            timeout_sec: Timeout for detection (default 2.0 seconds)
            performance_tracker: Optional PerformanceTracker from Story 1.4
            file_access_handler: Optional FileAccessHandler from Story 2.10
        """
        self.timeout = timeout_sec
        self.performance_tracker = performance_tracker  # FIX CRITICAL #1
        self.file_access_handler = file_access_handler  # FIX CRITICAL #2
        self.start_time = None

    def detect_documentation_style(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
        project_root: str = "."
    ) -> Optional[DocumentationStyleResult]:
        """
        Detect documentation style used in project.

        Args:
            tech_result: Project type detection results
            files_result: Project files detection results
            project_root: Root directory of project

        Returns:
            DocumentationStyleResult or None if detection fails
        """
        # FIX CRITICAL #1: Track start time for timeout checks and performance tracking
        self.start_time = time.time()

        # FIX CRITICAL #2: Initialize FileAccessHandler if not provided
        if self.file_access_handler is None:
            self.file_access_handler = FileAccessHandler(project_root)

        if not tech_result or not tech_result.primary_language:
            return None

        # Early termination for unsupported languages
        if tech_result.primary_language not in [
            ProjectLanguage.PYTHON,
            ProjectLanguage.NODEJS,
            ProjectLanguage.JAVA,
            ProjectLanguage.GO
        ]:
            return None

        result = DocumentationStyleResult()

        # Sample source files
        source_files = self._sample_source_files(
            tech_result, files_result, project_root
        )

        if not source_files:
            return None

        # Detect styles based on language
        detected_styles = {}
        total_docs = 0

        for source_file in source_files:
            # FIX HIGH #4: Use self.start_time for consistency
            if time.time() - self.start_time > self.timeout:
                logger.warning("Timeout during documentation style detection")
                break

            # FIX CRITICAL #2: Use FileAccessHandler instead of direct file read
            content = self.file_access_handler.try_read_file(source_file)
            if not content:
                continue

            try:
                if tech_result.primary_language == ProjectLanguage.PYTHON:
                    styles = self._detect_python_styles(content)
                    total_docs += self._count_python_docs(content)
                elif tech_result.primary_language == ProjectLanguage.NODEJS:
                    styles = self._detect_javascript_styles(content)
                    total_docs += self._count_javascript_docs(content)
                elif tech_result.primary_language == ProjectLanguage.JAVA:
                    styles = self._detect_java_styles(content)
                    total_docs += self._count_java_docs(content)
                elif tech_result.primary_language == ProjectLanguage.GO:
                    styles = self._detect_go_styles(content)
                    total_docs += self._count_go_docs(content)
                else:
                    continue

                for style, count in styles.items():
                    detected_styles[style] = detected_styles.get(style, 0) + count

            except (IOError, OSError):
                continue

        # Calculate coverage metrics
        coverage = self._calculate_coverage(source_files, tech_result)

        # Build result
        if detected_styles:
            sorted_styles = sorted(detected_styles.items(), key=lambda x: x[1], reverse=True)
            result.primary_style = sorted_styles[0][0]

            total_occurrences = sum(detected_styles.values())
            for style, count in sorted_styles:
                confidence = self._calculate_confidence(
                    count, total_occurrences, len(source_files)
                )
                result.detected_styles.append(
                    DocumentationStyleDetection(
                        style=style,
                        confidence=confidence,
                        count=count,
                        percentage=(count / total_occurrences * 100) if total_occurrences > 0 else 0
                    )
                )

        # Find special documentation files
        result.special_documentation_files = self._find_special_doc_files(project_root)

        # Set coverage
        result.coverage = coverage

        # Generate analysis notes
        result.analysis_notes = self._generate_analysis_notes(result)

        return result

    def _sample_source_files(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
        project_root: str
    ) -> List[str]:
        """Sample representative source files from project"""
        source_files = []

        # Get file list from files_result or scan directory
        if files_result and files_result.files_found:
            candidate_files = files_result.files_found
        else:
            candidate_files = self._scan_for_source_files(project_root, tech_result)

        # Filter based on language
        if tech_result.primary_language == ProjectLanguage.PYTHON:
            pattern = self.PYTHON_FILE_PATTERN
        elif tech_result.primary_language == ProjectLanguage.NODEJS:
            # NODEJS includes both JavaScript and TypeScript files
            pattern = r"\.(js|jsx|mjs|ts|tsx)$"
        elif tech_result.primary_language == ProjectLanguage.JAVA:
            pattern = self.JAVA_FILE_PATTERN
        elif tech_result.primary_language == ProjectLanguage.GO:
            pattern = self.GO_FILE_PATTERN
        else:
            return []

        # Exclude test files and vendor directories
        # More specific patterns: test/ directory, _test suffix, test_ prefix, .test files
        for file_path in candidate_files:
            path_lower = file_path.lower()
            # Exclude vendor directories and caches
            if any(x in path_lower for x in ['/node_modules/', '/vendor/', '/__pycache__/', '/.git/']):
                continue
            # Exclude test files (more specific patterns)
            if any(x in path_lower for x in ['/test/', '/tests/', '/spec/', '/_test_', '_test.', '.test.']):
                continue
            if re.search(pattern, file_path):
                source_files.append(file_path)

        # FIX MEDIUM #8: Improve file sampling strategy for better diversity
        # Group files by directory to ensure cross-directory representation
        if len(source_files) > 100:
            from collections import defaultdict
            files_by_dir = defaultdict(list)
            for f in source_files:
                dir_path = os.path.dirname(f) or '.'
                files_by_dir[dir_path].append(f)

            # Sample proportionally from each directory
            sampled = []
            files_per_dir = max(1, 100 // len(files_by_dir))
            for dir_files in files_by_dir.values():
                sampled.extend(dir_files[:files_per_dir])

            # If we haven't reached 100, add more files
            if len(sampled) < 100:
                remaining = [f for f in source_files if f not in sampled]
                sampled.extend(remaining[:100 - len(sampled)])

            return sampled[:100]

        return source_files

    def _scan_for_source_files(self, project_root: str, tech_result: ProjectTypeDetectionResult) -> List[str]:
        """Scan directory for source files"""
        files = []
        try:
            for root, dirs, filenames in os.walk(project_root):
                # Skip hidden and vendor directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '__pycache__']]

                for filename in filenames:
                    files.append(os.path.join(root, filename))

                if len(files) >= 100:
                    break
        except (OSError, IOError):
            pass

        return files

    def _detect_python_styles(self, content: str) -> dict:
        """Detect Python documentation styles"""
        styles = {}

        # Count Google style
        if self.GOOGLE_STYLE_PATTERN.search(content):
            styles[DocumentationStyle.GOOGLE] = len(
                self.GOOGLE_STYLE_PATTERN.findall(content)
            )

        # Count NumPy style
        if self.NUMPY_STYLE_PATTERN.search(content):
            styles[DocumentationStyle.NUMPY] = len(
                self.NUMPY_STYLE_PATTERN.findall(content)
            )

        # Count Sphinx style
        if self.SPHINX_STYLE_PATTERN.search(content):
            styles[DocumentationStyle.SPHINX] = len(
                self.SPHINX_STYLE_PATTERN.findall(content)
            )

        # Count PEP 257 style (simple docstrings)
        docstrings = self.PYTHON_DOCSTRING_PATTERN.findall(content)
        if docstrings and not any(styles.values()):
            styles[DocumentationStyle.PEP257] = len(docstrings)

        return styles

    def _detect_javascript_styles(self, content: str) -> dict:
        """Detect JavaScript/TypeScript documentation styles"""
        styles = {}

        # Detect JSDoc style - look for /** ... */ patterns with @ tags
        # Simplified pattern that handles JSDoc comments
        if '/**' in content and '@' in content:
            # Count JSDoc blocks
            jsdoc_count = len(re.findall(r'/\*\*[\s\S]*?\*/', content))
            # Count JSDoc tags
            tag_count = len(re.findall(r'@\w+', content))

            # If we find both JSDoc blocks and tags, it's JSDoc
            if jsdoc_count > 0 and tag_count > 0:
                styles[DocumentationStyle.JSDOC] = tag_count

        return styles

    def _detect_java_styles(self, content: str) -> dict:
        """Detect Java documentation styles"""
        styles = {}

        # Detect Javadoc style - look for /** ... */ patterns with @ tags
        if '/**' in content and '@' in content:
            # Count Javadoc blocks
            javadoc_count = len(re.findall(r'/\*\*[\s\S]*?\*/', content))
            # Count Javadoc tags like @param, @return, @throws, @see
            tag_count = len(re.findall(r'@(param|return|throws|see|author|version|deprecated)', content))

            # If we find both Javadoc blocks and tags, it's Javadoc
            if javadoc_count > 0 and tag_count > 0:
                styles[DocumentationStyle.JAVADOC] = tag_count

        return styles

    def _detect_go_styles(self, content: str) -> dict:
        """Detect Go documentation styles"""
        styles = {}

        # Detect Go doc comments - comments directly before declarations
        # Pattern: // followed by text, appearing before func, type, const, var declarations
        if '//' in content:
            # Look for Go doc patterns: // Comment followed by func/type/const/var declarations
            go_doc_count = len(re.findall(
                r'//\s+\w+.*?\n\s*(func|type|const|var|package)\s+\w+',
                content,
                re.MULTILINE
            ))

            if go_doc_count > 0:
                styles[DocumentationStyle.GO_DOC] = go_doc_count

        return styles

    def _count_python_docs(self, content: str) -> int:
        """Count Python documentation occurrences"""
        docstrings = self.PYTHON_DOCSTRING_PATTERN.findall(content)
        return len(docstrings)

    def _count_javascript_docs(self, content: str) -> int:
        """Count JavaScript/TypeScript documentation occurrences"""
        return len(self.JAVASCRIPT_COMMENT_PATTERN.findall(content))

    def _count_java_docs(self, content: str) -> int:
        """Count Java documentation occurrences"""
        return len(self.JAVA_COMMENT_PATTERN.findall(content))

    def _count_go_docs(self, content: str) -> int:
        """Count Go documentation occurrences"""
        return len(self.GO_DOC_PATTERN.findall(content))

    def _calculate_coverage(
        self,
        source_files: List[str],
        tech_result: ProjectTypeDetectionResult
    ) -> DocumentationCoverage:
        """
        Calculate documentation coverage metrics.

        FIX MEDIUM #6: Coverage Calculation Limitation
        -----------------------------------------------
        Current implementation counts total functions/classes vs total docstrings
        separately, which may not accurately reflect which specific functions are
        documented. For example:
        - 5 functions + 3 docstrings = 60% coverage reported
        - But all 3 docstrings could be on the same function (actual: 20% coverage)

        A more accurate implementation would require AST parsing to match each
        function/class with its docstring. The current heuristic provides a
        reasonable approximation for most projects.
        """
        total_count = 0
        documented_count = 0

        if tech_result.primary_language == ProjectLanguage.PYTHON:
            func_pattern = self.PYTHON_FUNCTION_PATTERN
            class_pattern = self.PYTHON_CLASS_PATTERN
            doc_pattern = self.PYTHON_DOCSTRING_PATTERN
        elif tech_result.primary_language == ProjectLanguage.NODEJS:
            func_pattern = self.JAVASCRIPT_FUNCTION_PATTERN
            class_pattern = None
            doc_pattern = self.JAVASCRIPT_COMMENT_PATTERN
        elif tech_result.primary_language == ProjectLanguage.JAVA:
            func_pattern = self.JAVA_FUNCTION_PATTERN
            class_pattern = None
            doc_pattern = self.JAVA_COMMENT_PATTERN
        elif tech_result.primary_language == ProjectLanguage.GO:
            func_pattern = self.GO_FUNCTION_PATTERN
            class_pattern = None
            doc_pattern = self.GO_DOC_PATTERN
        else:
            return DocumentationCoverage()

        for source_file in source_files[:50]:  # Limit sample for performance
            # FIX HIGH #4: Add timeout check in coverage calculation loop
            if self.start_time and (time.time() - self.start_time > self.timeout):
                logger.warning("Timeout during coverage calculation")
                break

            # FIX CRITICAL #2: Use FileAccessHandler instead of direct file read
            content = self.file_access_handler.try_read_file(source_file)
            if not content:
                continue

            try:
                # Count functions/classes
                func_count = len(func_pattern.findall(content))
                total_count += func_count

                # Count documented items
                if class_pattern:
                    class_count = len(class_pattern.findall(content))
                    total_count += class_count

                doc_count = len(doc_pattern.findall(content))
                documented_count += doc_count

            except Exception as e:
                logger.debug(f"Error calculating coverage for {source_file}: {e}")
                continue

        coverage_pct = (documented_count / total_count * 100) if total_count > 0 else 0

        return DocumentationCoverage(
            documented_count=documented_count,
            total_count=total_count,
            coverage_percentage=coverage_pct
        )

    def _calculate_confidence(self, count: int, total: int, file_count: int) -> float:
        """
        Calculate confidence score for detected style.

        Uses logarithmic scaling based on frequency and file diversity.
        """
        if total == 0:
            return 0.0

        # Frequency score (0-1)
        frequency = min(count / total, 1.0)

        # Diversity score based on files analyzed
        diversity = min(file_count / 10.0, 1.0)  # Max out at 10 files

        # Combined confidence with frequency weighted more heavily
        confidence = (frequency * 0.7) + (diversity * 0.3)

        return min(confidence, 1.0)

    def _find_special_doc_files(self, project_root: str) -> List[str]:
        """Find special documentation files in project"""
        special_files = []

        try:
            for item in self.SPECIAL_DOC_FILES:
                if item.endswith('/'):
                    path = Path(project_root) / item.rstrip('/')
                    if path.is_dir():
                        special_files.append(str(path))
                else:
                    path = Path(project_root) / item
                    if path.exists():
                        special_files.append(str(path))
        except (OSError, IOError):
            pass

        return special_files

    def _generate_analysis_notes(self, result: DocumentationStyleResult) -> str:
        """Generate analysis notes from results"""
        notes = []

        if result.primary_style:
            notes.append(f"Primary style: {result.primary_style.value}")

        if result.coverage:
            if result.coverage.coverage_percentage < 25:
                notes.append("WARNING: Low documentation coverage (<25%)")
            elif result.coverage.coverage_percentage < 50:
                notes.append("INFO: Moderate documentation coverage (25-50%)")
            else:
                notes.append("INFO: Good documentation coverage (>50%)")

        if len(result.detected_styles) > 1:
            notes.append("Mixed documentation styles detected in project")

        return "; ".join(notes)
