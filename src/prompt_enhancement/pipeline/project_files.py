"""
Project Indicator Files Detector - Extract metadata from language-specific config files.

Identifies and parses configuration files for multiple languages to extract
project metadata, dependencies, and structure information.

This module implements Story 2.2: Identify Project Indicator Files.
"""

import os
import json
import re
import time
import logging
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple

# TOML parsing support
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python 3.6-3.10
    except ImportError:
        tomllib = None  # Fallback to regex if no TOML library available

logger = logging.getLogger(__name__)

from .tech_stack import ProjectLanguage


# ============================================================================
# Data Structures (Task 2.2.1)
# ============================================================================

@dataclass
class DependencyInfo:
    """Information about a single dependency."""

    name: str
    version: Optional[str]
    scope: str  # "production", "development", "optional"
    features: List[str]  # For Rust features, etc.


@dataclass
class ProjectMetadata:
    """Extracted project metadata."""

    name: Optional[str]
    version: Optional[str]
    source_language: ProjectLanguage
    dependencies: List[DependencyInfo]
    dev_dependencies: List[DependencyInfo]
    target_version: Optional[str]  # Python/Node/Java version, Rust edition, etc.
    package_manager: Optional[str]  # npm, pip, cargo, maven, gradle, etc.
    # AC4: Directory structure information
    source_directories: List[str] = None  # src/, lib/, main/, etc.
    test_directories: List[str] = None  # tests/, test/, __tests__, spec/, etc.
    build_directories: List[str] = None  # dist/, build/, target/, out/, etc.
    config_directories: List[str] = None  # config/, etc/

    def __post_init__(self):
        """Initialize list fields if None."""
        if self.source_directories is None:
            self.source_directories = []
        if self.test_directories is None:
            self.test_directories = []
        if self.build_directories is None:
            self.build_directories = []
        if self.config_directories is None:
            self.config_directories = []


@dataclass
class ProjectIndicatorResult:
    """Result of project indicator file detection."""

    metadata: Optional[ProjectMetadata]
    files_found: List[str]
    lock_files_present: Set[str]
    confidence: float
    lock_file_sync_status: Optional[str] = None  # AC3: "in-sync", "out-of-sync", "unknown"


# ============================================================================
# ProjectIndicatorFilesDetector Class
# ============================================================================

class ProjectIndicatorFilesDetector:
    """
    Detects and extracts metadata from project configuration files.

    Supports 6 languages: Python, Node.js, Go, Rust, Java, C#.
    Parses language-specific config files to extract project metadata,
    dependencies, and structure information.

    Attributes:
        project_root: Root directory of the project
        detected_language: Language detected from Story 2.1
    """

    # Language-specific configuration file definitions
    PYTHON_CONFIGS = {
        'pyproject.toml': {'priority': 10, 'type': 'toml'},
        'setup.cfg': {'priority': 8, 'type': 'ini'},
        'setup.py': {'priority': 7, 'type': 'python'},
        'requirements.txt': {'priority': 6, 'type': 'text'},
        'Pipfile': {'priority': 5, 'type': 'ini'},
    }

    PYTHON_LOCK_FILES = ['poetry.lock', 'Pipfile.lock']

    NODE_CONFIGS = {
        'package.json': {'priority': 10, 'type': 'json'},
    }

    NODE_LOCK_FILES = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']

    GO_CONFIGS = {
        'go.mod': {'priority': 10, 'type': 'text'},
    }

    GO_LOCK_FILES = ['go.sum']

    RUST_CONFIGS = {
        'Cargo.toml': {'priority': 10, 'type': 'toml'},
    }

    RUST_LOCK_FILES = ['Cargo.lock']

    JAVA_CONFIGS = {
        'pom.xml': {'priority': 10, 'type': 'xml'},
        'build.gradle': {'priority': 10, 'type': 'gradle'},
    }

    JAVA_LOCK_FILES = []

    CSHARP_CONFIGS = {
        '.csproj': {'priority': 10, 'type': 'xml'},
        '.sln': {'priority': 8, 'type': 'text'},
    }

    CSHARP_LOCK_FILES = ['packages.config']

    # Timeout for detection (2-second budget from Story 1.4)
    DETECTION_TIMEOUT_SECONDS = 2.0

    def __init__(self, project_root: str, detected_language: ProjectLanguage):
        """
        Initialize ProjectIndicatorFilesDetector.

        Args:
            project_root: Root directory of the project to analyze.
            detected_language: ProjectLanguage detected by Story 2.1.
        """
        self.project_root = Path(project_root)
        self.detected_language = detected_language
        self._start_time = time.perf_counter()

    def extract_project_metadata(self) -> Optional[ProjectIndicatorResult]:
        """
        Extract project metadata from configuration files.

        Returns:
            ProjectIndicatorResult with metadata and files found,
            or None if no configuration files found.

        AC Coverage:
            - AC1: Identify all language-specific config files
            - AC2: Extract project metadata
            - AC3: Handle lock files and dependency snapshots
            - AC4: Extract file structure information
            - AC5: Graceful handling of missing configuration
            - AC6: Dependency version analysis
        """
        try:
            # Find all config and lock files for this language
            files_found, lock_files = self._find_config_files()

            if not files_found:
                logger.debug(f"No config files found for {self.detected_language.value}")
                return None

            # Parse the first found config file (by priority)
            metadata = self._parse_config_files(files_found)

            if metadata is None:
                return None

            # Add lock file information
            metadata.package_manager = self._identify_package_manager(files_found, lock_files)

            # FIX #1 (CRITICAL): AC4 - Infer directory structure
            self._infer_directory_structure(metadata)

            # FIX #3 (HIGH): AC3 - Check lock file sync status
            lock_sync_status = self._check_lock_file_sync(files_found, lock_files)

            confidence = self._calculate_confidence(files_found, lock_files, metadata)

            # Combine all found files (config + lock files)
            all_files_found = files_found + list(lock_files)

            return ProjectIndicatorResult(
                metadata=metadata,
                files_found=all_files_found,
                lock_files_present=lock_files,
                confidence=confidence,
                lock_file_sync_status=lock_sync_status
            )

        except Exception as e:
            logger.error(f"Error extracting project metadata: {e}", exc_info=True)
            return None

    # ========================================================================
    # Task 2.2.2: Config File Reading
    # ========================================================================

    def _find_config_files(self) -> tuple[List[str], Set[str]]:
        """
        Find all config and lock files for the detected language.

        Returns:
            Tuple of (config_files_found, lock_files_found)
        """
        config_defs = self._get_config_files_for_language()
        lock_defs = self._get_lock_files_for_language()

        config_files = []
        lock_files = set()

        if not self.project_root.exists():
            logger.warning(f"Project root does not exist: {self.project_root}")
            return [], set()

        try:
            for item in self.project_root.iterdir():
                if self._is_timeout():
                    logger.warning("Detection timeout - stopping scan")
                    break

                # Check config files
                if item.name in config_defs and item.is_file():
                    config_files.append(item.name)

                # Check lock files
                if item.name in lock_defs and item.is_file():
                    lock_files.add(item.name)

                # Check for .csproj and .sln files (C#)
                if self.detected_language == ProjectLanguage.CSHARP:
                    if item.name.endswith('.csproj') or item.name.endswith('.sln'):
                        config_files.append(item.name)

        except PermissionError as e:
            logger.warning(f"Permission denied scanning project root: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")

        return config_files, lock_files

    def _read_file_safe(self, filename: str, lines: int = 200, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file safely with encoding fallback.

        Args:
            filename: Filename relative to project root.
            lines: Maximum lines to read.
            encoding: Preferred encoding.

        Returns:
            File contents or None if error.
        """
        filepath = self.project_root / filename

        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = ''
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    content += line
                return content

        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = ''
                    for i, line in enumerate(f):
                        if i >= lines:
                            break
                        content += line
                    return content
            except Exception as e:
                logger.debug(f"Error reading {filename} even with latin-1: {e}")
                return None

        except Exception as e:
            logger.debug(f"Error reading {filename}: {e}")
            return None

    # ========================================================================
    # Task 2.2.3 & 2.2.4: Language-Specific Parsing
    # ========================================================================

    def _parse_config_files(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """
        Parse config files and extract metadata.

        Args:
            config_files: List of found config filenames.

        Returns:
            ProjectMetadata or None if parsing fails.
        """
        if self.detected_language == ProjectLanguage.PYTHON:
            return self._parse_python_config(config_files)
        elif self.detected_language == ProjectLanguage.NODEJS:
            return self._parse_node_config(config_files)
        elif self.detected_language == ProjectLanguage.GO:
            return self._parse_go_config(config_files)
        elif self.detected_language == ProjectLanguage.RUST:
            return self._parse_rust_config(config_files)
        elif self.detected_language == ProjectLanguage.JAVA:
            return self._parse_java_config(config_files)
        elif self.detected_language == ProjectLanguage.CSHARP:
            return self._parse_csharp_config(config_files)

        return None

    def _parse_python_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse Python configuration files."""
        metadata = None

        # Try pyproject.toml first (modern standard)
        if 'pyproject.toml' in config_files:
            try:
                content = self._read_file_safe('pyproject.toml')
                if content:
                    metadata = self._extract_pyproject_toml(content)
                    if metadata:
                        return metadata
            except Exception as e:
                logger.debug(f"Error parsing pyproject.toml: {e}")

        # Try setup.py
        if 'setup.py' in config_files:
            try:
                content = self._read_file_safe('setup.py')
                if content:
                    metadata = self._extract_setup_py(content)
                    if metadata:
                        return metadata
            except Exception as e:
                logger.debug(f"Error parsing setup.py: {e}")

        # Try requirements.txt
        if 'requirements.txt' in config_files:
            try:
                content = self._read_file_safe('requirements.txt')
                if content:
                    metadata = self._extract_requirements_txt(content)
                    if metadata:
                        return metadata
            except Exception as e:
                logger.debug(f"Error parsing requirements.txt: {e}")

        return metadata

    def _extract_pyproject_toml(self, content: str) -> Optional[ProjectMetadata]:
        """Extract metadata from pyproject.toml using proper TOML parser."""
        try:
            # Try using tomllib if available (FIX #6: Use TOML library instead of regex)
            if tomllib:
                try:
                    data = tomllib.loads(content)
                    project = data.get('project', {})

                    name = project.get('name')
                    version = project.get('version')
                    python_version = project.get('requires-python')

                    # Extract dependencies (FIX #5: Proper dependency parsing)
                    dependencies = []
                    for dep_spec in project.get('dependencies', []):
                        dep_info = self._parse_python_dependency(dep_spec)
                        if dep_info:
                            dependencies.append(dep_info)

                    # Extract dev dependencies
                    dev_dependencies = []
                    optional_deps = project.get('optional-dependencies', {})
                    for group_name, deps in optional_deps.items():
                        for dep_spec in deps:
                            dep_info = self._parse_python_dependency(dep_spec)
                            if dep_info:
                                dep_info.scope = "development"
                                dev_dependencies.append(dep_info)

                    return ProjectMetadata(
                        name=name,
                        version=version,
                        source_language=ProjectLanguage.PYTHON,
                        dependencies=dependencies,
                        dev_dependencies=dev_dependencies,
                        target_version=python_version,
                        package_manager="pip"
                    )
                except Exception as toml_error:
                    logger.debug(f"TOML parsing failed: {toml_error}, falling back to regex")

            # Fallback to regex parsing if tomllib not available
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            python_match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)

            name = name_match.group(1) if name_match else None
            version = version_match.group(1) if version_match else None
            python_version = python_match.group(1) if python_match else None

            # Extract dependencies
            dependencies = []
            deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if deps_match:
                deps_text = deps_match.group(1)
                for dep in re.findall(r'["\']([^"\']+)["\']', deps_text):
                    dep_info = self._parse_python_dependency(dep)
                    if dep_info:
                        dependencies.append(dep_info)

            return ProjectMetadata(
                name=name,
                version=version,
                source_language=ProjectLanguage.PYTHON,
                dependencies=dependencies,
                dev_dependencies=[],
                target_version=python_version,
                package_manager="pip"
            )
        except Exception as e:
            logger.debug(f"Error extracting from pyproject.toml: {e}")
            return None

    def _parse_python_dependency(self, dep_spec: str) -> Optional[DependencyInfo]:
        """
        Parse Python dependency specification.

        Handles: requests==2.28.0, requests>=1.2.0, requests~=1.2.0, requests!=1.1.0, etc.
        FIX #5: Proper handling of Python version operators.

        Args:
            dep_spec: Dependency specification string

        Returns:
            DependencyInfo or None if parsing fails
        """
        try:
            # Match package name and version constraint
            # Pattern: package_name (comparison_operator version)?
            match = re.match(r'^([a-zA-Z0-9_\-\.]+)\s*([><=!~]+.*)?$', dep_spec.strip())
            if match:
                dep_name = match.group(1)
                dep_version = match.group(2).strip() if match.group(2) else None

                return DependencyInfo(
                    name=dep_name,
                    version=dep_version,
                    scope="production",
                    features=[]
                )
            return None
        except Exception as e:
            logger.debug(f"Error parsing Python dependency '{dep_spec}': {e}")
            return None

    def _extract_setup_py(self, content: str) -> Optional[ProjectMetadata]:
        """Extract metadata from setup.py."""
        try:
            name_match = re.search(r"name\s*=\s*['\"]([^'\"]+)['\"]", content)
            version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)

            name = name_match.group(1) if name_match else None
            version = version_match.group(1) if version_match else None

            return ProjectMetadata(
                name=name,
                version=version,
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version=None,
                package_manager="pip"
            )
        except Exception as e:
            logger.debug(f"Error extracting from setup.py: {e}")
            return None

    def _extract_requirements_txt(self, content: str) -> Optional[ProjectMetadata]:
        """Extract dependencies from requirements.txt (FIX #5: Use proper parser)."""
        try:
            dependencies = []
            for line in content.split('\n'):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Skip -r, -e, git+, and local paths for now
                if line.startswith('-r') or line.startswith('-e') or line.startswith('git+') or line.startswith('./'):
                    continue

                # Use the proper Python dependency parser
                dep_info = self._parse_python_dependency(line)
                if dep_info:
                    dependencies.append(dep_info)

            return ProjectMetadata(
                name=None,
                version=None,
                source_language=ProjectLanguage.PYTHON,
                dependencies=dependencies,
                dev_dependencies=[],
                target_version=None,
                package_manager="pip"
            )
        except Exception as e:
            logger.debug(f"Error extracting from requirements.txt: {e}")
            return None

    def _parse_node_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse Node.js configuration files."""
        if 'package.json' not in config_files:
            return None

        try:
            content = self._read_file_safe('package.json')
            if not content:
                return None

            data = json.loads(content)

            # Extract metadata
            name = data.get('name')
            version = data.get('version')

            # Extract Node version
            node_version = None
            if 'engines' in data and 'node' in data['engines']:
                node_ver_str = data['engines']['node']
                # Match semantic version like 16, 16.0, 16.0.0
                match = re.search(r'(\d+(?:\.\d+)*)', node_ver_str)
                if match:
                    node_version = match.group(1)

            # Extract dependencies
            dependencies = []
            if 'dependencies' in data:
                for dep_name, dep_version in data['dependencies'].items():
                    dependencies.append(DependencyInfo(
                        name=dep_name,
                        version=dep_version,
                        scope="production",
                        features=[]
                    ))

            dev_dependencies = []
            if 'devDependencies' in data:
                for dep_name, dep_version in data['devDependencies'].items():
                    dev_dependencies.append(DependencyInfo(
                        name=dep_name,
                        version=dep_version,
                        scope="development",
                        features=[]
                    ))

            return ProjectMetadata(
                name=name,
                version=version,
                source_language=ProjectLanguage.NODEJS,
                dependencies=dependencies,
                dev_dependencies=dev_dependencies,
                target_version=node_version,
                package_manager="npm"
            )

        except json.JSONDecodeError as e:
            logger.debug(f"Error parsing package.json: {e}")
            return None
        except Exception as e:
            logger.debug(f"Error extracting from package.json: {e}")
            return None

    def _parse_go_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse Go configuration files (FIX #2: Extract dependencies)."""
        if 'go.mod' not in config_files:
            return None

        try:
            content = self._read_file_safe('go.mod')
            if not content:
                return None

            lines = content.split('\n')
            go_version = None
            module_name = None
            dependencies = []
            in_require_block = False

            for line in lines:
                line = line.strip()

                # Extract Go version
                if line.startswith('go '):
                    go_version = line.replace('go ', '').strip()

                # Extract module name
                if line.startswith('module '):
                    module_name = line.replace('module ', '').strip()

                # Handle require block
                if line.startswith('require ('):
                    in_require_block = True
                    continue
                elif line == ')' and in_require_block:
                    in_require_block = False
                    continue

                # Parse dependency
                if in_require_block or line.startswith('require '):
                    # Remove 'require ' prefix if single-line
                    if line.startswith('require '):
                        line = line.replace('require ', '', 1).strip()

                    # Parse: github.com/some/lib v1.2.3 or github.com/some/lib v1.2.3 // indirect
                    match = re.match(r'([^\s]+)\s+([^\s]+)', line)
                    if match:
                        dep_name = match.group(1)
                        dep_version = match.group(2)
                        scope = "production" if "// indirect" not in line else "transitive"
                        dependencies.append(DependencyInfo(
                            name=dep_name,
                            version=dep_version,
                            scope=scope,
                            features=[]
                        ))

            return ProjectMetadata(
                name=module_name,
                version=None,
                source_language=ProjectLanguage.GO,
                dependencies=dependencies,
                dev_dependencies=[],
                target_version=go_version,
                package_manager="go"
            )

        except Exception as e:
            logger.debug(f"Error parsing go.mod: {e}")
            return None

    def _parse_rust_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse Rust configuration files (FIX #2: Extract dependencies)."""
        if 'Cargo.toml' not in config_files:
            return None

        try:
            content = self._read_file_safe('Cargo.toml')
            if not content:
                return None

            # Try using TOML library if available
            if tomllib:
                try:
                    data = tomllib.loads(content)
                    package = data.get('package', {})

                    name = package.get('name')
                    version = package.get('version')
                    edition = package.get('edition')

                    # Extract dependencies
                    dependencies = []
                    for dep_name, dep_spec in data.get('dependencies', {}).items():
                        if isinstance(dep_spec, str):
                            # Simple version: tokio = "1.35"
                            dependencies.append(DependencyInfo(
                                name=dep_name,
                                version=dep_spec,
                                scope="production",
                                features=[]
                            ))
                        elif isinstance(dep_spec, dict):
                            # Complex spec: serde = { version = "1.0", features = ["derive"] }
                            version = dep_spec.get('version')
                            features = dep_spec.get('features', [])
                            dependencies.append(DependencyInfo(
                                name=dep_name,
                                version=version,
                                scope="production",
                                features=features
                            ))

                    # Extract dev dependencies
                    dev_dependencies = []
                    for dep_name, dep_spec in data.get('dev-dependencies', {}).items():
                        if isinstance(dep_spec, str):
                            dev_dependencies.append(DependencyInfo(
                                name=dep_name,
                                version=dep_spec,
                                scope="development",
                                features=[]
                            ))

                    return ProjectMetadata(
                        name=name,
                        version=version,
                        source_language=ProjectLanguage.RUST,
                        dependencies=dependencies,
                        dev_dependencies=dev_dependencies,
                        target_version=edition,
                        package_manager="cargo"
                    )
                except Exception as toml_error:
                    logger.debug(f"Cargo.toml TOML parsing failed: {toml_error}, falling back to regex")

            # Fallback to regex
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            edition_match = re.search(r'edition\s*=\s*["\'](\d+)["\']', content)

            name = name_match.group(1) if name_match else None
            version = version_match.group(1) if version_match else None
            edition = edition_match.group(1) if edition_match else None

            return ProjectMetadata(
                name=name,
                version=version,
                source_language=ProjectLanguage.RUST,
                dependencies=[],
                dev_dependencies=[],
                target_version=edition,
                package_manager="cargo"
            )

        except Exception as e:
            logger.debug(f"Error parsing Cargo.toml: {e}")
            return None

    def _parse_java_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse Java configuration files (FIX #2: Extract dependencies)."""
        # Try pom.xml first
        if 'pom.xml' in config_files:
            try:
                content = self._read_file_safe('pom.xml')
                if content:
                    java_version = self._extract_java_version_from_pom(content)
                    dependencies = self._extract_maven_dependencies(content)
                    return ProjectMetadata(
                        name=None,
                        version=None,
                        source_language=ProjectLanguage.JAVA,
                        dependencies=dependencies,
                        dev_dependencies=[],
                        target_version=java_version,
                        package_manager="maven"
                    )
            except Exception as e:
                logger.debug(f"Error parsing pom.xml: {e}")

        # Try build.gradle
        if 'build.gradle' in config_files:
            try:
                content = self._read_file_safe('build.gradle')
                if content:
                    java_version = self._extract_java_version_from_gradle(content)
                    dependencies = self._extract_gradle_dependencies(content)
                    return ProjectMetadata(
                        name=None,
                        version=None,
                        source_language=ProjectLanguage.JAVA,
                        dependencies=dependencies,
                        dev_dependencies=[],
                        target_version=java_version,
                        package_manager="gradle"
                    )
            except Exception as e:
                logger.debug(f"Error parsing build.gradle: {e}")

        return None

    def _extract_maven_dependencies(self, content: str) -> List[DependencyInfo]:
        """Extract dependencies from pom.xml (FIX #2)."""
        dependencies = []
        try:
            # Extract all <dependency> blocks
            dep_pattern = r'<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>(?:\s*<scope>([^<]+)</scope>)?'
            for match in re.finditer(dep_pattern, content, re.DOTALL):
                group_id = match.group(1).strip()
                artifact_id = match.group(2).strip()
                version = match.group(3).strip()
                scope = match.group(4).strip() if match.group(4) else "compile"

                dep_name = f"{group_id}:{artifact_id}"
                dep_scope = "development" if scope == "test" else "production"

                dependencies.append(DependencyInfo(
                    name=dep_name,
                    version=version,
                    scope=dep_scope,
                    features=[]
                ))
        except Exception as e:
            logger.debug(f"Error extracting Maven dependencies: {e}")
        return dependencies

    def _extract_gradle_dependencies(self, content: str) -> List[DependencyInfo]:
        """Extract dependencies from build.gradle (FIX #2)."""
        dependencies = []
        try:
            # Match patterns like: implementation 'group:artifact:version'
            dep_pattern = r"(implementation|api|compile|testImplementation|testCompile)\s+['\"]([^'\"]+)['\"]"
            for match in re.finditer(dep_pattern, content):
                config = match.group(1)
                dep_spec = match.group(2)

                # Parse group:artifact:version
                parts = dep_spec.split(':')
                if len(parts) >= 2:
                    dep_name = f"{parts[0]}:{parts[1]}"
                    dep_version = parts[2] if len(parts) >= 3 else None
                    dep_scope = "development" if "test" in config.lower() else "production"

                    dependencies.append(DependencyInfo(
                        name=dep_name,
                        version=dep_version,
                        scope=dep_scope,
                        features=[]
                    ))
        except Exception as e:
            logger.debug(f"Error extracting Gradle dependencies: {e}")
        return dependencies

    def _extract_java_version_from_pom(self, content: str) -> Optional[str]:
        """Extract Java version from pom.xml."""
        # Try maven.compiler.source first (more common in properties)
        match = re.search(r'<maven\.compiler\.source>(\d+)</maven\.compiler\.source>', content)
        if match:
            return match.group(1)
        # Try maven.compiler.target
        match = re.search(r'<maven\.compiler\.target>(\d+)</maven\.compiler\.target>', content)
        if match:
            return match.group(1)
        # Try direct source/target tags
        match = re.search(r'<source>(\d+)</source>', content)
        if match:
            return match.group(1)
        match = re.search(r'<target>(\d+)</target>', content)
        if match:
            return match.group(1)
        return None

    def _extract_java_version_from_gradle(self, content: str) -> Optional[str]:
        """Extract Java version from build.gradle."""
        match = re.search(r"sourceCompatibility\s*=\s*['\"]?(\d+)['\"]?", content)
        if match:
            return match.group(1)
        return None

    def _parse_csharp_config(self, config_files: List[str]) -> Optional[ProjectMetadata]:
        """Parse C# configuration files (FIX #2: Extract dependencies)."""
        # Find .csproj file
        csproj_file = next((f for f in config_files if f.endswith('.csproj')), None)
        if not csproj_file:
            return None

        try:
            content = self._read_file_safe(csproj_file)
            if not content:
                return None

            target_match = re.search(r'<TargetFramework>([^<]+)</TargetFramework>', content)
            target_version = target_match.group(1) if target_match else None

            # Extract dependencies from PackageReference tags
            dependencies = []
            dep_pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
            for match in re.finditer(dep_pattern, content):
                dep_name = match.group(1)
                dep_version = match.group(2)
                dependencies.append(DependencyInfo(
                    name=dep_name,
                    version=dep_version,
                    scope="production",
                    features=[]
                ))

            return ProjectMetadata(
                name=None,
                version=None,
                source_language=ProjectLanguage.CSHARP,
                dependencies=dependencies,
                dev_dependencies=[],
                target_version=target_version,
                package_manager="nuget"
            )

        except Exception as e:
            logger.debug(f"Error parsing {csproj_file}: {e}")
            return None

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_config_files_for_language(self) -> Dict[str, Dict[str, str]]:
        """Get config file definitions for detected language."""
        if self.detected_language == ProjectLanguage.PYTHON:
            return self.PYTHON_CONFIGS
        elif self.detected_language == ProjectLanguage.NODEJS:
            return self.NODE_CONFIGS
        elif self.detected_language == ProjectLanguage.GO:
            return self.GO_CONFIGS
        elif self.detected_language == ProjectLanguage.RUST:
            return self.RUST_CONFIGS
        elif self.detected_language == ProjectLanguage.JAVA:
            return self.JAVA_CONFIGS
        elif self.detected_language == ProjectLanguage.CSHARP:
            return self.CSHARP_CONFIGS
        return {}

    def _get_lock_files_for_language(self) -> List[str]:
        """Get lock file definitions for detected language."""
        if self.detected_language == ProjectLanguage.PYTHON:
            return self.PYTHON_LOCK_FILES
        elif self.detected_language == ProjectLanguage.NODEJS:
            return self.NODE_LOCK_FILES
        elif self.detected_language == ProjectLanguage.GO:
            return self.GO_LOCK_FILES
        elif self.detected_language == ProjectLanguage.RUST:
            return self.RUST_LOCK_FILES
        elif self.detected_language == ProjectLanguage.JAVA:
            return self.JAVA_LOCK_FILES
        elif self.detected_language == ProjectLanguage.CSHARP:
            return self.CSHARP_LOCK_FILES
        return []

    def _identify_package_manager(self, config_files: List[str], lock_files: Set[str]) -> Optional[str]:
        """Identify package manager from files present."""
        if self.detected_language == ProjectLanguage.PYTHON:
            if 'poetry.lock' in lock_files:
                return 'poetry'
            elif 'Pipfile.lock' in lock_files:
                return 'pipenv'
            return 'pip'
        elif self.detected_language == ProjectLanguage.NODEJS:
            if 'yarn.lock' in lock_files:
                return 'yarn'
            elif 'pnpm-lock.yaml' in lock_files:
                return 'pnpm'
            return 'npm'
        elif self.detected_language == ProjectLanguage.GO:
            return 'go'
        elif self.detected_language == ProjectLanguage.RUST:
            return 'cargo'
        elif self.detected_language == ProjectLanguage.JAVA:
            if 'pom.xml' in config_files:
                return 'maven'
            elif 'build.gradle' in config_files:
                return 'gradle'
        elif self.detected_language == ProjectLanguage.CSHARP:
            return 'nuget'
        return None

    def _calculate_confidence(self, config_files: List[str], lock_files: Set[str],
                            metadata: Optional[ProjectMetadata]) -> float:
        """Calculate confidence score."""
        if not config_files:
            return 0.0

        # Base: 0.6 for finding config file
        confidence = 0.6

        # Bonus for multiple files
        if len(config_files) > 1:
            confidence += 0.15

        # Bonus for lock files
        if lock_files:
            confidence += 0.15

        # Bonus for extracted metadata
        if metadata:
            if metadata.name:
                confidence += 0.05
            if metadata.version:
                confidence += 0.05

        return min(confidence, 1.0)

    def _is_timeout(self) -> bool:
        """Check if detection has exceeded timeout."""
        elapsed = time.perf_counter() - self._start_time
        return elapsed > self.DETECTION_TIMEOUT_SECONDS

    def _infer_directory_structure(self, metadata: ProjectMetadata) -> None:
        """
        Infer directory structure from project root (FIX #1 CRITICAL: AC4).

        Identifies common directories:
        - Source directories: src/, lib/, main/, app/, etc.
        - Test directories: tests/, test/, __tests__, spec/, etc.
        - Build directories: dist/, build/, target/, out/, bin/, etc.
        - Config directories: config/, etc/, conf/

        Args:
            metadata: ProjectMetadata to populate with directory information
        """
        # Common directory patterns by category
        SOURCE_PATTERNS = {'src', 'lib', 'main', 'app', 'source', 'pkg', 'internal'}
        TEST_PATTERNS = {'tests', 'test', '__tests__', 'spec', 'specs', 'testing', 'test-unit', 'test-integration'}
        BUILD_PATTERNS = {'dist', 'build', 'target', 'out', 'bin', 'obj', 'release', 'debug', 'output'}
        CONFIG_PATTERNS = {'config', 'etc', 'conf', 'settings', '.config'}

        try:
            if not self.project_root.exists():
                return

            for item in self.project_root.iterdir():
                if not item.is_dir():
                    continue

                dir_name = item.name.lower()

                # Categorize directory
                if dir_name in SOURCE_PATTERNS:
                    metadata.source_directories.append(item.name)
                elif dir_name in TEST_PATTERNS:
                    metadata.test_directories.append(item.name)
                elif dir_name in BUILD_PATTERNS:
                    metadata.build_directories.append(item.name)
                elif dir_name in CONFIG_PATTERNS:
                    metadata.config_directories.append(item.name)

        except Exception as e:
            logger.debug(f"Error inferring directory structure: {e}")

    def _check_lock_file_sync(self, config_files: List[str], lock_files: Set[str]) -> str:
        """
        Check if lock files are in sync with config files (FIX #3 HIGH: AC3).

        Compares modification timestamps between config and lock files.

        Args:
            config_files: List of config file names found
            lock_files: Set of lock file names found

        Returns:
            "in-sync", "out-of-sync", or "unknown"
        """
        try:
            if not lock_files:
                return "unknown"  # No lock files to check

            # Get primary config file (first in list)
            if not config_files:
                return "unknown"

            primary_config = config_files[0]
            config_path = self.project_root / primary_config

            # Find corresponding lock file
            lock_file = None
            for lock in lock_files:
                lock_file = lock
                break

            if not lock_file:
                return "unknown"

            lock_path = self.project_root / lock_file

            # Compare modification times
            if config_path.exists() and lock_path.exists():
                config_mtime = config_path.stat().st_mtime
                lock_mtime = lock_path.stat().st_mtime

                # Lock file should be newer or equal to config file
                if lock_mtime >= config_mtime:
                    return "in-sync"
                else:
                    return "out-of-sync"

            return "unknown"

        except Exception as e:
            logger.debug(f"Error checking lock file sync: {e}")
            return "unknown"
