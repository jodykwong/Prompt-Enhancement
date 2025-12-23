"""Override parsing and validation for per-request standards customization."""

import logging
from typing import Dict, Optional, Tuple, List

from .schema import (
    StandardsConfig,
    VALID_NAMING_CONVENTIONS,
    VALID_TEST_FRAMEWORKS,
    VALID_DOCUMENTATION_STYLES,
    VALID_CODE_ORGANIZATION,
)

logger = logging.getLogger(__name__)

# Mapping of override keys to valid values
OVERRIDE_VALIDATORS = {
    "naming": VALID_NAMING_CONVENTIONS,
    "test_framework": VALID_TEST_FRAMEWORKS,
    "documentation": VALID_DOCUMENTATION_STYLES,
    "organization": VALID_CODE_ORGANIZATION,
    "module_naming": None,  # Accept any string
}


class OverrideParser:
    """Parses and validates --override command-line flags."""

    @staticmethod
    def parse_overrides(override_flags: List[str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Parse override flags.

        Args:
            override_flags: List of override strings (e.g., ["naming=camelCase"])

        Returns:
            Tuple of (overrides_dict, list_of_errors)
        """
        overrides = {}
        errors = []

        for override in override_flags:
            if "=" not in override:
                errors.append(f"Invalid override format: {override} (expected key=value)")
                continue

            key, value = override.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key or not value:
                errors.append(f"Invalid override: key and value cannot be empty")
                continue

            if key not in OVERRIDE_VALIDATORS:
                errors.append(f"Unknown override key: {key}")
                continue

            # Validate value if validator exists
            validator = OVERRIDE_VALIDATORS[key]
            if validator and value not in validator:
                errors.append(
                    f"Invalid value for {key}: {value}. "
                    f"Valid options: {', '.join(validator)}"
                )
                continue

            overrides[key] = value
            logger.debug(f"Parsed override: {key}={value}")

        return overrides, errors

    @staticmethod
    def apply_overrides(
        base_config: StandardsConfig,
        overrides: Dict[str, str],
    ) -> StandardsConfig:
        """
        Apply overrides to base configuration.

        Args:
            base_config: Base StandardsConfig
            overrides: Dictionary of overrides

        Returns:
            New StandardsConfig with overrides applied
        """
        # Map override keys to StandardsConfig attributes
        key_mapping = {
            "naming": "naming_convention",
            "test_framework": "test_framework",
            "documentation": "documentation_style",
            "organization": "code_organization",
            "module_naming": "module_naming_pattern",
        }

        config_dict = base_config.to_dict()

        for override_key, override_value in overrides.items():
            config_key = key_mapping.get(override_key)
            if config_key:
                config_dict[config_key] = override_value
                logger.debug(f"Applied override: {config_key}={override_value}")

        return StandardsConfig.from_dict(config_dict)

    @staticmethod
    def get_override_help() -> str:
        """Get help text for override usage."""
        return """
⚙️ Per-Request Override Options

Use --override to temporarily change standards for a single request:

  /pe --override naming=camelCase "my prompt"

Supported overrides:
  naming=<value>
    Valid: snake_case, camelCase, PascalCase, kebab-case

  test_framework=<value>
    Valid: pytest, unittest, jest, mocha, NUnit, xUnit, TestNG, JUnit

  documentation=<value>
    Valid: google, numpy, sphinx, jsdoc, javadoc, pep257

  organization=<value>
    Valid: by-feature, by-layer, by-type, domain-driven, monolithic

  module_naming=<value>
    Custom pattern (e.g., service_, models_, etc.)

Multiple overrides:
  /pe --override naming=camelCase --override test_framework=jest "prompt"

Note: Overrides are temporary and don't modify project configuration.
"""
