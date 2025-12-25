"""Template system for managing standard presets and custom templates."""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, List
from .schema import StandardsConfig

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages predefined and custom templates for standards."""

    # Built-in templates
    BUILTIN_TEMPLATES = {
        "fastapi": {
            "naming_convention": "snake_case",
            "test_framework": "pytest",
            "documentation_style": "google",
            "code_organization": "by-feature",
            "module_naming_pattern": "service_",
        },
        "django": {
            "naming_convention": "snake_case",
            "test_framework": "pytest",
            "documentation_style": "google",
            "code_organization": "by-layer",
            "module_naming_pattern": "models_",
        },
        "flask": {
            "naming_convention": "snake_case",
            "test_framework": "pytest",
            "documentation_style": "google",
            "code_organization": "by-feature",
            "module_naming_pattern": None,
        },
        "react": {
            "naming_convention": "camelCase",
            "test_framework": "jest",
            "documentation_style": "jsdoc",
            "code_organization": "by-feature",
            "module_naming_pattern": None,
        },
        "generic": {
            "naming_convention": None,
            "test_framework": None,
            "documentation_style": None,
            "code_organization": None,
            "module_naming_pattern": None,
        },
    }

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory for custom templates (~/.prompt-enhancement/templates/)
        """
        if templates_dir is None:
            templates_dir = str(Path.home() / ".prompt-enhancement" / "templates")

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized TemplateManager with dir={self.templates_dir}")

    def get_template(self, template_name: str) -> Optional[StandardsConfig]:
        """
        Get template by name.

        Args:
            template_name: Name of template

        Returns:
            StandardsConfig if found, None otherwise
        """
        # Check built-in templates first
        if template_name in self.BUILTIN_TEMPLATES:
            data = self.BUILTIN_TEMPLATES[template_name]
            return StandardsConfig.from_dict(data)

        # Check custom templates
        custom_path = self.templates_dir / f"{template_name}.json"
        if custom_path.exists():
            try:
                with open(custom_path) as f:
                    data = json.load(f)
                return StandardsConfig.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading custom template {template_name}: {e}")
                return None

        return None

    def list_templates(self) -> Dict[str, str]:
        """
        List all available templates.

        Returns:
            Dictionary of template_name -> description
        """
        templates = {}

        # Built-in templates
        descriptions = {
            "fastapi": "FastAPI web framework standards",
            "django": "Django web framework standards",
            "flask": "Flask web framework standards",
            "react": "React application standards",
            "generic": "Generic default standards",
        }

        for name, desc in descriptions.items():
            templates[name] = f"(built-in) {desc}"

        # Custom templates
        for template_file in self.templates_dir.glob("*.json"):
            name = template_file.stem
            templates[name] = "(custom)"

        return templates

    def save_template(
        self,
        template_name: str,
        config: StandardsConfig,
    ) -> bool:
        """
        Save custom template.

        Args:
            template_name: Name for template
            config: StandardsConfig to save

        Returns:
            True if successful, False otherwise
        """
        if template_name in self.BUILTIN_TEMPLATES:
            logger.error(f"Cannot overwrite built-in template: {template_name}")
            return False

        try:
            template_path = self.templates_dir / f"{template_name}.json"
            with open(template_path, "w") as f:
                json.dump(config.to_dict(), f, indent=2)

            logger.info(f"Saved custom template: {template_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving template {template_name}: {e}")
            return False

    def delete_template(self, template_name: str) -> bool:
        """
        Delete custom template.

        Args:
            template_name: Name of template to delete

        Returns:
            True if successful, False otherwise
        """
        if template_name in self.BUILTIN_TEMPLATES:
            logger.error(f"Cannot delete built-in template: {template_name}")
            return False

        try:
            template_path = self.templates_dir / f"{template_name}.json"
            if template_path.exists():
                template_path.unlink()
                logger.info(f"Deleted custom template: {template_name}")
                return True
            else:
                logger.warning(f"Template not found: {template_name}")
                return False
        except Exception as e:
            logger.error(f"Error deleting template {template_name}: {e}")
            return False

    def is_builtin(self, template_name: str) -> bool:
        """Check if template is built-in."""
        return template_name in self.BUILTIN_TEMPLATES

    def is_custom(self, template_name: str) -> bool:
        """Check if template is custom."""
        if self.is_builtin(template_name):
            return False
        return (self.templates_dir / f"{template_name}.json").exists()
