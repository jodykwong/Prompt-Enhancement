"""Tests for Story 4.2: Project-Level Standards Configuration."""

import pytest
import tempfile
import os
from pathlib import Path
from src.prompt_enhancement.config.schema import StandardsConfig
from src.prompt_enhancement.config.loader import ConfigLoader


class TestStandardsConfigSchema:
    """Test StandardsConfig validation."""

    def test_valid_config_creation(self):
        """Test creating valid configuration."""
        config = StandardsConfig(
            naming_convention="snake_case",
            test_framework="pytest",
            documentation_style="google",
            code_organization="by-feature",
            module_naming_pattern="service_",
        )
        is_valid, errors = config.validate()
        assert is_valid
        assert len(errors) == 0

    def test_invalid_naming_convention(self):
        """Test invalid naming convention."""
        config = StandardsConfig(naming_convention="InvalidCase")
        is_valid, errors = config.validate()
        assert not is_valid
        assert len(errors) > 0
        assert "naming_convention" in errors[0]

    def test_invalid_test_framework(self):
        """Test invalid test framework."""
        config = StandardsConfig(test_framework="InvalidFramework")
        is_valid, errors = config.validate()
        assert not is_valid
        assert "test_framework" in errors[0]

    def test_partial_config(self):
        """Test partial configuration."""
        config = StandardsConfig(naming_convention="camelCase")
        is_valid, errors = config.validate()
        assert is_valid
        assert config.test_framework is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = StandardsConfig(naming_convention="snake_case")
        data = config.to_dict()
        assert data["naming_convention"] == "snake_case"
        assert data["test_framework"] is None

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "naming_convention": "camelCase",
            "test_framework": "jest",
            "documentation_style": "jsdoc",
        }
        config = StandardsConfig.from_dict(data)
        assert config.naming_convention == "camelCase"
        assert config.test_framework == "jest"
        assert config.documentation_style == "jsdoc"


class TestConfigLoader:
    """Test configuration file loading."""

    def test_find_config_file_claude_path(self):
        """Test finding .claude/pe-config.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".claude"
            config_dir.mkdir()
            config_file = config_dir / "pe-config.yaml"
            config_file.write_text("naming_convention: snake_case\n")

            loader = ConfigLoader(tmpdir)
            found_path = loader._find_config_file()

            assert found_path is not None
            assert found_path.name == "pe-config.yaml"

    def test_find_config_file_root_path(self):
        """Test finding .pe.yaml in root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pe.yaml"
            config_file.write_text("naming_convention: camelCase\n")

            loader = ConfigLoader(tmpdir)
            found_path = loader._find_config_file()

            assert found_path is not None
            assert found_path.name == ".pe.yaml"

    def test_find_config_file_not_found(self):
        """Test when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ConfigLoader(tmpdir)
            found_path = loader._find_config_file()
            assert found_path is None

    def test_load_valid_config(self):
        """Test loading valid YAML configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".claude"
            config_dir.mkdir()
            config_file = config_dir / "pe-config.yaml"
            config_file.write_text(
                """naming_convention: snake_case
test_framework: pytest
documentation_style: google
code_organization: by-feature
module_naming_pattern: service_
"""
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load_config()

            assert config is not None
            assert config.naming_convention == "snake_case"
            assert config.test_framework == "pytest"
            assert config.documentation_style == "google"

    def test_load_partial_config(self):
        """Test loading partial configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pe.yaml"
            config_file.write_text("naming_convention: camelCase\n")

            loader = ConfigLoader(tmpdir)
            config = loader.load_config()

            assert config is not None
            assert config.naming_convention == "camelCase"
            assert config.test_framework is None

    def test_load_empty_config(self):
        """Test loading empty YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pe.yaml"
            config_file.write_text("")

            loader = ConfigLoader(tmpdir)
            config = loader.load_config()

            assert config is not None
            assert config.naming_convention is None

    def test_load_invalid_config_values(self):
        """Test invalid configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pe.yaml"
            config_file.write_text("naming_convention: InvalidCase\n")

            loader = ConfigLoader(tmpdir)
            config = loader.load_config()

            # Should return None on validation error
            assert config is None

    def test_invalid_yaml(self):
        """Test handling of invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".pe.yaml"
            config_file.write_text("naming_convention: [invalid yaml:::\n")

            loader = ConfigLoader(tmpdir)
            config = loader.load_config()

            # Should gracefully handle YAML error
            assert config is None

    def test_config_file_not_found(self):
        """Test when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ConfigLoader(tmpdir)
            config = loader.load_config()
            assert config is None


class TestConfigLoaderPriority:
    """Test configuration file priority."""

    def test_claude_path_prioritized(self):
        """Test .claude/pe-config.yaml has priority over .pe.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both files
            claude_dir = Path(tmpdir) / ".claude"
            claude_dir.mkdir()
            claude_file = claude_dir / "pe-config.yaml"
            claude_file.write_text("naming_convention: snake_case\n")

            root_file = Path(tmpdir) / ".pe.yaml"
            root_file.write_text("naming_convention: camelCase\n")

            loader = ConfigLoader(tmpdir)
            found_path = loader._find_config_file()

            assert found_path.name == "pe-config.yaml"


class TestIntegration_ConfigLoading:
    """Integration tests for configuration loading."""

    def test_full_config_loading_workflow(self):
        """Test complete config loading workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".claude"
            config_dir.mkdir()
            config_file = config_dir / "pe-config.yaml"
            config_file.write_text(
                """naming_convention: snake_case
test_framework: pytest
documentation_style: google
code_organization: by-feature
module_naming_pattern: service_
"""
            )

            loader = ConfigLoader(tmpdir)

            # Step 1: Find config file
            found = loader._find_config_file()
            assert found is not None

            # Step 2: Load config
            config = loader.load_config()
            assert config is not None

            # Step 3: Validate config
            is_valid, errors = config.validate()
            assert is_valid
            assert len(errors) == 0
