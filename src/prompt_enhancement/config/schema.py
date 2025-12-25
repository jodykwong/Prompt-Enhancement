"""Configuration schema and validation for standards configuration."""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Valid values for each configuration option
VALID_NAMING_CONVENTIONS = ["snake_case", "camelCase", "PascalCase", "kebab-case"]
VALID_TEST_FRAMEWORKS = [
    "pytest",
    "unittest",
    "jest",
    "mocha",
    "NUnit",
    "xUnit",
    "TestNG",
    "JUnit",
]
VALID_DOCUMENTATION_STYLES = [
    "google",
    "numpy",
    "sphinx",
    "jsdoc",
    "javadoc",
    "pep257",
]
VALID_CODE_ORGANIZATION = [
    "by-feature",
    "by-layer",
    "by-type",
    "domain-driven",
    "monolithic",
]


@dataclass
class StandardsConfig:
    """Configuration for coding standards."""

    naming_convention: Optional[str] = None
    test_framework: Optional[str] = None
    documentation_style: Optional[str] = None
    code_organization: Optional[str] = None
    module_naming_pattern: Optional[str] = None

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration values.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if self.naming_convention and self.naming_convention not in VALID_NAMING_CONVENTIONS:
            errors.append(
                f"Invalid naming_convention: {self.naming_convention}. "
                f"Valid options: {', '.join(VALID_NAMING_CONVENTIONS)}"
            )

        if self.test_framework and self.test_framework not in VALID_TEST_FRAMEWORKS:
            errors.append(
                f"Invalid test_framework: {self.test_framework}. "
                f"Valid options: {', '.join(VALID_TEST_FRAMEWORKS)}"
            )

        if (
            self.documentation_style
            and self.documentation_style not in VALID_DOCUMENTATION_STYLES
        ):
            errors.append(
                f"Invalid documentation_style: {self.documentation_style}. "
                f"Valid options: {', '.join(VALID_DOCUMENTATION_STYLES)}"
            )

        if self.code_organization and self.code_organization not in VALID_CODE_ORGANIZATION:
            errors.append(
                f"Invalid code_organization: {self.code_organization}. "
                f"Valid options: {', '.join(VALID_CODE_ORGANIZATION)}"
            )

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary."""
        return {
            "naming_convention": self.naming_convention,
            "test_framework": self.test_framework,
            "documentation_style": self.documentation_style,
            "code_organization": self.code_organization,
            "module_naming_pattern": self.module_naming_pattern,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardsConfig":
        """Create config from dictionary."""
        return cls(
            naming_convention=data.get("naming_convention"),
            test_framework=data.get("test_framework"),
            documentation_style=data.get("documentation_style"),
            code_organization=data.get("code_organization"),
            module_naming_pattern=data.get("module_naming_pattern"),
        )
