"""First-time user detection and quick guide display."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FirstTimeDetector:
    """Detects if this is the user's first time using the system."""

    # Config key for tracking first-time setup
    FIRST_TIME_KEY = "first_time_setup_complete"

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize first-time detector.

        Args:
            config_dir: Directory containing config (default: ~/.prompt-enhancement/)
        """
        if config_dir is None:
            config_dir = str(Path.home() / ".prompt-enhancement")

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"

    def is_first_time(self) -> bool:
        """
        Check if this is first-time use.

        Returns:
            True if first-time (config missing or flag not set), False otherwise
        """
        if not self.config_file.exists():
            logger.debug("Config file doesn't exist - first time use detected")
            return True

        # Read flag from config
        try:
            import yaml

            with open(self.config_file) as f:
                config = yaml.safe_load(f) or {}

            is_complete = config.get(self.FIRST_TIME_KEY, False)
            logger.debug(f"First-time check: {self.FIRST_TIME_KEY}={is_complete}")
            return not is_complete

        except Exception as e:
            logger.debug(f"Error reading config for first-time check: {e}")
            # Safe default: assume first time if we can't read config
            return True

    def mark_setup_complete(self) -> bool:
        """
        Mark first-time setup as complete.

        Returns:
            True if successfully marked, False otherwise
        """
        try:
            import yaml

            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Read existing config or create new
            config = {}
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = yaml.safe_load(f) or {}

            # Set the flag
            config[self.FIRST_TIME_KEY] = True

            # Write back to file
            with open(self.config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

            logger.info(f"Marked first-time setup as complete")
            return True

        except Exception as e:
            logger.error(f"Error marking setup complete: {e}")
            return False


class QuickGuideDisplay:
    """Displays the 3-step quick guide for new users."""

    QUICKSTART_GUIDE = """
🚀 Welcome to Prompt Enhancement!

This system helps you enhance prompts with project-aware guidance.
Let's get started quickly:

📋 Step 1: Configure Your API Key
  Run: /pe-setup
  (Only needed once)

📊 Step 2: Run Your First Enhancement
  Run: /pe "Your prompt to enhance"

🎯 Step 3: View Enhancement Results
  System will show original, enhanced prompt and implementation steps

💡 Tip: Run /pe-help for full documentation

Press [Enter] to continue...
"""

    @staticmethod
    def show_quickstart_guide() -> str:
        """
        Display the 3-step quick guide.

        Returns:
            The formatted guide text
        """
        return QuickGuideDisplay.QUICKSTART_GUIDE.strip()

    @staticmethod
    def format_guide() -> str:
        """
        Get formatted quick guide text.

        Returns:
            Formatted guide with emojis and structure
        """
        return QuickGuideDisplay.QUICKSTART_GUIDE.strip()

    @staticmethod
    def display_and_wait() -> None:
        """
        Display guide and wait for user to press Enter.
        """
        guide = QuickGuideDisplay.show_quickstart_guide()
        print(guide)

        # Wait for user to press Enter
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            # User cancelled
            pass


class OnboardingManager:
    """Manages the onboarding workflow."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize onboarding manager.

        Args:
            config_dir: Directory containing config
        """
        self.detector = FirstTimeDetector(config_dir)
        self.guide = QuickGuideDisplay()

    def should_show_guide(self) -> bool:
        """
        Determine if quick guide should be shown.

        Returns:
            True if first-time and guide should show, False otherwise
        """
        return self.detector.is_first_time()

    def show_guide(self) -> None:
        """Display the quick guide to user."""
        self.guide.display_and_wait()

    def complete_onboarding(self) -> bool:
        """
        Mark onboarding as complete.

        Returns:
            True if successfully marked, False otherwise
        """
        return self.detector.mark_setup_complete()

    def reset_onboarding(self) -> bool:
        """
        Reset onboarding (for testing or user request).

        Returns:
            True if successfully reset, False otherwise
        """
        return self.detector.mark_setup_complete() is False  # Reset flag
