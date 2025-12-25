"""
AgentsTemplateGenerator - Generates AGENTS.md content from templates and project info.

This module combines template selection, content extraction, and template
filling to generate complete AGENTS.md content for a project.

Phase 4 Task: AGENTS.md Generation
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .template_registry import TemplateRegistry, TemplateType
from .content_extractor import ContentExtractor, ProjectInfo
from ..pipeline.tech_stack import ProjectTypeDetector, ProjectLanguage

logger = logging.getLogger(__name__)


class AgentsTemplateGenerator:
    """
    Generates AGENTS.md content from templates and project information.

    This class orchestrates the process of:
    1. Detecting project type using existing tech stack detector
    2. Selecting appropriate template from registry
    3. Extracting project information
    4. Filling template placeholders with extracted values

    Attributes:
        project_root: Root directory of the project
        template_registry: Registry of available templates
        tech_detector: Tech stack detector instance
        content_extractor: Content extraction instance
    """

    def __init__(self, project_root: str):
        """
        Initialize the template generator.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.template_registry = TemplateRegistry()
        self.tech_detector = ProjectTypeDetector(project_root)
        self.content_extractor = ContentExtractor(project_root)

    def generate_agents_md(self) -> str:
        """
        Generate AGENTS.md content.

        Process:
        1. Detect project type using tech stack detector
        2. Select appropriate template
        3. Extract project information
        4. Fill template with extracted values

        Returns:
            Generated AGENTS.md content as string
        """
        # Detect project type
        project_info = self.content_extractor.extract_info()

        # Select template based on language
        template_type = self._map_language_to_template(project_info.primary_language)
        template = self.template_registry.get_template(template_type)

        if not template:
            logger.warning(
                f"No template found for {template_type}, using generic template"
            )
            template = self._create_generic_template()

        # Generate content by filling placeholders
        content = self._fill_template(template.template_content, project_info)

        logger.info(f"Generated AGENTS.md for {project_info.name}")
        return content

    def _map_language_to_template(self, language: str) -> TemplateType:
        """
        Map detected language to template type.

        Args:
            language: Detected language name

        Returns:
            Corresponding TemplateType
        """
        mapping = {
            "Python": TemplateType.PYTHON,
            "Node.js": TemplateType.NODEJS,
            "Go": TemplateType.GO,
            "Rust": TemplateType.RUST,
            "Java": TemplateType.JAVA,
            "C#": TemplateType.CSHARP,
        }
        return mapping.get(language, TemplateType.PYTHON)

    def _fill_template(self, template: str, project_info: ProjectInfo) -> str:
        """
        Fill template placeholders with project information.

        Args:
            template: Template content with placeholders
            project_info: Extracted project information

        Returns:
            Filled template with actual values
        """
        # Build placeholder dictionary
        placeholders = self._build_placeholder_dict(project_info)

        # Replace placeholders
        result = template
        for key, value in placeholders.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, value or "N/A")

        return result

    def _build_placeholder_dict(self, project_info: ProjectInfo) -> Dict[str, str]:
        """
        Build dictionary of placeholders to values.

        Args:
            project_info: Extracted project information

        Returns:
            Dictionary mapping placeholder names to values
        """
        return {
            # Basic info
            "PROJECT_NAME": project_info.name,
            "PROJECT_DESCRIPTION": project_info.description,
            "VERSION": project_info.version,
            "LAST_UPDATED": datetime.now().strftime("%Y-%m-%d"),
            # Language-specific versions
            "PYTHON_VERSION": project_info.additional_info.get(
                "python_version", "3.8+"
            ),
            "NODE_VERSION": project_info.additional_info.get("node_version", "14.0+"),
            "GO_VERSION": "1.16+",
            "RUST_VERSION": "1.56+",
            "JAVA_VERSION": "11+",
            "CSHARP_VERSION": "9.0+",
            "DOTNET_VERSION": "6.0+",
            # Commands
            "SETUP_COMMAND": project_info.setup_command or "N/A",
            "TEST_COMMAND": project_info.test_command or "N/A",
            "RUN_COMMAND": project_info.run_command or "N/A",
            "BUILD_COMMAND": project_info.build_command or "N/A",
            "LINT_COMMAND": project_info.lint_command or "N/A",
            "FORMAT_COMMAND": project_info.format_command or "N/A",
            "TYPE_CHECK_COMMAND": project_info.type_check_command or "N/A",
            "DEV_COMMAND": "npm run dev",
            "TEST_VERBOSE_COMMAND": (
                project_info.test_command.replace("-v", "-vv")
                if project_info.test_command
                else "N/A"
            ),
            "TEST_COVERAGE_COMMAND": (
                f"{project_info.test_command} --cov"
                if project_info.test_command
                else "N/A"
            ),
            # Package managers
            "PACKAGE_MANAGER": project_info.additional_info.get(
                "package_manager", "npm"
            ),
            "NPM_VERSION": "7.0+",
            "CODE_FORMATTER": self._detect_code_formatter(
                project_info.primary_language
            ),
            "TYPE_CHECKER": self._detect_type_checker(project_info.primary_language),
            "LINTER": self._detect_linter(project_info.primary_language),
            "TEST_FRAMEWORK": self._detect_test_framework(
                project_info.primary_language
            ),
            # Code style
            "LINE_LENGTH": "88" if project_info.primary_language == "Python" else "100",
            "INDENTATION": (
                "2 spaces" if "Node" in project_info.primary_language else "4 spaces"
            ),
            "SEMICOLON_REQUIREMENT": (
                "Required" if "Node" in project_info.primary_language else "N/A"
            ),
            "QUOTE_STYLE": (
                "Double quotes"
                if "Node" in project_info.primary_language
                else "Single or double"
            ),
            # Project structure
            "PROJECT_STRUCTURE": project_info.project_structure,
            "SRC_DIR": "src" if "Node" in project_info.primary_language else "src",
            "TESTS_DIR": (
                "tests" if "Python" in project_info.primary_language else "test"
            ),
            "DIST_DIR": "dist" if "Node" in project_info.primary_language else "build",
            "DOCS_DIR": "docs",
            "CMD_DIR": "cmd",
            # Boundaries
            "PROTECTED_DIRS": ", ".join(project_info.protected_directories)
            or "legacy, vendor",
            "DEPRECATED_AREAS": "old_api, legacy_module",
            "APPROVAL_REQUIRED": "Database migrations, security changes",
            # Testing
            "MIN_COVERAGE": "80",
            "INSTALL_COMMAND": "npm install",
            "LOCK_FILE": "package-lock.json",
            "DEFAULT_PORT": "3000",
            # Dependencies
            "DEPENDENCY_1": (
                project_info.main_dependencies[0]
                if project_info.main_dependencies
                else "requests"
            ),
            "DEPENDENCY_1_PURPOSE": "HTTP library",
            "DEPENDENCY_2": (
                project_info.main_dependencies[1]
                if len(project_info.main_dependencies) > 1
                else "pytest"
            ),
            "DEPENDENCY_2_PURPOSE": "Testing framework",
            # Patterns
            "PATTERN_1_NAME": "Error Handling",
            "PATTERN_1_DESCRIPTION": "Standard way to handle errors",
            "PATTERN_1_EXAMPLE": self._get_error_pattern_example(
                project_info.primary_language
            ),
            "PATTERN_2_NAME": "Function Documentation",
            "PATTERN_2_DESCRIPTION": "Standard documentation format",
            "PATTERN_2_EXAMPLE": self._get_doc_pattern_example(
                project_info.primary_language
            ),
            # Additional
            "ADDITIONAL_TOOLS": "Git",
            "REQUIREMENTS_FILE": "requirements.txt",
            "ENV_VAR_1": "API_KEY",
            "ENV_VAR_1_PURPOSE": "API authentication key",
            "ENV_VAR_2": "DEBUG",
            "ENV_VAR_2_PURPOSE": "Debug mode flag",
            "ERROR_PATTERN_EXAMPLE": self._get_error_pattern_example(
                project_info.primary_language
            ),
            "INTERFACE_PATTERN_EXAMPLE": self._get_interface_pattern_example(
                project_info.primary_language
            ),
            "BINARY_NAME": project_info.name.lower().replace(" ", "_"),
            "LANGUAGES": project_info.primary_language,
            "LANGUAGE_1": project_info.primary_language,
            "LANGUAGE_1_GUIDELINES": f"Follow {project_info.primary_language} standard conventions",
            "LANGUAGE_2": (
                "TypeScript" if "Node" in project_info.primary_language else "Go"
            ),
            "LANGUAGE_2_GUIDELINES": "Follow community best practices",
        }

    def _detect_code_formatter(self, language: str) -> str:
        """Detect code formatter based on language."""
        formatters = {
            "Python": "Black",
            "Node.js": "Prettier",
            "Go": "gofmt",
            "Rust": "rustfmt",
            "Java": "Google Java Format",
            "C#": ".editorconfig",
        }
        return formatters.get(language, "Standard formatter")

    def _detect_type_checker(self, language: str) -> str:
        """Detect type checker based on language."""
        checkers = {
            "Python": "mypy",
            "Node.js": "TypeScript",
            "Go": "Built-in",
            "Rust": "Built-in",
            "Java": "Built-in",
            "C#": "Built-in",
        }
        return checkers.get(language, "N/A")

    def _detect_linter(self, language: str) -> str:
        """Detect linter based on language."""
        linters = {
            "Python": "flake8 or pylint",
            "Node.js": "ESLint",
            "Go": "golangci-lint",
            "Rust": "clippy",
            "Java": "Checkstyle",
            "C#": "Roslyn",
        }
        return linters.get(language, "Standard linter")

    def _detect_test_framework(self, language: str) -> str:
        """Detect test framework based on language."""
        frameworks = {
            "Python": "pytest",
            "Node.js": "Jest or Mocha",
            "Go": "testing (built-in)",
            "Rust": "cargo test",
            "Java": "JUnit",
            "C#": "xUnit or NUnit",
        }
        return frameworks.get(language, "Standard test framework")

    def _get_error_pattern_example(self, language: str) -> str:
        """Get error handling pattern example."""
        examples = {
            "Python": """try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise""",
            "Node.js": """try {
    const result = await riskyOperation();
} catch (error) {
    logger.error(`Error: ${error.message}`);
    throw error;
}""",
            "Go": """if err != nil {
    log.Printf("Error: %v", err)
    return err
}""",
            "Java": """try {
    result = riskyOperation();
} catch (IOException e) {
    logger.error("IO Error", e);
    throw new RuntimeException(e);
}""",
        }
        return examples.get(language, "# Error handling example")

    def _get_doc_pattern_example(self, language: str) -> str:
        """Get documentation pattern example."""
        examples = {
            "Python": '''def calculate(a: int, b: int) -> int:
    """
    Calculate sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b''',
            "Node.js": """/**
 * Calculate sum of two numbers.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function calculate(a, b) {
    return a + b;
}""",
            "Go": """// Calculate returns the sum of two numbers.
func Calculate(a, b int) int {
    return a + b
}""",
        }
        return examples.get(language, "// Documentation example")

    def _get_interface_pattern_example(self, language: str) -> str:
        """Get interface/protocol pattern example."""
        examples = {
            "Python": """from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def read(self) -> str:
        pass""",
            "Node.js": """interface Reader {
    read(): Promise<string>;
}""",
            "Go": """type Reader interface {
    Read() (string, error)
}""",
        }
        return examples.get(language, "// Interface example")

    def _create_generic_template(self) -> Any:
        """Create a generic template as fallback."""
        from .template_registry import AgentsTemplate

        return AgentsTemplate(
            template_type=TemplateType.PYTHON,
            name="Generic",
            description="Generic template",
            template_content="""# {PROJECT_NAME}

## Setup

{SETUP_COMMAND}

## Commands

- Test: {TEST_COMMAND}
- Run: {RUN_COMMAND}
- Build: {BUILD_COMMAND}

## Code Style

{LINE_LENGTH} character line length

## Testing

Minimum {MIN_COVERAGE}% coverage

## Boundaries

Never modify: {PROTECTED_DIRS}
""",
            placeholders={},
        )
