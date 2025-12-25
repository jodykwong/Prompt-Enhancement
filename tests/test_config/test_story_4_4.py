"""Tests for Story 4.4: Template System and Save User Overrides."""

import pytest
import tempfile
import json
from pathlib import Path
from src.prompt_enhancement.config.schema import StandardsConfig
from src.prompt_enhancement.config.templates import TemplateManager


class TestTemplateSystemAC1:
    """AC1: Use predefined templates."""

    def test_load_fastapi_template(self):
        """Test loading FastAPI template."""
        manager = TemplateManager()
        config = manager.get_template("fastapi")

        assert config is not None
        assert config.naming_convention == "snake_case"
        assert config.test_framework == "pytest"
        assert config.documentation_style == "google"

    def test_load_django_template(self):
        """Test loading Django template."""
        manager = TemplateManager()
        config = manager.get_template("django")

        assert config is not None
        assert config.naming_convention == "snake_case"
        assert config.code_organization == "by-layer"

    def test_load_react_template(self):
        """Test loading React template."""
        manager = TemplateManager()
        config = manager.get_template("react")

        assert config is not None
        assert config.naming_convention == "camelCase"
        assert config.test_framework == "jest"
        assert config.documentation_style == "jsdoc"

    def test_nonexistent_template_returns_none(self):
        """Test loading nonexistent template returns None."""
        manager = TemplateManager()
        config = manager.get_template("nonexistent")

        assert config is None


class TestTemplateSystemAC2:
    """AC2: Built-in templates exist."""

    def test_builtin_templates_defined(self):
        """Test all required built-in templates are defined."""
        manager = TemplateManager()
        required = ["fastapi", "django", "flask", "react", "generic"]

        for template_name in required:
            config = manager.get_template(template_name)
            assert config is not None, f"Missing template: {template_name}"


class TestTemplateSystemAC3:
    """AC3: Template discovery."""

    def test_list_templates(self):
        """Test listing all templates."""
        manager = TemplateManager()
        templates = manager.list_templates()

        assert "fastapi" in templates
        assert "django" in templates
        assert "flask" in templates
        assert "react" in templates
        assert "generic" in templates

    def test_list_templates_includes_custom(self):
        """Test listing includes custom templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)

            # Create custom template
            custom_config = StandardsConfig(naming_convention="camelCase")
            manager.save_template("my-custom", custom_config)

            # List should include custom template
            templates = manager.list_templates()
            assert "my-custom" in templates
            assert "custom" in templates["my-custom"].lower()


class TestTemplateSystemAC4:
    """AC4: Save custom templates."""

    def test_save_custom_template(self):
        """Test saving custom template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)
            config = StandardsConfig(naming_convention="camelCase")

            result = manager.save_template("my-template", config)

            assert result is True
            # Verify it can be loaded
            loaded = manager.get_template("my-template")
            assert loaded is not None
            assert loaded.naming_convention == "camelCase"

    def test_cannot_overwrite_builtin_template(self):
        """Test cannot overwrite built-in template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)
            config = StandardsConfig(naming_convention="camelCase")

            result = manager.save_template("fastapi", config)

            assert result is False


class TestTemplateSystemAC5:
    """AC5: Template suggestion from overrides."""

    def test_save_template_from_config(self):
        """Test saving configuration as template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)

            # Simulate user's repeated overrides
            config = StandardsConfig(
                naming_convention="camelCase",
                test_framework="jest",
                documentation_style="jsdoc",
            )

            # Save as template
            result = manager.save_template("my-react-style", config)
            assert result is True

            # Verify saved
            loaded = manager.get_template("my-react-style")
            assert loaded is not None
            assert loaded.naming_convention == "camelCase"


class TestTemplateSystemAC6:
    """AC6: Template priority and composition."""

    def test_template_overrides_auto_detection(self):
        """Test template overrides auto-detected config."""
        # Simulate auto-detection result
        auto_config = StandardsConfig(naming_convention="snake_case")

        # User specifies template
        manager = TemplateManager()
        template_config = manager.get_template("react")

        # Template should override
        assert template_config.naming_convention == "camelCase"

    def test_cli_override_on_template(self):
        """Test CLI override can further customize template."""
        # Load template
        manager = TemplateManager()
        template_config = manager.get_template("react")

        # Simulate applying CLI override on top of template
        from src.prompt_enhancement.config.overrides import OverrideParser

        overrides = {"naming": "snake_case"}
        final_config = OverrideParser.apply_overrides(template_config, overrides)

        # CLI override should win
        assert final_config.naming_convention == "snake_case"
        # But other template settings remain
        assert final_config.test_framework == "jest"


class TestTemplateSystemAC7:
    """AC7: Template composition."""

    def test_template_with_override_composition(self):
        """Test composing template with override."""
        # Load template
        manager = TemplateManager()
        template_config = manager.get_template("fastapi")

        # Apply override on top
        from src.prompt_enhancement.config.overrides import OverrideParser

        overrides = {"naming": "camelCase"}
        final_config = OverrideParser.apply_overrides(template_config, overrides)

        # Check composition
        assert final_config.naming_convention == "camelCase"  # Overridden
        assert final_config.test_framework == "pytest"  # From template
        assert final_config.documentation_style == "google"  # From template


class TestTemplateSystemAC8:
    """AC8: Template management."""

    def test_delete_custom_template(self):
        """Test deleting custom template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)

            # Create template
            config = StandardsConfig(naming_convention="camelCase")
            manager.save_template("to-delete", config)

            # Verify exists
            assert manager.get_template("to-delete") is not None

            # Delete it
            result = manager.delete_template("to-delete")
            assert result is True

            # Verify gone
            assert manager.get_template("to-delete") is None

    def test_cannot_delete_builtin_template(self):
        """Test cannot delete built-in template."""
        manager = TemplateManager()
        result = manager.delete_template("fastapi")
        assert result is False

    def test_is_builtin_check(self):
        """Test checking if template is built-in."""
        manager = TemplateManager()
        assert manager.is_builtin("fastapi") is True
        assert manager.is_builtin("nonexistent") is False

    def test_is_custom_check(self):
        """Test checking if template is custom."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)

            config = StandardsConfig(naming_convention="camelCase")
            manager.save_template("custom-one", config)

            assert manager.is_custom("custom-one") is True
            assert manager.is_custom("fastapi") is False


class TestIntegration_TemplateWorkflow:
    """Integration tests for template workflow."""

    def test_complete_template_workflow(self):
        """Test complete template usage workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)

            # Step 1: User loads template
            template_config = manager.get_template("react")
            assert template_config is not None

            # Step 2: User customizes with overrides
            from src.prompt_enhancement.config.overrides import OverrideParser

            overrides = {"naming": "snake_case"}
            final_config = OverrideParser.apply_overrides(template_config, overrides)

            # Step 3: User saves as custom template
            result = manager.save_template("custom-react", final_config)
            assert result is True

            # Step 4: User can load custom template later
            loaded = manager.get_template("custom-react")
            assert loaded is not None
            assert loaded.naming_convention == "snake_case"
            assert loaded.test_framework == "jest"  # From original template

    def test_all_builtin_templates_loadable(self):
        """Test all built-in templates can be loaded and are valid."""
        manager = TemplateManager()

        for template_name in manager.BUILTIN_TEMPLATES.keys():
            config = manager.get_template(template_name)
            assert config is not None, f"Failed to load {template_name}"
            is_valid, errors = config.validate()
            assert is_valid, f"Template {template_name} is invalid: {errors}"
