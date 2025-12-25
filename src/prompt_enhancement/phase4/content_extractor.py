"""
ContentExtractor - Extracts project information for AGENTS.md template filling.

This module analyzes project structure, configuration files, and metadata
to automatically fill in template placeholders with project-specific values.

Phase 4 Task: Dynamic Constraint Generation
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProjectInfo:
    """Extracted project information."""

    name: str
    description: str
    primary_language: str
    version: str
    setup_command: str
    test_command: str
    run_command: str
    build_command: Optional[str]
    lint_command: Optional[str]
    format_command: Optional[str]
    type_check_command: Optional[str]
    main_dependencies: List[str]
    code_style_guidelines: Dict[str, str]
    project_structure: str
    protected_directories: List[str]
    additional_info: Dict[str, Any]


class ContentExtractor:
    """
    Extracts project information for AGENTS.md template filling.

    Analyzes various configuration files (package.json, pyproject.toml, etc.)
    and project structure to determine appropriate values for template placeholders.

    Attributes:
        project_root: Root directory of the project
    """

    def __init__(self, project_root: str):
        """
        Initialize the content extractor.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)

    def extract_info(self) -> ProjectInfo:
        """
        Extract all project information.

        Returns:
            ProjectInfo object with extracted values
        """
        name = self._extract_project_name()
        description = self._extract_description()
        primary_language = self._detect_primary_language()
        version = self._extract_version()

        setup_cmd, test_cmd, run_cmd, build_cmd = self._extract_commands(
            primary_language
        )
        lint_cmd, format_cmd, type_check_cmd = self._extract_quality_commands(
            primary_language
        )

        dependencies = self._extract_main_dependencies()
        code_style = self._extract_code_style_guidelines(primary_language)
        structure = self._generate_project_structure()
        protected_dirs = self._identify_protected_directories()

        return ProjectInfo(
            name=name,
            description=description,
            primary_language=primary_language,
            version=version,
            setup_command=setup_cmd,
            test_command=test_cmd,
            run_command=run_cmd,
            build_command=build_cmd,
            lint_command=lint_cmd,
            format_command=format_cmd,
            type_check_command=type_check_cmd,
            main_dependencies=dependencies,
            code_style_guidelines=code_style,
            project_structure=structure,
            protected_directories=protected_dirs,
            additional_info=self._extract_additional_info(primary_language),
        )

    def _extract_project_name(self) -> str:
        """Extract project name from various sources."""
        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "name" in data:
                        return data["name"]
            except (json.JSONDecodeError, IOError):
                pass

        # Try pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                    match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except IOError:
                pass

        # Try go.mod
        go_mod = self.project_root / "go.mod"
        if go_mod.exists():
            try:
                with open(go_mod) as f:
                    first_line = f.readline()
                    match = re.search(r"module\s+(.+)", first_line)
                    if match:
                        return match.group(1).split("/")[-1]
            except IOError:
                pass

        # Fallback to directory name
        return self.project_root.name

    def _extract_description(self) -> str:
        """Extract project description."""
        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "description" in data:
                        return data["description"]
            except (json.JSONDecodeError, IOError):
                pass

        # Try pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                    match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except IOError:
                pass

        return "Project description"

    def _detect_primary_language(self) -> str:
        """Detect primary programming language."""
        # Check for Python
        if (
            (self.project_root / "requirements.txt").exists()
            or (self.project_root / "pyproject.toml").exists()
            or (self.project_root / "setup.py").exists()
        ):
            return "Python"

        # Check for Node.js
        if (self.project_root / "package.json").exists():
            return "Node.js"

        # Check for Go
        if (self.project_root / "go.mod").exists():
            return "Go"

        # Check for Rust
        if (self.project_root / "Cargo.toml").exists():
            return "Rust"

        # Check for Java
        if (self.project_root / "pom.xml").exists() or (
            self.project_root / "build.gradle"
        ).exists():
            return "Java"

        # Check for C#
        if (self.project_root / "*.csproj").exists() or (
            self.project_root / "*.sln"
        ).exists():
            return "C#"

        return "Unknown"

    def _extract_version(self) -> str:
        """Extract project version."""
        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "version" in data:
                        return data["version"]
            except (json.JSONDecodeError, IOError):
                pass

        # Try pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except IOError:
                pass

        return "0.1.0"

    def _extract_commands(self, language: str) -> Tuple[str, str, str, Optional[str]]:
        """
        Extract setup, test, run, and build commands.

        Returns:
            Tuple of (setup_cmd, test_cmd, run_cmd, build_cmd)
        """
        if language == "Python":
            return (
                "pip install -r requirements.txt",
                "pytest tests/ -v",
                "python -m main",
                None,
            )
        elif language == "Node.js":
            package_json = self.project_root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                        scripts = data.get("scripts", {})
                        return (
                            "npm install",
                            scripts.get("test", "npm test"),
                            scripts.get("start", "npm start"),
                            scripts.get("build", "npm run build"),
                        )
                except (json.JSONDecodeError, IOError):
                    pass
            return ("npm install", "npm test", "npm start", "npm run build")
        elif language == "Go":
            return (
                "go mod download",
                "go test ./...",
                "go run main.go",
                "go build -o app",
            )
        elif language == "Rust":
            return ("cargo build", "cargo test", "cargo run", "cargo build --release")
        elif language == "Java":
            if (self.project_root / "pom.xml").exists():
                return (
                    "mvn clean install",
                    "mvn test",
                    "mvn clean compile exec:java",
                    "mvn package",
                )
            else:
                return ("gradle build", "gradle test", "gradle run", "gradle build")

        return ("N/A", "N/A", "N/A", None)

    def _extract_quality_commands(
        self, language: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract lint, format, and type-check commands."""
        if language == "Python":
            lint_cmd = "pylint src/"
            format_cmd = "black src/"
            type_check_cmd = "mypy src/"
            return lint_cmd, format_cmd, type_check_cmd
        elif language == "Node.js":
            lint_cmd = "eslint src/"
            format_cmd = "prettier --write src/"
            type_check_cmd = None
            return lint_cmd, format_cmd, type_check_cmd
        elif language == "Go":
            lint_cmd = "golangci-lint run ./..."
            format_cmd = "go fmt ./..."
            type_check_cmd = None
            return lint_cmd, format_cmd, type_check_cmd
        elif language == "Rust":
            lint_cmd = "cargo clippy"
            format_cmd = "cargo fmt"
            type_check_cmd = "cargo check"
            return lint_cmd, format_cmd, type_check_cmd

        return None, None, None

    def _extract_main_dependencies(self) -> List[str]:
        """Extract main project dependencies."""
        dependencies: List[str] = []

        # Python
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            dependencies.append(line.split("==")[0].split(";")[0])
            except IOError:
                pass

        # Node.js
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dependencies.extend(list(deps.keys())[:5])
            except (json.JSONDecodeError, IOError):
                pass

        return dependencies[:5]  # Return top 5

    def _extract_code_style_guidelines(self, language: str) -> Dict[str, str]:
        """Extract code style guidelines based on language."""
        guidelines: Dict[str, str] = {}

        if language == "Python":
            guidelines = {
                "naming": "snake_case for functions/variables, PascalCase for classes",
                "formatting": "Black formatter (line-length: 88)",
                "docstrings": "Google-style format",
                "type_hints": "Required for public functions",
            }
        elif language == "Node.js":
            guidelines = {
                "naming": "camelCase for variables/functions, PascalCase for classes",
                "formatting": "Prettier formatter",
                "docstrings": "JSDoc format",
                "linting": "ESLint with standard rules",
            }
        elif language == "Go":
            guidelines = {
                "naming": "camelCase for unexported, CamelCase for exported",
                "formatting": "gofmt",
                "error_handling": "Explicit if err != nil",
                "comments": "Explain why, not what",
            }
        elif language == "Rust":
            guidelines = {
                "naming": "snake_case for functions/variables, CamelCase for types",
                "formatting": "rustfmt",
                "ownership": "Respect Rust's ownership rules",
                "error_handling": "Use Result and Option types",
            }

        return guidelines

    def _generate_project_structure(self) -> str:
        """Generate ASCII representation of project structure."""
        lines: List[str] = [self.project_root.name + "/"]
        self._build_tree_lines(self.project_root, lines, "", max_depth=3)
        return "\n".join(lines[:20])  # Limit to 20 lines

    def _build_tree_lines(
        self,
        path: Path,
        lines: List[str],
        prefix: str,
        depth: int = 0,
        max_depth: int = 3,
    ) -> None:
        """Recursively build tree structure."""
        if depth >= max_depth:
            return

        try:
            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            # Skip hidden files and common ignore patterns
            items = [
                item
                for item in items
                if not item.name.startswith(".")
                and item.name not in ["__pycache__", "node_modules", ".git"]
            ]

            for i, item in enumerate(items[:10]):  # Limit to 10 items per directory
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    self._build_tree_lines(
                        item, lines, prefix + extension, depth + 1, max_depth
                    )
        except PermissionError:
            pass

    def _identify_protected_directories(self) -> List[str]:
        """Identify directories that should be protected from modification."""
        protected: List[str] = []

        # Common protected directories
        for dirname in ["legacy", "vendor", ".git", "build", "dist", "node_modules"]:
            if (self.project_root / dirname).exists():
                protected.append(dirname)

        return protected

    def _extract_additional_info(self, language: str) -> Dict[str, Any]:
        """Extract additional language-specific information."""
        info: Dict[str, Any] = {}

        if language == "Python":
            pyproject = self.project_root / "pyproject.toml"
            if pyproject.exists():
                info["python_version"] = "3.8+"
                info["package_manager"] = "pip or poetry"

        elif language == "Node.js":
            package_json = self.project_root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                        info["node_version"] = data.get("engines", {}).get(
                            "node", "14.0+"
                        )
                        info["package_manager"] = (
                            "npm"
                            if (self.project_root / "package-lock.json").exists()
                            else (
                                "yarn"
                                if (self.project_root / "yarn.lock").exists()
                                else "npm"
                            )
                        )
                except (json.JSONDecodeError, IOError):
                    pass

        return info
