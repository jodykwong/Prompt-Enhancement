"""Interactive setup wizard for configuring the system."""

import logging
from pathlib import Path
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)


class APIKeyValidator:
    """Validates OpenAI/DeepSeek API keys."""

    @staticmethod
    def is_valid_format(api_key: str) -> bool:
        """
        Check if API key has valid format.

        Args:
            api_key: The API key to validate

        Returns:
            True if format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # OpenAI keys start with sk-
        # DeepSeek keys may vary, but we accept any non-empty string
        return api_key.startswith("sk-") or len(api_key) > 10

    @staticmethod
    def validate_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate API key (format check only in this version).

        Args:
            api_key: The API key to validate

        Returns:
            Tuple of (is_valid, message)
        """
        api_key = api_key.strip() if api_key else ""

        if not api_key:
            return False, "API key cannot be empty"

        if not APIKeyValidator.is_valid_format(api_key):
            return False, f"Invalid API key format. Should start with 'sk-'"

        # In production, would test with actual API
        # For now, just validate format
        logger.debug("API key validation passed (format check)")
        return True, "✓ API key valid"


class ProjectTypeDetector:
    """Detects project type from project files."""

    PROJECT_FILES = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "nodejs": ["package.json"],
        "java": ["pom.xml", "build.gradle"],
        "go": ["go.mod"],
        "ruby": ["Gemfile"],
    }

    @staticmethod
    def detect_project_type(project_dir: Optional[Path] = None) -> Optional[str]:
        """
        Detect project type from files.

        Args:
            project_dir: Directory to check (default: current directory)

        Returns:
            Detected project type or None
        """
        if project_dir is None:
            project_dir = Path.cwd()

        if not project_dir.exists():
            return None

        # Check for identifying files
        for project_type, files in ProjectTypeDetector.PROJECT_FILES.items():
            for file_name in files:
                if (project_dir / file_name).exists():
                    logger.debug(f"Detected {project_type} project (found {file_name})")
                    return project_type

        logger.debug("Could not detect project type")
        return None


class SetupWizard:
    """Interactive setup wizard for user configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize setup wizard.

        Args:
            config_dir: Directory for config (default: ~/.prompt-enhancement/)
        """
        if config_dir is None:
            config_dir = str(Path.home() / ".prompt-enhancement")

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"

    def run_interactive_setup(self) -> bool:
        """
        Run complete setup flow.

        Returns:
            True if setup completed successfully, False otherwise
        """
        logger.info("Starting interactive setup wizard")

        print("🔧 Prompt Enhancement Setup Wizard\n")

        # Step 1: API Key
        api_key = self.step_1_api_key()
        if not api_key:
            logger.warning("Setup cancelled - no API key provided")
            return False

        # Step 2: Project Type
        project_type = self.step_2_project_type()

        # Step 3: Standards Preferences
        standards = self.step_3_standards()

        # Save configuration
        if self.save_configuration(api_key, project_type, standards):
            print("\n✅ Setup Complete!")
            print("You can now run: /pe \"your prompt\"")
            print("\n💡 Tip: Run /pe-help for full documentation")
            logger.info("Setup wizard completed successfully")
            return True
        else:
            logger.error("Failed to save configuration")
            return False

    def step_1_api_key(self) -> Optional[str]:
        """
        Get and validate API key.

        Returns:
            Valid API key or None if cancelled
        """
        print("Step 1/3: API Key Configuration")
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                api_key = input("Please enter your OpenAI API key: ").strip()

                if not api_key:
                    print("Cancelled - no API key provided")
                    return None

                is_valid, message = APIKeyValidator.validate_key(api_key)

                if is_valid:
                    print(f"{message}\n")
                    return api_key
                else:
                    print(f"❌ {message}")
                    if attempt < max_attempts - 1:
                        print("Please try again.\n")
                    else:
                        print("Max attempts reached. Setup cancelled.")
                        return None

            except (KeyboardInterrupt, EOFError):
                print("\nSetup cancelled by user")
                return None

    def step_2_project_type(self) -> Optional[str]:
        """
        Detect and confirm project type.

        Returns:
            Project type or None if skipped
        """
        print("Step 2/3: Project Type Detection")

        detected = ProjectTypeDetector.detect_project_type()

        if detected:
            try:
                response = input(f"Detected project type: {detected}\n" +
                               "Is this correct? [Y/n]: ").strip().lower()

                if response == "" or response == "y":
                    print()
                    return detected
                else:
                    print("Skipping project type detection\n")
                    return None
            except (KeyboardInterrupt, EOFError):
                print("\nSetup cancelled by user")
                return None
        else:
            print("Could not detect project type\n")
            return None

    def step_3_standards(self) -> Dict[str, str]:
        """
        Get standards preferences.

        Returns:
            Dictionary of standards settings
        """
        print("Step 3/3: Standards Preferences (Optional)")
        standards = {}

        try:
            # Naming convention
            naming = input(
                "Naming convention (snake_case/camelCase/other) [snake_case]: "
            ).strip().lower()
            if naming:
                standards["naming_convention"] = naming
            else:
                standards["naming_convention"] = "snake_case"

            # Test framework
            framework = input(
                "Test framework (pytest/unittest/jest/other) [pytest]: "
            ).strip().lower()
            if framework:
                standards["test_framework"] = framework
            else:
                standards["test_framework"] = "pytest"

            print()

        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled by user")
            return {}

        return standards

    def save_configuration(
        self,
        api_key: str,
        project_type: Optional[str],
        standards: Dict[str, str],
    ) -> bool:
        """
        Save configuration to file.

        Args:
            api_key: The API key
            project_type: Detected or selected project type
            standards: Standards preferences

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            import yaml

            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Read existing config
            config = {}
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = yaml.safe_load(f) or {}

            # Update with setup results
            config["api_key"] = api_key
            if project_type:
                config["project_type"] = project_type
            config.update(standards)
            config["first_time_setup_complete"] = True

            # Write to file
            with open(self.config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

            logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
