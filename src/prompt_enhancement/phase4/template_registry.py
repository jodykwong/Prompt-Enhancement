"""
TemplateRegistry - Manages AGENTS.md templates for different project types.

This module provides a registry of AGENTS.md templates for various programming
languages and frameworks, making it easy to extend support for new project types.

Phase 4 Task: AGENTS.md Template Creation
"""

import logging
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Supported template types for AGENTS.md generation."""
    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"
    MULTI_LANGUAGE = "multi_language"


@dataclass
class AgentsTemplate:
    """Represents an AGENTS.md template."""
    template_type: TemplateType
    name: str
    description: str
    template_content: str
    placeholders: Dict[str, str]  # key -> description of what to fill


class TemplateRegistry:
    """
    Manages AGENTS.md templates for different project types.

    This registry allows registration and retrieval of templates based on
    project type detection results. Templates can be customized per language
    and framework.

    Attributes:
        _templates: Dictionary mapping TemplateType to AgentsTemplate
    """

    def __init__(self):
        """Initialize the template registry with built-in templates."""
        self._templates: Dict[TemplateType, AgentsTemplate] = {}
        self._register_builtin_templates()

    def _register_builtin_templates(self) -> None:
        """Register all built-in templates."""
        self._register_python_template()
        self._register_nodejs_template()
        self._register_go_template()
        self._register_rust_template()
        self._register_java_template()
        self._register_csharp_template()
        self._register_multi_language_template()

    def register_template(self, template_type: TemplateType, template: AgentsTemplate) -> None:
        """
        Register a custom template.

        Args:
            template_type: Type of template to register
            template: The template to register
        """
        self._templates[template_type] = template
        logger.info(f"Registered template for {template_type.value}")

    def get_template(self, template_type: TemplateType) -> Optional[AgentsTemplate]:
        """
        Get a template by type.

        Args:
            template_type: Type of template to retrieve

        Returns:
            AgentsTemplate if found, None otherwise
        """
        return self._templates.get(template_type)

    def _register_python_template(self) -> None:
        """Register Python project template."""
        template_content = '''# {PROJECT_NAME} - Development Guidelines

## Overview

{PROJECT_DESCRIPTION}

## Setup & Installation

### Prerequisites
- Python {PYTHON_VERSION}
- pip or poetry

### Installation Steps

```bash
{SETUP_COMMAND}
```

## Development Commands

### Testing
```bash
{TEST_COMMAND}
```

### Running the Application
```bash
{RUN_COMMAND}
```

### Code Quality
```bash
{LINT_COMMAND}
{TYPE_CHECK_COMMAND}
```

## Code Style Guidelines

### Language & Tools
- **Language**: Python {PYTHON_VERSION}+
- **Package Manager**: {PACKAGE_MANAGER}
- **Code Formatter**: {CODE_FORMATTER}
- **Type Checker**: {TYPE_CHECKER}
- **Linter**: {LINTER}

### Naming Conventions
- Functions & variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### Code Standards
- Line Length: {LINE_LENGTH} characters
- Docstring Style: Google-style format
- Type Hints: Required for all public functions
- Imports: Organized by standard, third-party, local

## Project Structure

```
{PROJECT_STRUCTURE}
```

## Key Directories

- **{SRC_DIR}**: Main source code
- **{TESTS_DIR}**: Test files
- **{DOCS_DIR}**: Documentation

## Boundaries & Constraints

### Never Modify Without Approval
- {PROTECTED_DIRS}

### Deprecated Areas
- {DEPRECATED_AREAS}

### Requires Special Permission
- Database migrations
- Security-related changes
- API contract modifications

## Testing Requirements

### Standards
- Minimum coverage: {MIN_COVERAGE}%
- All public APIs must be tested
- Integration tests for workflows
- Performance benchmarks for critical paths

### Running Tests
```bash
{TEST_COVERAGE_COMMAND}
```

## Common Patterns

### {PATTERN_1_NAME}
{PATTERN_1_DESCRIPTION}

```python
{PATTERN_1_EXAMPLE}
```

### {PATTERN_2_NAME}
{PATTERN_2_DESCRIPTION}

```python
{PATTERN_2_EXAMPLE}
```

## Git Workflow

### Commit Message Format
Follow Angular convention:
- `feat: add new feature`
- `fix: fix bug`
- `docs: update documentation`
- `test: add or update tests`
- `refactor: refactor code`

### Branch Naming
- `feature/feature-name` for new features
- `fix/bug-name` for bug fixes
- `docs/doc-name` for documentation

## Dependencies

See `{REQUIREMENTS_FILE}` for complete dependencies list.

### Key Dependencies
- {DEPENDENCY_1}: {DEPENDENCY_1_PURPOSE}
- {DEPENDENCY_2}: {DEPENDENCY_2_PURPOSE}

## Support & Troubleshooting

### Common Issues

**Issue**: Import errors when running tests
**Solution**: Run `{SETUP_COMMAND}` to install all dependencies

**Issue**: Type checking failures
**Solution**: Ensure all function signatures include type hints

### Getting Help

- Check existing issues: See GitHub issues
- Documentation: See {DOCS_DIR} directory
- Run tests in verbose mode: `{TEST_VERBOSE_COMMAND}`

## Version & Release Info

- **Current Version**: {VERSION}
- **Last Updated**: {LAST_UPDATED}
- **Python Version**: {PYTHON_VERSION}

---

**Note**: This file is auto-generated by Prompt Enhancement Phase 4.
Keep it updated as project structure and conventions evolve.
'''

        template = AgentsTemplate(
            template_type=TemplateType.PYTHON,
            name="Python Project",
            description="Template for Python projects",
            template_content=template_content,
            placeholders={
                "PROJECT_NAME": "Name of the project",
                "PROJECT_DESCRIPTION": "Brief description of project",
                "PYTHON_VERSION": "Minimum Python version (e.g., 3.9)",
                "SETUP_COMMAND": "Installation command (e.g., pip install -r requirements.txt)",
                "TEST_COMMAND": "Test running command",
                "RUN_COMMAND": "Application run command",
                "LINT_COMMAND": "Linting command",
                "TYPE_CHECK_COMMAND": "Type checking command",
                "PACKAGE_MANAGER": "Package manager (pip, poetry, etc.)",
                "CODE_FORMATTER": "Code formatter (black, autopep8, etc.)",
                "TYPE_CHECKER": "Type checker (mypy, pyright, etc.)",
                "LINTER": "Linter tool (flake8, pylint, etc.)",
                "LINE_LENGTH": "Max line length (e.g., 88)",
                "PROJECT_STRUCTURE": "ASCII representation of project structure",
                "SRC_DIR": "Source directory name",
                "TESTS_DIR": "Tests directory name",
                "DOCS_DIR": "Documentation directory name",
                "PROTECTED_DIRS": "Directories that should not be modified",
                "DEPRECATED_AREAS": "Deprecated code or modules",
                "MIN_COVERAGE": "Minimum test coverage percentage",
                "TEST_COVERAGE_COMMAND": "Command to check test coverage",
                "PATTERN_1_NAME": "Name of common pattern 1",
                "PATTERN_1_DESCRIPTION": "Description of pattern 1",
                "PATTERN_1_EXAMPLE": "Code example of pattern 1",
                "PATTERN_2_NAME": "Name of common pattern 2",
                "PATTERN_2_DESCRIPTION": "Description of pattern 2",
                "PATTERN_2_EXAMPLE": "Code example of pattern 2",
                "REQUIREMENTS_FILE": "Requirements file name",
                "DEPENDENCY_1": "First key dependency",
                "DEPENDENCY_1_PURPOSE": "Purpose of dependency 1",
                "DEPENDENCY_2": "Second key dependency",
                "DEPENDENCY_2_PURPOSE": "Purpose of dependency 2",
                "TEST_VERBOSE_COMMAND": "Verbose test command",
                "VERSION": "Current version",
                "LAST_UPDATED": "Last update date",
            }
        )
        self.register_template(TemplateType.PYTHON, template)

    def _register_nodejs_template(self) -> None:
        """Register Node.js project template."""
        template_content = '''# {PROJECT_NAME} - Development Guidelines

## Overview

{PROJECT_DESCRIPTION}

## Setup & Installation

### Prerequisites
- Node.js {NODE_VERSION}
- npm {NPM_VERSION} or {PACKAGE_MANAGER}

### Installation Steps

```bash
{SETUP_COMMAND}
```

## Development Commands

### Running Development Server
```bash
{DEV_COMMAND}
```

### Building for Production
```bash
{BUILD_COMMAND}
```

### Testing
```bash
{TEST_COMMAND}
```

### Code Quality
```bash
{LINT_COMMAND}
{FORMAT_COMMAND}
```

## Code Style Guidelines

### Language & Tools
- **Runtime**: Node.js {NODE_VERSION}+
- **Package Manager**: {PACKAGE_MANAGER}
- **Code Formatter**: {CODE_FORMATTER}
- **Linter**: {LINTER}
- **Testing Framework**: {TEST_FRAMEWORK}

### Naming Conventions
- Functions & variables: `camelCase`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Files: `kebab-case` (for components), `camelCase` (for modules)

### Code Standards
- Line Length: {LINE_LENGTH} characters
- Semicolons: {SEMICOLON_REQUIREMENT}
- Quotes: {QUOTE_STYLE}
- Indentation: {INDENTATION}
- Arrow Functions: Preferred over function expressions

## Project Structure

```
{PROJECT_STRUCTURE}
```

## Key Directories

- **{SRC_DIR}**: Source code
- **{TESTS_DIR}**: Test files
- **{DIST_DIR}**: Build output
- **{DOCS_DIR}**: Documentation

## Boundaries & Constraints

### Never Modify Without Approval
- {PROTECTED_DIRS}

### Deprecated Code
- {DEPRECATED_AREAS}

### Requires Special Permission
- Database migrations
- Security-related changes
- API contract modifications
- Dependency upgrades

## Testing Requirements

### Standards
- Minimum coverage: {MIN_COVERAGE}%
- Unit tests for all utilities
- Integration tests for workflows
- E2E tests for critical user paths

### Running Tests
```bash
{TEST_COVERAGE_COMMAND}
```

## Common Patterns

### {PATTERN_1_NAME}
{PATTERN_1_DESCRIPTION}

```javascript
{PATTERN_1_EXAMPLE}
```

### {PATTERN_2_NAME}
{PATTERN_2_DESCRIPTION}

```javascript
{PATTERN_2_EXAMPLE}
```

## Git Workflow

### Commit Message Format
Follow Angular convention:
- `feat: add new feature`
- `fix: fix bug`
- `docs: update documentation`
- `test: add or update tests`
- `refactor: refactor code`

### Branch Naming
- `feature/feature-name` for new features
- `fix/bug-name` for bug fixes
- `release/version-number` for releases

## Environment Variables

See `.env.example` for template.

### Required Variables
- {ENV_VAR_1}: {ENV_VAR_1_PURPOSE}
- {ENV_VAR_2}: {ENV_VAR_2_PURPOSE}

## Dependencies

See `package.json` for complete dependencies list.

### Key Dependencies
- {DEPENDENCY_1}: {DEPENDENCY_1_PURPOSE}
- {DEPENDENCY_2}: {DEPENDENCY_2_PURPOSE}

## Build & Deployment

### Production Build
```bash
{BUILD_COMMAND}
```

### Environment-Specific Configuration
- Development: Uses `.env.development`
- Production: Uses `.env.production`

## Support & Troubleshooting

### Common Issues

**Issue**: Dependency conflicts
**Solution**: Delete `node_modules` and `{LOCK_FILE}`, run `{INSTALL_COMMAND}`

**Issue**: Port already in use
**Solution**: Kill process on port {DEFAULT_PORT} or set PORT environment variable

### Getting Help

- Check package.json scripts for available commands
- Run `{DEV_COMMAND}` to start development server
- Check GitHub issues for known problems

## Version & Release Info

- **Current Version**: {VERSION}
- **Node Version**: {NODE_VERSION}
- **Last Updated**: {LAST_UPDATED}

---

**Note**: This file is auto-generated by Prompt Enhancement Phase 4.
Keep it updated as project requirements and conventions evolve.
'''

        template = AgentsTemplate(
            template_type=TemplateType.NODEJS,
            name="Node.js Project",
            description="Template for Node.js projects",
            template_content=template_content,
            placeholders={
                "PROJECT_NAME": "Name of the project",
                "PROJECT_DESCRIPTION": "Brief description of project",
                "NODE_VERSION": "Minimum Node.js version",
                "NPM_VERSION": "Minimum npm version",
                "PACKAGE_MANAGER": "Package manager (npm, yarn, pnpm)",
                "SETUP_COMMAND": "Installation command",
                "DEV_COMMAND": "Development server command",
                "BUILD_COMMAND": "Build command",
                "TEST_COMMAND": "Test running command",
                "LINT_COMMAND": "Linting command",
                "FORMAT_COMMAND": "Code formatting command",
                "CODE_FORMATTER": "Formatter tool (prettier, etc.)",
                "LINTER": "Linter tool (eslint, etc.)",
                "TEST_FRAMEWORK": "Testing framework (jest, vitest, mocha, etc.)",
                "LINE_LENGTH": "Max line length",
                "SEMICOLON_REQUIREMENT": "Semicolon usage requirement",
                "QUOTE_STYLE": "Quote style (single or double)",
                "INDENTATION": "Indentation size/style",
                "PROJECT_STRUCTURE": "ASCII project structure",
                "SRC_DIR": "Source directory",
                "TESTS_DIR": "Tests directory",
                "DIST_DIR": "Distribution directory",
                "DOCS_DIR": "Documentation directory",
                "PROTECTED_DIRS": "Protected directories",
                "DEPRECATED_AREAS": "Deprecated code",
                "MIN_COVERAGE": "Minimum coverage percentage",
                "TEST_COVERAGE_COMMAND": "Coverage check command",
                "PATTERN_1_NAME": "Pattern 1 name",
                "PATTERN_1_DESCRIPTION": "Pattern 1 description",
                "PATTERN_1_EXAMPLE": "Pattern 1 code",
                "PATTERN_2_NAME": "Pattern 2 name",
                "PATTERN_2_DESCRIPTION": "Pattern 2 description",
                "PATTERN_2_EXAMPLE": "Pattern 2 code",
                "ENV_VAR_1": "Environment variable 1",
                "ENV_VAR_1_PURPOSE": "Purpose of env var 1",
                "ENV_VAR_2": "Environment variable 2",
                "ENV_VAR_2_PURPOSE": "Purpose of env var 2",
                "DEPENDENCY_1": "Key dependency 1",
                "DEPENDENCY_1_PURPOSE": "Purpose of dependency 1",
                "DEPENDENCY_2": "Key dependency 2",
                "DEPENDENCY_2_PURPOSE": "Purpose of dependency 2",
                "DEFAULT_PORT": "Default development port",
                "INSTALL_COMMAND": "Install dependencies command",
                "LOCK_FILE": "Lock file name (package-lock.json, yarn.lock, etc.)",
                "VERSION": "Current version",
                "LAST_UPDATED": "Last update date",
            }
        )
        self.register_template(TemplateType.NODEJS, template)

    def _register_go_template(self) -> None:
        """Register Go project template."""
        template_content = '''# {PROJECT_NAME} - Development Guidelines

## Overview

{PROJECT_DESCRIPTION}

## Setup & Installation

### Prerequisites
- Go {GO_VERSION}
- {ADDITIONAL_TOOLS}

### Installation Steps

```bash
{SETUP_COMMAND}
```

## Development Commands

### Building
```bash
{BUILD_COMMAND}
```

### Running
```bash
{RUN_COMMAND}
```

### Testing
```bash
{TEST_COMMAND}
```

### Code Quality
```bash
{LINT_COMMAND}
{FORMAT_COMMAND}
```

## Code Style Guidelines

### Language & Tools
- **Go Version**: {GO_VERSION}+
- **Code Formatter**: {CODE_FORMATTER}
- **Linter**: {LINTER}
- **Testing**: Built-in `testing` package

### Naming Conventions
- Functions & variables: `camelCase`
- Constants: `CamelCase` or `UPPER_CASE`
- Unexported: `lowerCamelCase`
- Exported: `UpperCamelCase`

### Code Standards
- Line Length: {LINE_LENGTH} characters
- Error handling: Explicit with `if err != nil`
- Interfaces: Small and focused
- Comments: Explain why, not what

## Project Structure

```
{PROJECT_STRUCTURE}
```

## Key Directories

- **{SRC_DIR}**: Main source code
- **{TESTS_DIR}**: Test files
- **{CMD_DIR}**: Command-line tools
- **{DOCS_DIR}**: Documentation

## Boundaries & Constraints

### Never Modify Without Approval
- {PROTECTED_DIRS}

### Deprecated Packages
- {DEPRECATED_AREAS}

### Requires Special Permission
- Database schema changes
- Security-related changes
- Public API modifications

## Testing Requirements

### Standards
- Coverage: {MIN_COVERAGE}%
- Table-driven tests for multiple cases
- Benchmark tests for performance-critical code
- Integration tests for workflows

### Running Tests
```bash
{TEST_COVERAGE_COMMAND}
```

## Dependencies

See `go.mod` for complete dependencies.

### Key Dependencies
- {DEPENDENCY_1}: {DEPENDENCY_1_PURPOSE}
- {DEPENDENCY_2}: {DEPENDENCY_2_PURPOSE}

## Git Workflow

### Commit Message Format
Follow Angular convention:
- `feat: add new feature`
- `fix: fix bug`
- `docs: update documentation`
- `test: add or update tests`
- `refactor: refactor code`

### Branch Naming
- `feature/feature-name` for new features
- `fix/bug-name` for bug fixes
- `release/version` for releases

## Build & Deployment

### Cross-platform Build
```bash
GOOS=linux GOARCH=amd64 go build -o {BINARY_NAME}
GOOS=darwin GOARCH=arm64 go build -o {BINARY_NAME}
```

### Static Analysis
```bash
{LINT_COMMAND}
```

## Common Patterns

### Error Handling
```go
{ERROR_PATTERN_EXAMPLE}
```

### Interface Design
```go
{INTERFACE_PATTERN_EXAMPLE}
```

## Support & Troubleshooting

### Common Issues

**Issue**: Module not found
**Solution**: Run `go mod tidy` to sync dependencies

**Issue**: Build fails on different OS
**Solution**: Use `GOOS=target` and `GOARCH=target` flags

### Getting Help

- Go Documentation: https://golang.org/doc
- Go Forum: https://forum.golangbridge.org
- Project Issues: Check GitHub issues

## Version & Release Info

- **Current Version**: {VERSION}
- **Go Version**: {GO_VERSION}
- **Last Updated**: {LAST_UPDATED}

---

**Note**: This file is auto-generated by Prompt Enhancement Phase 4.
'''

        template = AgentsTemplate(
            template_type=TemplateType.GO,
            name="Go Project",
            description="Template for Go projects",
            template_content=template_content,
            placeholders={
                "PROJECT_NAME": "Name of the project",
                "PROJECT_DESCRIPTION": "Brief description",
                "GO_VERSION": "Minimum Go version",
                "ADDITIONAL_TOOLS": "Additional required tools",
                "SETUP_COMMAND": "Setup command",
                "BUILD_COMMAND": "Build command",
                "RUN_COMMAND": "Run command",
                "TEST_COMMAND": "Test command",
                "LINT_COMMAND": "Lint command",
                "FORMAT_COMMAND": "Format command",
                "CODE_FORMATTER": "Formatter (gofmt, etc.)",
                "LINTER": "Linter (golangci-lint, etc.)",
                "LINE_LENGTH": "Max line length",
                "PROJECT_STRUCTURE": "ASCII structure",
                "SRC_DIR": "Source directory",
                "TESTS_DIR": "Tests directory",
                "CMD_DIR": "Commands directory",
                "DOCS_DIR": "Documentation directory",
                "PROTECTED_DIRS": "Protected directories",
                "DEPRECATED_AREAS": "Deprecated code",
                "MIN_COVERAGE": "Min coverage percentage",
                "TEST_COVERAGE_COMMAND": "Coverage command",
                "DEPENDENCY_1": "Dependency 1",
                "DEPENDENCY_1_PURPOSE": "Dependency 1 purpose",
                "DEPENDENCY_2": "Dependency 2",
                "DEPENDENCY_2_PURPOSE": "Dependency 2 purpose",
                "BINARY_NAME": "Binary name",
                "ERROR_PATTERN_EXAMPLE": "Error handling example",
                "INTERFACE_PATTERN_EXAMPLE": "Interface pattern example",
                "VERSION": "Current version",
                "LAST_UPDATED": "Last update",
            }
        )
        self.register_template(TemplateType.GO, template)

    def _register_rust_template(self) -> None:
        """Register Rust project template."""
        template = AgentsTemplate(
            template_type=TemplateType.RUST,
            name="Rust Project",
            description="Template for Rust projects",
            template_content="# {PROJECT_NAME} - Development Guidelines\n\n## Setup & Installation\n\n```bash\n{SETUP_COMMAND}\n```\n\n## Development Commands\n\n```bash\n{TEST_COMMAND}\n{BUILD_COMMAND}\n{RUN_COMMAND}\n```\n\n## Code Standards\n\n- Rust {RUST_VERSION}+\n- Use `cargo fmt` for formatting\n- Use `clippy` for linting\n- 100% coverage for public APIs\n\n## Boundaries\n\n- Never modify: {PROTECTED_DIRS}\n- Requires approval: Security changes\n",
            placeholders={
                "PROJECT_NAME": "Project name",
                "SETUP_COMMAND": "Setup command",
                "TEST_COMMAND": "Test command",
                "BUILD_COMMAND": "Build command",
                "RUN_COMMAND": "Run command",
                "RUST_VERSION": "Rust version",
                "PROTECTED_DIRS": "Protected directories",
            }
        )
        self.register_template(TemplateType.RUST, template)

    def _register_java_template(self) -> None:
        """Register Java project template."""
        template = AgentsTemplate(
            template_type=TemplateType.JAVA,
            name="Java Project",
            description="Template for Java projects",
            template_content="# {PROJECT_NAME} - Development Guidelines\n\n## Setup & Installation\n\n```bash\n{SETUP_COMMAND}\n```\n\n## Development Commands\n\n```bash\n{TEST_COMMAND}\n{BUILD_COMMAND}\n{RUN_COMMAND}\n```\n\n## Code Standards\n\n- Java {JAVA_VERSION}+\n- Maven/Gradle: {BUILD_TOOL}\n- Code style: Google Java Style Guide\n- Naming: camelCase for methods, PascalCase for classes\n\n## Boundaries\n\n- Never modify: {PROTECTED_DIRS}\n- Requires approval: {APPROVAL_REQUIRED}\n",
            placeholders={
                "PROJECT_NAME": "Project name",
                "SETUP_COMMAND": "Setup command",
                "TEST_COMMAND": "Test command",
                "BUILD_COMMAND": "Build command",
                "RUN_COMMAND": "Run command",
                "JAVA_VERSION": "Java version",
                "BUILD_TOOL": "Build tool (Maven/Gradle)",
                "PROTECTED_DIRS": "Protected directories",
                "APPROVAL_REQUIRED": "Approval required areas",
            }
        )
        self.register_template(TemplateType.JAVA, template)

    def _register_csharp_template(self) -> None:
        """Register C# project template."""
        template = AgentsTemplate(
            template_type=TemplateType.CSHARP,
            name="C# Project",
            description="Template for C# projects",
            template_content="# {PROJECT_NAME} - Development Guidelines\n\n## Setup & Installation\n\n```bash\n{SETUP_COMMAND}\n```\n\n## Development Commands\n\n```bash\n{TEST_COMMAND}\n{BUILD_COMMAND}\n{RUN_COMMAND}\n```\n\n## Code Standards\n\n- .NET {DOTNET_VERSION}+\n- C# {CSHARP_VERSION}+\n- Code style: Microsoft C# Coding Conventions\n- Naming: PascalCase for public members, _camelCase for private\n\n## Boundaries\n\n- Never modify: {PROTECTED_DIRS}\n",
            placeholders={
                "PROJECT_NAME": "Project name",
                "SETUP_COMMAND": "Setup command",
                "TEST_COMMAND": "Test command",
                "BUILD_COMMAND": "Build command",
                "RUN_COMMAND": "Run command",
                "DOTNET_VERSION": ".NET version",
                "CSHARP_VERSION": "C# version",
                "PROTECTED_DIRS": "Protected directories",
            }
        )
        self.register_template(TemplateType.CSHARP, template)

    def _register_multi_language_template(self) -> None:
        """Register multi-language project template."""
        template = AgentsTemplate(
            template_type=TemplateType.MULTI_LANGUAGE,
            name="Multi-Language Project",
            description="Template for projects with multiple languages",
            template_content="# {PROJECT_NAME} - Development Guidelines\n\n## Overview\n\nThis is a multi-language project using:\n- {LANGUAGES}\n\n## Setup & Installation\n\n```bash\n{SETUP_COMMAND}\n```\n\n## Development Commands\n\n```bash\n{TEST_COMMAND}\n{BUILD_COMMAND}\n{RUN_COMMAND}\n```\n\n## Per-Language Guidelines\n\n### {LANGUAGE_1}\n{LANGUAGE_1_GUIDELINES}\n\n### {LANGUAGE_2}\n{LANGUAGE_2_GUIDELINES}\n\n## Boundaries\n\n- Never modify: {PROTECTED_DIRS}\n",
            placeholders={
                "PROJECT_NAME": "Project name",
                "LANGUAGES": "List of languages",
                "SETUP_COMMAND": "Setup command",
                "TEST_COMMAND": "Test command",
                "BUILD_COMMAND": "Build command",
                "RUN_COMMAND": "Run command",
                "LANGUAGE_1": "First language",
                "LANGUAGE_1_GUIDELINES": "Guidelines for language 1",
                "LANGUAGE_2": "Second language",
                "LANGUAGE_2_GUIDELINES": "Guidelines for language 2",
                "PROTECTED_DIRS": "Protected directories",
            }
        )
        self.register_template(TemplateType.MULTI_LANGUAGE, template)

    def list_templates(self) -> Dict[str, str]:
        """
        List all available templates.

        Returns:
            Dictionary mapping template type names to descriptions
        """
        return {
            tpl.template_type.value: tpl.description
            for tpl in self._templates.values()
        }
