"""
Code organization pattern detection module.
Identifies code organization and structure patterns used in projects.
"""

import os
import re
import json
import time
from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

from src.prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from src.prompt_enhancement.pipeline.project_files import ProjectIndicatorResult


class OrganizationType(str, Enum):
    """Types of project organization"""
    MONOREPO = "monorepo"
    SINGLE_REPO = "single_repo"
    UNKNOWN = "unknown"


@dataclass
class OrganizationPattern:
    """Single organization pattern detection"""
    name: str
    pattern_type: str
    confidence: float
    description: str = ""
    frequency: int = 0


@dataclass
class DirectoryMetrics:
    """Directory structure metrics"""
    max_depth: int = 0
    avg_depth: float = 0.0
    max_fanout: int = 0
    avg_fanout: float = 0.0
    total_directories: int = 0
    is_flat: bool = False
    is_hierarchical: bool = False


@dataclass
class CodeOrganizationResult:
    """Result of code organization pattern detection"""
    primary_type: Optional[OrganizationType] = None
    detected_patterns: List[OrganizationPattern] = field(default_factory=list)
    confidence: float = 0.0
    module_count: Optional[int] = None
    module_names: List[str] = field(default_factory=list)
    metrics: Optional[DirectoryMetrics] = None
    config_organization: str = ""
    analysis_notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"


class CodeOrganizationDetector:
    """Detects code organization patterns in projects"""

    # Common directory patterns
    COMMON_SOURCE_DIRS = {
        "src": "Source code root",
        "lib": "Library code",
        "app": "Application code",
        "source": "Source code",
    }

    COMPONENT_PATTERN_DIRS = {
        "components": "Component-based (React/Vue)",
        "containers": "Container components (React)",
        "pages": "Pages/routes",
        "services": "Service-oriented",
        "features": "Feature-based organization",
        "modules": "Module-based organization",
    }

    TEST_PATTERN_DIRS = {
        "test": "Standard test directory",
        "tests": "Tests directory",
        "__tests__": "JavaScript tests",
        "spec": "Specification tests",
    }

    CONFIG_DIRS = {
        "config": "Configuration directory",
        ".config": "Hidden config directory",
    }

    BUILD_DIRS = {
        "build": "Build output",
        "dist": "Distribution output",
        "out": "Output directory",
        "target": "Maven/Gradle output",
    }

    DOCUMENTATION_DIRS = {
        "docs": "Documentation",
        "doc": "Documentation",
        "documentation": "Documentation",
    }

    # Monorepo indicators
    MONOREPO_INDICATORS = {
        "lerna.json": "Lerna monorepo",
        "packages": "Monorepo packages directory",
        "modules": "Monorepo modules directory",
        "go.work": "Go workspace",
    }

    def __init__(self):
        """Initialize detector"""
        self.timeout = 1.5  # 1.5-second budget

    def detect_code_organization(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
        project_root: str = "."
    ) -> Optional[CodeOrganizationResult]:
        """
        Detect code organization patterns used in project.

        Args:
            tech_result: Project type detection results
            files_result: Project files detection results
            project_root: Root directory of project

        Returns:
            CodeOrganizationResult or None if detection fails
        """
        start_time = time.time()

        if not tech_result or not tech_result.primary_language:
            return None

        result = CodeOrganizationResult()

        # Build directory tree
        dir_tree = self._build_directory_tree(project_root)

        if not dir_tree:
            return None

        # Detect monorepo vs single-repo
        org_type, org_confidence = self._detect_organization_type(
            dir_tree, project_root, tech_result
        )
        result.primary_type = org_type
        result.confidence = org_confidence

        # Detect common directory patterns
        patterns = self._detect_directory_patterns(dir_tree, tech_result)
        result.detected_patterns = patterns

        # Detect module boundaries
        if org_type == OrganizationType.MONOREPO:
            module_info = self._detect_module_boundaries(dir_tree, project_root, tech_result)
            result.module_count = len(module_info["names"])
            result.module_names = module_info["names"]

        # Calculate metrics
        metrics = self._calculate_directory_metrics(dir_tree)
        result.metrics = metrics

        # Analyze configuration organization
        config_org = self._analyze_config_organization(project_root)
        result.config_organization = config_org

        # Generate analysis notes
        result.analysis_notes = self._generate_analysis_notes(result)

        return result

    def _build_directory_tree(self, project_root: str, max_depth: int = 10) -> Dict:
        """Build a tree of directory structure"""
        tree = {}

        try:
            for root, dirs, files in os.walk(project_root, topdown=True):
                # Limit depth
                depth = root[len(project_root):].count(os.sep)
                if depth > max_depth:
                    dirs[:] = []
                    continue

                # Skip hidden and vendor directories
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith(".") and d not in [
                        "node_modules", "vendor", "__pycache__", ".git",
                        ".venv", "venv", "dist", "build", "target"
                    ]
                ]

                rel_path = os.path.relpath(root, project_root)
                if rel_path == ".":
                    tree["_root"] = True
                    tree["_dirs"] = dirs
                    tree["_files"] = files
                else:
                    # Store directory info
                    parts = rel_path.split(os.sep)
                    current = tree
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    if parts[-1] not in current:
                        current[parts[-1]] = {}
                    current[parts[-1]]["_subdirs"] = dirs
                    current[parts[-1]]["_files"] = files

        except (OSError, IOError):
            pass

        return tree

    def _detect_organization_type(
        self,
        dir_tree: Dict,
        project_root: str,
        tech_result: ProjectTypeDetectionResult
    ) -> tuple:
        """Detect monorepo vs single-repo"""
        # Check for monorepo indicators
        monorepo_score = 0
        total_checks = 0

        # Check root-level indicators
        root_files = set(dir_tree.get("_files", []))
        root_dirs = set(dir_tree.get("_dirs", []))

        total_checks += 1
        if "lerna.json" in root_files:
            monorepo_score += 1
        if "go.work" in root_files:
            monorepo_score += 1

        # Check package.json workspaces (JavaScript/Node)
        if tech_result.primary_language == ProjectLanguage.NODEJS:
            if "package.json" in root_files:
                try:
                    pkg_path = Path(project_root) / "package.json"
                    with open(pkg_path, 'r') as f:
                        pkg_data = json.load(f)
                        if "workspaces" in pkg_data:
                            monorepo_score += 2
                except (IOError, json.JSONDecodeError):
                    pass

        # Check pom.xml modules (Java/Maven)
        if tech_result.primary_language == ProjectLanguage.JAVA:
            if "pom.xml" in root_files:
                try:
                    pom_path = Path(project_root) / "pom.xml"
                    with open(pom_path, 'r') as f:
                        content = f.read()
                        if "<modules>" in content or "<module>" in content:
                            monorepo_score += 2
                except (IOError, OSError):
                    pass

        # Check for packages/ or modules/ directories
        total_checks += 1
        if "packages" in root_dirs or "modules" in root_dirs:
            monorepo_score += 1

        # Count child package.json files
        pkg_json_count = 0
        for key in dir_tree.keys():
            if key.startswith("_"):
                continue
            if isinstance(dir_tree[key], dict) and "_files" in dir_tree[key]:
                if "package.json" in dir_tree[key].get("_files", []):
                    pkg_json_count += 1

        if pkg_json_count >= 2:
            monorepo_score += 1

        # Determine organization type
        confidence = monorepo_score / max(total_checks, 1)
        if confidence >= 0.5:
            return OrganizationType.MONOREPO, min(confidence, 0.95)
        else:
            return OrganizationType.SINGLE_REPO, 0.8

    def _detect_directory_patterns(
        self,
        dir_tree: Dict,
        tech_result: ProjectTypeDetectionResult
    ) -> List[OrganizationPattern]:
        """Detect common directory patterns"""
        patterns = []
        pattern_freq: Dict[str, int] = {}

        # Scan all directories in tree
        def scan_tree(node: Dict, path: str = ""):
            for key, value in node.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, dict):
                    # Check against known patterns
                    if key in self.COMMON_SOURCE_DIRS:
                        pattern_freq[key] = pattern_freq.get(key, 0) + 1
                    if key in self.COMPONENT_PATTERN_DIRS:
                        pattern_freq[key] = pattern_freq.get(key, 0) + 1
                    if key in self.TEST_PATTERN_DIRS:
                        pattern_freq[key] = pattern_freq.get(key, 0) + 1
                    scan_tree(value, f"{path}/{key}" if path else key)

        scan_tree(dir_tree)

        # Create patterns from detected directories
        for pattern_name, freq in pattern_freq.items():
            confidence = min(0.9, freq * 0.3)
            description = ""

            if pattern_name in self.COMMON_SOURCE_DIRS:
                description = self.COMMON_SOURCE_DIRS[pattern_name]
            elif pattern_name in self.COMPONENT_PATTERN_DIRS:
                description = self.COMPONENT_PATTERN_DIRS[pattern_name]
            elif pattern_name in self.TEST_PATTERN_DIRS:
                description = self.TEST_PATTERN_DIRS[pattern_name]

            patterns.append(OrganizationPattern(
                name=pattern_name,
                pattern_type="directory",
                confidence=confidence,
                description=description,
                frequency=freq
            ))

        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)

        return patterns

    def _detect_module_boundaries(
        self,
        dir_tree: Dict,
        project_root: str,
        tech_result: ProjectTypeDetectionResult
    ) -> Dict:
        """Detect module/package boundaries in monorepo"""
        module_names = []

        # Check packages directory
        if "packages" in dir_tree:
            packages_dir = dir_tree["packages"]
            for key, value in packages_dir.items():
                if not key.startswith("_") and isinstance(value, dict):
                    module_names.append(key)

        # Check modules directory
        if "modules" in dir_tree:
            modules_dir = dir_tree["modules"]
            for key, value in modules_dir.items():
                if not key.startswith("_") and isinstance(value, dict):
                    module_names.append(key)

        # For JavaScript, check workspaces
        if tech_result.primary_language == ProjectLanguage.NODEJS:
            try:
                pkg_path = Path(project_root) / "package.json"
                with open(pkg_path, 'r') as f:
                    pkg_data = json.load(f)
                    workspaces = pkg_data.get("workspaces", [])
                    for ws in workspaces:
                        # Parse workspace pattern (e.g., "packages/*")
                        if isinstance(ws, str):
                            # Simple parsing for "packages/*" pattern
                            if "*" in ws:
                                base_dir = ws.replace("/*", "").replace("\\*", "")
                                # Extract subdirectories
                                if base_dir in dir_tree:
                                    for key, value in dir_tree[base_dir].items():
                                        if not key.startswith("_"):
                                            module_names.append(key)
                            else:
                                module_names.append(ws)
            except (IOError, json.JSONDecodeError):
                pass

        return {"names": module_names}

    def _calculate_directory_metrics(self, dir_tree: Dict) -> DirectoryMetrics:
        """Calculate directory structure metrics"""
        metrics = DirectoryMetrics()

        depths = []
        fanouts = []
        total_dirs = 0

        def traverse(node: Dict, current_depth: int = 0):
            nonlocal total_dirs
            subdir_count = 0
            for key, value in node.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, dict):
                    total_dirs += 1
                    depths.append(current_depth)
                    subdir_count += 1
                    traverse(value, current_depth + 1)

            if subdir_count > 0:
                fanouts.append(subdir_count)

        traverse(dir_tree)

        metrics.total_directories = total_dirs
        metrics.max_depth = max(depths) if depths else 0
        metrics.avg_depth = sum(depths) / len(depths) if depths else 0
        metrics.max_fanout = max(fanouts) if fanouts else 0
        metrics.avg_fanout = sum(fanouts) / len(fanouts) if fanouts else 0

        # Determine flat vs hierarchical
        if metrics.max_depth <= 2:
            metrics.is_flat = True
        elif metrics.max_depth >= 5:
            metrics.is_hierarchical = True

        return metrics

    def _analyze_config_organization(self, project_root: str) -> str:
        """Analyze how configuration files are organized"""
        root_path = Path(project_root)
        config_files = []

        # Look for common config files
        config_patterns = [
            ".eslintrc*", ".prettierrc*", "tsconfig*.json",
            "jest.config*", "webpack.config*", ".env*",
            "pytest.ini", "setup.cfg", "pyproject.toml",
            "gradle.properties", "maven.properties"
        ]

        # Check root level
        for pattern in config_patterns:
            for file in root_path.glob(pattern):
                if file.is_file():
                    config_files.append(file.name)

        # Check for config directory
        config_dir = root_path / "config"
        if config_dir.exists():
            return "config_directory"

        # If many config files at root
        if len(config_files) >= 3:
            return "centralized_root"

        # Check for env-specific files
        env_files = list(root_path.glob(".env*"))
        if len(env_files) >= 2:
            return "environment_specific"

        return "standard"

    def _generate_analysis_notes(self, result: CodeOrganizationResult) -> str:
        """Generate analysis notes from results"""
        notes = []

        if result.primary_type:
            notes.append(f"Organization: {result.primary_type.value}")

        if result.module_count:
            notes.append(f"Modules: {result.module_count}")

        if result.metrics:
            if result.metrics.is_flat:
                notes.append("Flat directory structure")
            elif result.metrics.is_hierarchical:
                notes.append(f"Hierarchical structure (depth: {result.metrics.max_depth})")

        if result.detected_patterns:
            pattern_names = [p.name for p in result.detected_patterns[:3]]
            notes.append(f"Key patterns: {', '.join(pattern_names)}")

        return "; ".join(notes)
