"""
Documentation style detection module.
Identifies documentation/docstring styles used in projects.
"""

import re
import os
import time
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

from src.prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from src.prompt_enhancement.pipeline.project_files import ProjectIndicatorResult


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

    def __init__(self):
        """Initialize detector"""
        self.timeout = 2.0  # 2-second budget

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
        start_time = time.time()

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
            if time.time() - start_time > self.timeout:
                break

            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

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

        # Limit to 100 representative files
        return source_files[:100]

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
        """Calculate documentation coverage metrics"""
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
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Count functions/classes
                func_count = len(func_pattern.findall(content))
                total_count += func_count

                # Count documented items
                if class_pattern:
                    class_count = len(class_pattern.findall(content))
                    total_count += class_count

                doc_count = len(doc_pattern.findall(content))
                documented_count += doc_count

            except (IOError, OSError):
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
