"""Tests for Story 6.1: First-Time User 3-Step Quick Guide."""

import tempfile
from pathlib import Path
import pytest
from src.prompt_enhancement.onboarding.quickstart import (
    FirstTimeDetector,
    QuickGuideDisplay,
    OnboardingManager,
)


class TestFirstTimeDetectionAC1:
    """AC1: Detect first-time use and display quick guide."""

    def test_first_time_when_no_config(self):
        """Test first-time is detected when config missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = FirstTimeDetector(config_dir=tmpdir)
            assert detector.is_first_time() is True

    def test_first_time_when_flag_missing(self):
        """Test first-time detected when flag missing from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump({"some_other_key": "value"}, f)

            detector = FirstTimeDetector(config_dir=tmpdir)
            assert detector.is_first_time() is True

    def test_not_first_time_when_flag_true(self):
        """Test first-time is False when flag is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump({"first_time_setup_complete": True}, f)

            detector = FirstTimeDetector(config_dir=tmpdir)
            assert detector.is_first_time() is False

    def test_quick_guide_displayed(self):
        """Test quick guide is displayed."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert "Welcome to Prompt Enhancement" in guide
        assert "Step 1" in guide
        assert "Step 2" in guide
        assert "Step 3" in guide


class TestFirstTimeDetectionAC2:
    """AC2: Remember first-time setup and don't show again."""

    def test_mark_setup_complete(self):
        """Test marking setup as complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = FirstTimeDetector(config_dir=tmpdir)

            # Should be first time initially
            assert detector.is_first_time() is True

            # Mark as complete
            result = detector.mark_setup_complete()
            assert result is True

            # Should not be first time anymore
            assert detector.is_first_time() is False

    def test_flag_persisted_to_config(self):
        """Test flag is saved to config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = FirstTimeDetector(config_dir=tmpdir)
            detector.mark_setup_complete()

            # Read config file directly
            import yaml

            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file) as f:
                config = yaml.safe_load(f)

            assert config.get("first_time_setup_complete") is True

    def test_flag_read_from_config(self):
        """Test flag is read correctly from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config with flag set
            import yaml

            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump({"first_time_setup_complete": True}, f)

            # New detector should read the flag
            detector = FirstTimeDetector(config_dir=tmpdir)
            assert detector.is_first_time() is False


class TestFirstTimeDetectionAC3:
    """AC3: Allow user to view guide again with /pe-quickstart."""

    def test_quickstart_always_shows_guide(self):
        """Test quickstart shows guide always."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert len(guide) > 0
        assert "🚀 Welcome" in guide

    def test_quickstart_format(self):
        """Test quickstart guide has correct format."""
        guide = QuickGuideDisplay.format_guide()
        assert "📋 Step 1" in guide
        assert "📊 Step 2" in guide
        assert "🎯 Step 3" in guide
        assert "💡 Tip" in guide


class TestFirstTimeDetectionAC4:
    """AC4: Integration with configuration system."""

    def test_config_directory_created(self):
        """Test config directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "new_dir"
            detector = FirstTimeDetector(config_dir=str(config_dir))
            detector.mark_setup_complete()

            assert config_dir.exists()

    def test_config_file_created(self):
        """Test config file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = FirstTimeDetector(config_dir=tmpdir)
            detector.mark_setup_complete()

            config_file = Path(tmpdir) / "config.yaml"
            assert config_file.exists()

    def test_yaml_format(self):
        """Test config file is valid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import yaml

            detector = FirstTimeDetector(config_dir=tmpdir)
            detector.mark_setup_complete()

            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file) as f:
                config = yaml.safe_load(f)

            assert isinstance(config, dict)
            assert "first_time_setup_complete" in config

    def test_safe_defaults_when_config_missing(self):
        """Test safe defaults when config missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = FirstTimeDetector(config_dir=tmpdir)
            # Should assume first-time when file doesn't exist
            assert detector.is_first_time() is True


class TestOnboardingManagerAC:
    """AC: Onboarding manager integration."""

    def test_manager_shows_guide_on_first_time(self):
        """Test manager detects first-time and suggests guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = OnboardingManager(config_dir=tmpdir)
            assert manager.should_show_guide() is True

    def test_manager_does_not_show_guide_after_complete(self):
        """Test manager doesn't show guide after setup complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = OnboardingManager(config_dir=tmpdir)

            # Mark as complete
            manager.complete_onboarding()

            # Should not show guide
            assert manager.should_show_guide() is False

    def test_manager_complete_onboarding(self):
        """Test manager can mark onboarding complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = OnboardingManager(config_dir=tmpdir)

            # Initially first-time
            assert manager.should_show_guide() is True

            # Complete onboarding
            result = manager.complete_onboarding()
            assert result is True

            # Should not be first-time
            assert manager.should_show_guide() is False


class TestQuickGuideAC:
    """AC: Quick guide display details."""

    def test_guide_has_emoji_indicators(self):
        """Test guide uses emoji indicators."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert "🚀" in guide  # Welcome
        assert "📋" in guide  # Step 1
        assert "📊" in guide  # Step 2
        assert "🎯" in guide  # Step 3
        assert "💡" in guide  # Tip

    def test_guide_has_clear_steps(self):
        """Test guide has clearly numbered steps."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert "Step 1:" in guide
        assert "Step 2:" in guide
        assert "Step 3:" in guide

    def test_guide_has_action_items(self):
        """Test guide includes action items."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert "/pe-setup" in guide
        assert "/pe" in guide
        assert "/pe-help" in guide

    def test_guide_mentions_help(self):
        """Test guide points to help documentation."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert "/pe-help" in guide or "help" in guide.lower()

    def test_guide_not_empty(self):
        """Test guide is not empty."""
        guide = QuickGuideDisplay.show_quickstart_guide()
        assert len(guide) > 100


class TestIntegration_FirstTimeFlow:
    """Integration tests for first-time user flow."""

    def test_complete_first_time_workflow(self):
        """Test complete first-time user workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = OnboardingManager(config_dir=tmpdir)

            # Check first-time
            assert manager.should_show_guide() is True

            # Get guide
            guide = QuickGuideDisplay.show_quickstart_guide()
            assert "Welcome" in guide

            # Complete onboarding
            manager.complete_onboarding()

            # Check not first-time anymore
            assert manager.should_show_guide() is False

    def test_first_time_flag_persistence(self):
        """Test first-time flag persists across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First instance
            manager1 = OnboardingManager(config_dir=tmpdir)
            manager1.complete_onboarding()

            # Second instance should remember
            manager2 = OnboardingManager(config_dir=tmpdir)
            assert manager2.should_show_guide() is False

    def test_quickstart_replays_guide(self):
        """Test quickstart always shows guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = OnboardingManager(config_dir=tmpdir)
            manager.complete_onboarding()

            # Even after completing, quickstart should show
            guide = QuickGuideDisplay.show_quickstart_guide()
            assert len(guide) > 0
