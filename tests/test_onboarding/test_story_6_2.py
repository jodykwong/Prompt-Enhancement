"""Tests for Story 6.2: /pe-setup Command for Initial Configuration."""

import tempfile
from pathlib import Path
import pytest
from src.prompt_enhancement.onboarding.setup_wizard import (
    APIKeyValidator,
    ProjectTypeDetector,
    SetupWizard,
)


class TestSetupWizardAC1:
    """AC1: Interactive setup wizard flow."""

    def test_setup_wizard_initialization(self):
        """Test setup wizard initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_dir=tmpdir)
            assert wizard is not None
            assert wizard.config_dir is not None

    def test_api_key_validator_exists(self):
        """Test API key validator is available."""
        validator = APIKeyValidator()
        assert validator is not None


class TestSetupWizardAC2:
    """AC2: API key validation."""

    def test_api_key_format_valid(self):
        """Test valid API key format."""
        is_valid, msg = APIKeyValidator.validate_key("sk-1234567890abcdef")
        assert is_valid is True
        assert "valid" in msg.lower()

    def test_api_key_format_invalid_empty(self):
        """Test empty API key rejected."""
        is_valid, msg = APIKeyValidator.validate_key("")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_api_key_format_invalid_no_prefix(self):
        """Test API key without sk- prefix rejected."""
        is_valid, msg = APIKeyValidator.validate_key("1234567890")
        assert is_valid is False

    def test_api_key_format_validation_message(self):
        """Test validation error message."""
        is_valid, msg = APIKeyValidator.validate_key("invalid")
        assert is_valid is False
        assert msg is not None
        assert len(msg) > 0


class TestSetupWizardAC3:
    """AC3: Project type detection."""

    def test_detect_python_project(self):
        """Test detects Python project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            (Path(tmpdir) / "requirements.txt").touch()

            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "python"

    def test_detect_nodejs_project(self):
        """Test detects Node.js project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json
            (Path(tmpdir) / "package.json").touch()

            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "nodejs"

    def test_detect_java_project(self):
        """Test detects Java project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pom.xml
            (Path(tmpdir) / "pom.xml").touch()

            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "java"

    def test_no_detection(self):
        """Test returns None when no files detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected is None

    def test_detection_priority(self):
        """Test detection prioritizes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files
            (Path(tmpdir) / "requirements.txt").touch()
            (Path(tmpdir) / "package.json").touch()

            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            # Should detect one of them
            assert detected in ["python", "nodejs"]


class TestSetupWizardAC4:
    """AC4: Settings save and skip functionality."""

    def test_save_configuration(self):
        """Test configuration is saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_dir=tmpdir)

            result = wizard.save_configuration(
                api_key="sk-test123",
                project_type="python",
                standards={"naming_convention": "snake_case"},
            )

            assert result is True
            assert wizard.config_file.exists()

    def test_config_file_created(self):
        """Test config file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_dir=tmpdir)
            wizard.save_configuration("sk-test", None, {})

            config_file = Path(tmpdir) / "config.yaml"
            assert config_file.exists()

    def test_config_readable(self):
        """Test saved config is readable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            wizard = SetupWizard(config_dir=tmpdir)
            wizard.save_configuration(
                api_key="sk-test123",
                project_type="python",
                standards={"naming_convention": "snake_case", "test_framework": "pytest"},
            )

            with open(wizard.config_file) as f:
                config = yaml.safe_load(f)

            assert config["api_key"] == "sk-test123"
            assert config["project_type"] == "python"
            assert config["naming_convention"] == "snake_case"
            assert config["test_framework"] == "pytest"

    def test_first_time_flag_set(self):
        """Test first_time_setup_complete flag is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            wizard = SetupWizard(config_dir=tmpdir)
            wizard.save_configuration("sk-test", "python", {})

            with open(wizard.config_file) as f:
                config = yaml.safe_load(f)

            assert config.get("first_time_setup_complete") is True


class TestSetupWizardAC5:
    """AC5: Interactive questionnaire display."""

    def test_wizard_steps_exist(self):
        """Test wizard has all required steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_dir=tmpdir)

            # Methods should exist
            assert hasattr(wizard, "step_1_api_key")
            assert hasattr(wizard, "step_2_project_type")
            assert hasattr(wizard, "step_3_standards")

    def test_api_key_validator_function(self):
        """Test API key validator works correctly."""
        # Valid key
        is_valid, msg = APIKeyValidator.validate_key("sk-validkey123")
        assert is_valid is True

        # Invalid key
        is_valid, msg = APIKeyValidator.validate_key("invalid")
        assert is_valid is False


class TestProjectTypeDetectorAC:
    """AC: Project type detection details."""

    def test_pyproject_detection(self):
        """Test detects pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "pyproject.toml").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "python"

    def test_pipfile_detection(self):
        """Test detects Pipfile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "Pipfile").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "python"

    def test_setup_py_detection(self):
        """Test detects setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "setup.py").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "python"

    def test_gradle_detection(self):
        """Test detects build.gradle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "build.gradle").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "java"

    def test_go_mod_detection(self):
        """Test detects go.mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "go.mod").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "go"

    def test_gemfile_detection(self):
        """Test detects Gemfile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "Gemfile").touch()
            detected = ProjectTypeDetector.detect_project_type(Path(tmpdir))
            assert detected == "ruby"


class TestIntegration_SetupWizard:
    """Integration tests for setup wizard."""

    def test_api_key_validation_integration(self):
        """Test API key validation works correctly."""
        # Valid format
        is_valid, _ = APIKeyValidator.validate_key("sk-1234567890abc")
        assert is_valid is True

        # Invalid format
        is_valid, _ = APIKeyValidator.validate_key("invalid")
        assert is_valid is False

    def test_configuration_save_and_read(self):
        """Test configuration can be saved and read."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            wizard = SetupWizard(config_dir=tmpdir)

            # Save config
            wizard.save_configuration(
                api_key="sk-test",
                project_type="python",
                standards={"naming_convention": "snake_case"},
            )

            # Read it back
            with open(wizard.config_file) as f:
                config = yaml.safe_load(f)

            assert config["api_key"] == "sk-test"
            assert config["project_type"] == "python"

    def test_full_setup_workflow(self):
        """Test full setup wizard workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(config_dir=tmpdir)

            # Save configuration (simulating user input)
            result = wizard.save_configuration(
                api_key="sk-test123",
                project_type="python",
                standards={
                    "naming_convention": "snake_case",
                    "test_framework": "pytest",
                },
            )

            assert result is True
            assert wizard.config_file.exists()
