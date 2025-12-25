"""
Tech Stack Detector - Automatically detect project type and language.

Identifies project programming language by scanning for filesystem markers
(e.g., requirements.txt, package.json, go.mod, Cargo.toml, etc.)

This module implements Story 2.1: Detect Project Type from Filesystem Markers.
"""

import os
import json
import re
import time
import logging
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures (Task 2.1.1)
# ============================================================================


class ProjectLanguage(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"


@dataclass
class ProjectTypeDetectionResult:
    """Result of project type detection."""

    primary_language: ProjectLanguage
    version: Optional[str]
    confidence: float
    markers_found: List[str]
    secondary_languages: List[ProjectLanguage]

    # Note: Confidence validation removed as _calculate_confidence() already clamps to [0.0, 1.0]
    # Validation here was unreachable dead code


# ============================================================================
# ProjectTypeDetector Class
# ============================================================================


class ProjectTypeDetector:
    """
    Detects project type and programming language from filesystem markers.

    Scans project root directory for language-specific marker files and
    extracts version information from configuration files.

    Attributes:
        project_root: Root directory to scan for markers
        PYTHON_MARKERS: Dict of Python marker files and metadata
        NODE_MARKERS: Dict of Node.js marker files and metadata
        GO_MARKERS: Dict of Go marker files and metadata
        RUST_MARKERS: Dict of Rust marker files and metadata
        JAVA_MARKERS: Dict of Java marker files and metadata
        CSHARP_MARKERS: Dict of C# marker files and metadata
    """

    # Marker file definitions with priority and metadata extraction flag
    # Higher priority = preferred in multi-language detection
    PYTHON_MARKERS = {
        "requirements.txt": {"priority": 10, "metadata": False},
        "pyproject.toml": {"priority": 9, "metadata": True},
        "setup.py": {"priority": 8, "metadata": True},
        "Pipfile": {"priority": 7, "metadata": True},
        "poetry.lock": {"priority": 5, "metadata": False},
    }

    NODE_MARKERS = {
        "package.json": {"priority": 10, "metadata": True},
        "package-lock.json": {"priority": 9, "metadata": False},
        "yarn.lock": {"priority": 9, "metadata": False},
        "pnpm-lock.yaml": {"priority": 8, "metadata": False},
    }

    GO_MARKERS = {
        "go.mod": {"priority": 10, "metadata": True},
        "go.sum": {"priority": 8, "metadata": False},
    }

    RUST_MARKERS = {
        "Cargo.toml": {"priority": 10, "metadata": True},
        "Cargo.lock": {"priority": 8, "metadata": False},
    }

    JAVA_MARKERS = {
        "pom.xml": {"priority": 10, "metadata": True},
        "build.gradle": {"priority": 10, "metadata": True},
        "settings.xml": {"priority": 8, "metadata": False},
        "gradle.properties": {"priority": 7, "metadata": False},
    }

    # C# markers - note .csproj and .sln are file extensions, not exact names
    CSHARP_MARKERS = {
        "packages.config": {"priority": 8, "metadata": False},
    }
    CSHARP_EXTENSIONS = [".csproj", ".sln"]  # Extensions to check separately

    # Directories to skip during scanning
    SKIP_DIRS = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "venv",
        "env",
        ".env",
        "build",
        "dist",
        ".tox",
    }

    # Timeout for detection (2-second budget from Story 1.4)
    DETECTION_TIMEOUT_SECONDS = 2.0

    def __init__(
        self, project_root: Optional[str] = None, follow_symlinks: bool = False
    ):
        """
        Initialize ProjectTypeDetector.

        Args:
            project_root: Root directory to scan. Defaults to current directory.
            follow_symlinks: Whether to follow symbolic links (default: False for safety).
        """
        self.project_root = Path(project_root or os.getcwd())
        self.follow_symlinks = follow_symlinks
        self._start_time = None  # Will be set when detect_project_type() is called

    def detect_project_type(self) -> Optional[ProjectTypeDetectionResult]:
        """
        Detect project type and language.

        Scans project root for language marker files, extracts version info,
        calculates confidence score, and handles mixed-language projects.

        Returns:
            ProjectTypeDetectionResult with detected language, version, and confidence,
            or None if no language detected with meaningful confidence.

        AC Coverage:
            - AC1: Python detection from requirements.txt, pyproject.toml, setup.py
            - AC2: Node.js detection from package.json
            - AC3: Go detection from go.mod
            - AC4: Rust detection from Cargo.toml
            - AC5: Java detection from pom.xml, build.gradle
            - AC6: Mixed language handling with primary/secondary identification
        """
        # Reset start time for accurate timeout tracking
        self._start_time = time.perf_counter()

        try:
            # Scan root directory for all markers (Task 2.1.2)
            found_markers = self._find_marker_files()

            if not found_markers:
                logger.debug(f"No markers found in {self.project_root}")
                return None

            # Classify markers by language (Task 2.1.3)
            language_markers = self._classify_markers(found_markers)

            if not language_markers:
                return None

            # Determine primary and secondary languages (AC6 - Task 2.1.3)
            primary_lang = self._determine_primary_language(language_markers)
            secondary_langs = self._determine_secondary_languages(
                language_markers, primary_lang
            )

            # Extract version from config files (Task 2.1.4)
            version = self._extract_version(primary_lang, found_markers)

            # Calculate confidence score (Task 2.1.3)
            confidence = self._calculate_confidence(
                primary_lang, found_markers, version, language_markers
            )

            # Get list of primary language markers
            primary_markers = [
                m
                for m in found_markers
                if m in self._get_markers_for_language(primary_lang)
            ]

            return ProjectTypeDetectionResult(
                primary_language=primary_lang,
                version=version,
                confidence=confidence,
                markers_found=primary_markers,
                secondary_languages=secondary_langs,
            )

        except Exception as e:
            logger.error(f"Error detecting project type: {e}", exc_info=True)
            return None

    # ========================================================================
    # Task 2.1.2: Marker File Scanning
    # ========================================================================

    def _find_marker_files(self) -> List[str]:
        """
        Find all marker files in project root.

        Scans root directory (depth=0 only, no recursion) for language marker files.
        Skips hidden directories and common large directories.
        Handles permission denied gracefully.

        Returns:
            List of marker filenames found in project root.
        """
        found = []

        if not self.project_root.exists():
            logger.warning(f"Project root does not exist: {self.project_root}")
            return found

        if not self.project_root.is_dir():
            logger.warning(f"Project root is not a directory: {self.project_root}")
            return found

        # Get all marker filenames to check
        all_markers = set()
        for markers in [
            self.PYTHON_MARKERS,
            self.NODE_MARKERS,
            self.GO_MARKERS,
            self.RUST_MARKERS,
            self.JAVA_MARKERS,
            self.CSHARP_MARKERS,
        ]:
            all_markers.update(markers.keys())

        # Check for exact filename matches (no recursion)
        try:
            for item in self.project_root.iterdir():
                if self._is_timeout():
                    logger.warning("Detection timeout - stopping scan")
                    break

                # Skip hidden items (except .csproj, .sln files)
                if item.name.startswith("."):
                    continue
                if item.name in self.SKIP_DIRS:
                    continue

                # Skip symbolic links if not following them (prevents loops)
                if not self.follow_symlinks and item.is_symlink():
                    logger.debug(f"Skipping symlink: {item.name}")
                    continue

                # Check if item matches any marker (exact name match)
                if item.name in all_markers:
                    found.append(item.name)
                # Also check for C# extension-based markers
                elif any(item.name.endswith(ext) for ext in self.CSHARP_EXTENSIONS):
                    found.append(item.name)

        except PermissionError as e:
            logger.warning(f"Permission denied scanning {self.project_root}: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")

        return found

    def _check_marker_exists(self, marker_filename: str) -> bool:
        """
        Check if marker file exists in project root.

        Args:
            marker_filename: Name of marker file to check.

        Returns:
            True if marker file exists, False otherwise.
        """
        marker_path = self.project_root / marker_filename
        try:
            return marker_path.exists() and marker_path.is_file()
        except PermissionError:
            logger.debug(f"Permission denied checking marker: {marker_filename}")
            return False

    # ========================================================================
    # Task 2.1.3: Language Detection and Classification
    # ========================================================================

    def _classify_markers(
        self, found_markers: List[str]
    ) -> Dict[ProjectLanguage, List[str]]:
        """
        Classify found markers by language.

        Args:
            found_markers: List of marker filenames found.

        Returns:
            Dict mapping ProjectLanguage to list of markers for that language.
        """
        language_markers: Dict[ProjectLanguage, List[str]] = {}

        for marker in found_markers:
            if marker in self.PYTHON_MARKERS:
                if ProjectLanguage.PYTHON not in language_markers:
                    language_markers[ProjectLanguage.PYTHON] = []
                language_markers[ProjectLanguage.PYTHON].append(marker)

            elif marker in self.NODE_MARKERS:
                if ProjectLanguage.NODEJS not in language_markers:
                    language_markers[ProjectLanguage.NODEJS] = []
                language_markers[ProjectLanguage.NODEJS].append(marker)

            elif marker in self.GO_MARKERS:
                if ProjectLanguage.GO not in language_markers:
                    language_markers[ProjectLanguage.GO] = []
                language_markers[ProjectLanguage.GO].append(marker)

            elif marker in self.RUST_MARKERS:
                if ProjectLanguage.RUST not in language_markers:
                    language_markers[ProjectLanguage.RUST] = []
                language_markers[ProjectLanguage.RUST].append(marker)

            elif marker in self.JAVA_MARKERS:
                if ProjectLanguage.JAVA not in language_markers:
                    language_markers[ProjectLanguage.JAVA] = []
                language_markers[ProjectLanguage.JAVA].append(marker)

            # Check C# by markers or extensions
            elif marker in self.CSHARP_MARKERS or any(
                marker.endswith(ext) for ext in self.CSHARP_EXTENSIONS
            ):
                if ProjectLanguage.CSHARP not in language_markers:
                    language_markers[ProjectLanguage.CSHARP] = []
                language_markers[ProjectLanguage.CSHARP].append(marker)

        return language_markers

    def _determine_primary_language(
        self, language_markers: Dict[ProjectLanguage, List[str]]
    ) -> ProjectLanguage:
        """
        Determine primary language from detected markers.

        If multiple languages detected:
        - Single language > 80%: Primary = that language
        - Mixed (20-80%): Primary = language with highest marker count

        Args:
            language_markers: Dict of languages to their markers.

        Returns:
            ProjectLanguage with highest marker count or confidence.
        """
        if not language_markers:
            return ProjectLanguage.PYTHON  # Default fallback

        # Calculate total markers and percentages
        total_markers = sum(len(markers) for markers in language_markers.values())
        language_percentages = {
            lang: len(markers) / total_markers
            for lang, markers in language_markers.items()
        }

        # Find language with highest percentage
        primary = max(language_percentages, key=language_percentages.get)
        return primary

    def _determine_secondary_languages(
        self,
        language_markers: Dict[ProjectLanguage, List[str]],
        primary: ProjectLanguage,
    ) -> List[ProjectLanguage]:
        """
        Determine secondary languages in mixed-language project.

        Secondary languages are those with:
        - More than 20% of markers, OR
        - More than 2 marker files

        Args:
            language_markers: Dict of languages to their markers.
            primary: Primary language.

        Returns:
            List of secondary languages.
        """
        secondary = []

        if not language_markers:
            return secondary

        total_markers = sum(len(markers) for markers in language_markers.values())

        for lang, markers in language_markers.items():
            if lang == primary:
                continue

            percentage = len(markers) / total_markers if total_markers > 0 else 0
            # Include if >20% or >2 markers
            if percentage > 0.20 or len(markers) > 2:
                secondary.append(lang)

        return secondary

    # ========================================================================
    # Task 2.1.4: Version Extraction
    # ========================================================================

    def _extract_version(
        self, language: ProjectLanguage, markers: List[str]
    ) -> Optional[str]:
        """
        Extract version information for detected language.

        Delegates to language-specific extraction methods.

        Args:
            language: Detected language.
            markers: List of marker files found.

        Returns:
            Version string if found, None otherwise.
        """
        if language == ProjectLanguage.PYTHON:
            return self._extract_version_from_python(markers)
        elif language == ProjectLanguage.NODEJS:
            return self._extract_version_from_node(markers)
        elif language == ProjectLanguage.GO:
            return self._extract_version_from_go(markers)
        elif language == ProjectLanguage.RUST:
            return self._extract_version_from_rust(markers)
        elif language == ProjectLanguage.JAVA:
            return self._extract_version_from_java(markers)
        elif language == ProjectLanguage.CSHARP:
            return self._extract_version_from_csharp(markers)

        return None

    def _extract_version_from_python(self, markers: List[str]) -> Optional[str]:
        """
        Extract Python version from pyproject.toml, setup.py, or requirements.

        Args:
            markers: List of marker files found.

        Returns:
            Version string if found.
        """
        if self._is_timeout():
            return None

        # Try pyproject.toml first
        if "pyproject.toml" in markers:
            try:
                content = self._read_file_safe("pyproject.toml", lines=50)
                # Look for requires-python = ">=3.9" or similar
                match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    version_str = match.group(1)
                    # Extract version from >=3.9 format
                    match = re.search(r"\d+\.\d+", version_str)
                    if match:
                        return match.group(0)
            except Exception as e:
                logger.debug(f"Error extracting version from pyproject.toml: {e}")

        # Try setup.py
        if "setup.py" in markers:
            try:
                content = self._read_file_safe("setup.py", lines=50)
                match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    version_str = match.group(1)
                    match = re.search(r"\d+\.\d+", version_str)
                    if match:
                        return match.group(0)
            except Exception as e:
                logger.debug(f"Error extracting version from setup.py: {e}")

        return None

    def _extract_version_from_node(self, markers: List[str]) -> Optional[str]:
        """
        Extract Node.js version from package.json.

        Args:
            markers: List of marker files found.

        Returns:
            Version string if found.
        """
        if self._is_timeout():
            return None

        if "package.json" not in markers:
            return None

        try:
            content = self._read_file_safe("package.json", lines=100)
            data = json.loads(content)

            # Look for engines.node field
            if "engines" in data and "node" in data["engines"]:
                version_str = data["engines"]["node"]
                # Extract version from >=14.0.0 format
                match = re.search(r"\d+", version_str)
                if match:
                    return match.group(0)

            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Error extracting version from package.json: {e}")
            return None

    def _extract_version_from_go(self, markers: List[str]) -> Optional[str]:
        """
        Extract Go version from go.mod.

        First line should be "go 1.19" or similar.

        Args:
            markers: List of marker files found.

        Returns:
            Version string if found.
        """
        if self._is_timeout():
            return None

        if "go.mod" not in markers:
            return None

        try:
            content = self._read_file_safe("go.mod", lines=5)
            lines = content.strip().split("\n")
            for line in lines:
                if line.startswith("go "):
                    version = line.replace("go ", "").strip()
                    return version
            return None
        except Exception as e:
            logger.debug(f"Error extracting version from go.mod: {e}")
            return None

    def _extract_version_from_rust(self, markers: List[str]) -> Optional[str]:
        """
        Extract Rust edition from Cargo.toml.

        Args:
            markers: List of marker files found.

        Returns:
            Edition string if found.
        """
        if self._is_timeout():
            return None

        if "Cargo.toml" not in markers:
            return None

        try:
            content = self._read_file_safe("Cargo.toml", lines=50)
            # Look for edition = "2021" in [package] section
            match = re.search(r'edition\s*=\s*["\'](\d+)["\']', content)
            if match:
                return f"{match.group(1)}"
            return None
        except Exception as e:
            logger.debug(f"Error extracting version from Cargo.toml: {e}")
            return None

    def _extract_version_from_java(self, markers: List[str]) -> Optional[str]:
        """
        Extract Java version from pom.xml or build.gradle.

        Args:
            markers: List of marker files found.

        Returns:
            Version string if found.
        """
        if self._is_timeout():
            return None

        # Try pom.xml
        if "pom.xml" in markers:
            try:
                content = self._read_file_safe("pom.xml", lines=100)
                # Look for <source>11</source> or <target>11</target>
                match = re.search(r"<source>(\d+)</source>", content)
                if match:
                    return match.group(1)
                match = re.search(r"<target>(\d+)</target>", content)
                if match:
                    return match.group(1)
            except Exception as e:
                logger.debug(f"Error extracting version from pom.xml: {e}")

        # Try build.gradle
        if "build.gradle" in markers:
            try:
                content = self._read_file_safe("build.gradle", lines=100)
                # Look for sourceCompatibility = '11' or sourceCompatibility = JavaVersion.VERSION_11
                match = re.search(
                    r"sourceCompatibility\s*=\s*['\"]?(\d+)['\"]?", content
                )
                if match:
                    return match.group(1)
            except Exception as e:
                logger.debug(f"Error extracting version from build.gradle: {e}")

        return None

    def _extract_version_from_csharp(self, markers: List[str]) -> Optional[str]:
        """
        Extract .NET version from .csproj.

        Args:
            markers: List of marker files found.

        Returns:
            Version string if found.
        """
        if self._is_timeout():
            return None

        # Look for any .csproj file
        csproj_file = next((m for m in markers if m.endswith(".csproj")), None)
        if not csproj_file:
            return None

        try:
            content = self._read_file_safe(csproj_file, lines=50)
            # Look for <TargetFramework>net6.0</TargetFramework>
            match = re.search(r"<TargetFramework>([^<]+)</TargetFramework>", content)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            logger.debug(f"Error extracting version from {csproj_file}: {e}")
            return None

    # ========================================================================
    # Task 2.1.3: Confidence Scoring
    # ========================================================================

    def _calculate_confidence(
        self,
        language: ProjectLanguage,
        markers: List[str],
        version: Optional[str],
        language_markers: Dict[ProjectLanguage, List[str]],
    ) -> float:
        """
        Calculate confidence score for language detection.

        Confidence formula:
        - Base: 0.5 for any valid marker
        - Priority bonus: (priority_sum / max_priority) * 0.3
        - Marker count bonus: min(marker_count / 3, 1) * 0.1
        - Version bonus: +0.1 if version extracted
        - Multi-language penalty: -0.05 per secondary language

        High Confidence: >= 0.80
        Medium Confidence: 0.60-0.80
        Low Confidence: < 0.60

        Returns:
            Confidence between 0.0 and 1.0.
        """
        if not markers:
            return 0.0

        # Get markers for detected language
        lang_markers = language_markers.get(language, [])
        if not lang_markers:
            return 0.0

        # Base confidence: 0.5 for any detected marker
        confidence = 0.5

        # Calculate priority score bonus (up to 0.3)
        marker_defs = self._get_markers_for_language(language)
        total_priority = sum(
            marker_defs[m]["priority"] for m in lang_markers if m in marker_defs
        )
        max_priority = sum(info["priority"] for info in marker_defs.values())

        if max_priority > 0:
            priority_score = (total_priority / max_priority) * 0.3
            confidence += priority_score

        # Marker count bonus: more markers = higher confidence (up to 0.1)
        # 1 marker = 0.03, 2 markers = 0.067, 3+ markers = 0.1
        marker_count_factor = min(len(lang_markers) / 3.0, 1.0) * 0.1
        confidence += marker_count_factor

        # Boost for version extraction
        if version:
            confidence += 0.1

        # Penalty for multiple languages (mixed language projects less certain)
        num_secondary = len(language_markers) - 1  # Exclude primary
        if num_secondary > 0:
            confidence = max(confidence - (num_secondary * 0.05), 0.0)

        # Clamp to [0, 1]
        return max(0.0, min(confidence, 1.0))

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _read_file_safe(
        self, filename: str, lines: int = 100, encoding: str = "utf-8"
    ) -> str:
        """
        Read file safely with encoding fallback.

        Tries UTF-8 first, falls back to latin-1.

        Args:
            filename: Name of file to read (relative to project root).
            lines: Max number of lines to read.
            encoding: Preferred encoding.

        Returns:
            File contents as string.

        Raises:
            FileNotFoundError: If file doesn't exist.
            IOError: If file can't be read.
            ValueError: If path traversal detected.
        """
        filepath = self.project_root / filename

        # Security: Prevent path traversal attacks
        # Resolve to absolute path and verify it's within project_root
        try:
            resolved_path = filepath.resolve()
            if not str(resolved_path).startswith(str(self.project_root.resolve())):
                raise ValueError(f"Path traversal attempt blocked: {filename}")
        except (ValueError, OSError) as e:
            logger.warning(f"Invalid file path: {filename} - {e}")
            raise

        try:
            with open(filepath, "r", encoding=encoding) as f:
                # Read up to specified number of lines
                content = ""
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    content += line
                return content

        except UnicodeDecodeError:
            # Fallback to latin-1 (more permissive)
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    content = ""
                    for i, line in enumerate(f):
                        if i >= lines:
                            break
                        content += line
                    return content
            except Exception as e:
                logger.debug(f"Error reading {filename} even with latin-1: {e}")
                raise

    def _get_markers_for_language(
        self, language: ProjectLanguage
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get marker definitions for a language.

        Args:
            language: ProjectLanguage.

        Returns:
            Dict of marker filenames to metadata.
        """
        if language == ProjectLanguage.PYTHON:
            return self.PYTHON_MARKERS
        elif language == ProjectLanguage.NODEJS:
            return self.NODE_MARKERS
        elif language == ProjectLanguage.GO:
            return self.GO_MARKERS
        elif language == ProjectLanguage.RUST:
            return self.RUST_MARKERS
        elif language == ProjectLanguage.JAVA:
            return self.JAVA_MARKERS
        elif language == ProjectLanguage.CSHARP:
            return self.CSHARP_MARKERS
        else:
            return {}

    def _is_timeout(self) -> bool:
        """
        Check if detection has exceeded timeout budget.

        Returns:
            True if elapsed time > timeout.
        """
        elapsed = time.perf_counter() - self._start_time
        return elapsed > self.DETECTION_TIMEOUT_SECONDS
