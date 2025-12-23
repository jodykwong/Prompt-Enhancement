"""Configuration loader for project-level standards settings."""

import logging
import os
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

from .schema import StandardsConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and validates project-level configuration files."""

    # Configuration file locations in priority order
    CONFIG_PATHS = [".claude/pe-config.yaml", ".pe.yaml"]

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or os.getcwd()
        logger.debug(f"Initialized ConfigLoader with project_root={self.project_root}")

    def load_config(self) -> Optional[StandardsConfig]:
        """
        Load project configuration if present.

        Returns:
            StandardsConfig if found and valid, None otherwise
        """
        config_path = self._find_config_file()

        if not config_path:
            logger.debug("No project configuration file found")
            return None

        try:
            return self._load_and_validate(config_path)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            return None

    def _find_config_file(self) -> Optional[Path]:
        """
        Find configuration file in project root.

        Returns:
            Path to config file if found, None otherwise
        """
        for config_name in self.CONFIG_PATHS:
            config_path = Path(self.project_root) / config_name

            if config_path.exists():
                logger.debug(f"Found config file: {config_path}")
                return config_path

        return None

    def _load_and_validate(self, config_path: Path) -> Optional[StandardsConfig]:
        """
        Load and validate configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            StandardsConfig if valid, None otherwise
        """
        if not yaml:
            logger.error("PyYAML not installed, cannot load config files")
            return None

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            config = StandardsConfig.from_dict(data)
            is_valid, errors = config.validate()

            if not is_valid:
                for error in errors:
                    logger.warning(f"Config validation error: {error}")
                logger.warning(f"Using auto-detection instead of invalid config")
                return None

            logger.info(f"Loaded valid configuration from {config_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {config_path}: {e}")
            return None

    @staticmethod
    def get_config_help() -> str:
        """
        Get help text for creating configuration files.

        Returns:
            Help text with example configuration
        """
        return """
📝 Project Configuration File

Create a file `.claude/pe-config.yaml` in your project root:

naming_convention: snake_case          # Options: snake_case, camelCase, PascalCase, kebab-case
test_framework: pytest                 # Options: pytest, unittest, jest, mocha, NUnit, xUnit, etc.
documentation_style: google            # Options: google, numpy, sphinx, jsdoc, javadoc, pep257
code_organization: by-feature          # Options: by-feature, by-layer, by-type, domain-driven, monolithic
module_naming_pattern: service_        # e.g., service_*, models_*, etc.

All fields are optional. Omitted fields use auto-detection.
"""
