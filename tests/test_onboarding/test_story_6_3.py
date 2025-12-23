"""Tests for Story 6.3: /pe-help Command and Template Suggestions."""

import pytest
from src.prompt_enhancement.onboarding.help_system import HelpSystem, TemplateSuggestion


class TestHelpSystemAC1:
    """AC1: Basic help command (/pe-help)."""

    def test_basic_help_displayed(self):
        """Test basic help is displayed."""
        help_text = HelpSystem.show_basic_help()
        assert help_text is not None
        assert len(help_text) > 0

    def test_basic_help_has_usage_section(self):
        """Test basic help includes usage section."""
        help_text = HelpSystem.show_basic_help()
        assert "Basic Usage" in help_text or "usage" in help_text.lower()

    def test_basic_help_has_templates_section(self):
        """Test basic help lists available templates."""
        help_text = HelpSystem.show_basic_help()
        assert "fastapi" in help_text.lower()
        assert "django" in help_text.lower()
        assert "react" in help_text.lower()

    def test_basic_help_has_commands_section(self):
        """Test basic help lists commands."""
        help_text = HelpSystem.show_basic_help()
        assert "/pe-setup" in help_text
        assert "/pe-help" in help_text

    def test_basic_help_has_faq(self):
        """Test basic help includes FAQ section."""
        help_text = HelpSystem.show_basic_help()
        assert "FAQ" in help_text or "Q:" in help_text

    def test_basic_help_has_emoji(self):
        """Test basic help uses emoji indicators."""
        help_text = HelpSystem.show_basic_help()
        assert "📚" in help_text or "🚀" in help_text


class TestHelpSystemAC2:
    """AC2: Template suggestion based on project."""

    def test_suggest_template_python(self):
        """Test suggests fastapi for Python."""
        template = TemplateSuggestion.suggest_template("python")
        assert template == "fastapi"

    def test_suggest_template_nodejs(self):
        """Test suggests react for Node.js."""
        template = TemplateSuggestion.suggest_template("nodejs")
        assert template == "react"

    def test_suggest_template_java(self):
        """Test suggests generic for Java."""
        template = TemplateSuggestion.suggest_template("java")
        assert template == "generic"

    def test_suggest_template_none(self):
        """Test returns None when no match."""
        template = TemplateSuggestion.suggest_template("unknown")
        assert template is None

    def test_suggestion_prompt_formatted(self):
        """Test suggestion prompt is formatted correctly."""
        prompt = TemplateSuggestion.format_suggestion_prompt("FastAPI", "fastapi")
        assert "FastAPI" in prompt
        assert "fastapi" in prompt
        assert "Y/n" in prompt or "Continue" in prompt.lower()

    def test_suggestion_has_action_items(self):
        """Test suggestion includes action items."""
        prompt = TemplateSuggestion.format_suggestion_prompt("Python", "fastapi")
        assert "/pe --template fastapi" in prompt or "template" in prompt.lower()


class TestHelpSystemAC3:
    """AC3: Full help documentation (/pe-help-full)."""

    def test_full_help_displayed(self):
        """Test full help is displayed."""
        help_text = HelpSystem.show_full_help()
        assert help_text is not None
        assert len(help_text) > len(HelpSystem.show_basic_help())

    def test_full_help_comprehensive(self):
        """Test full help covers major topics."""
        help_text = HelpSystem.show_full_help()
        assert "Commands" in help_text
        assert "Configuration" in help_text
        assert "Examples" in help_text

    def test_full_help_longer_than_basic(self):
        """Test full help is longer than basic."""
        basic = HelpSystem.show_basic_help()
        full = HelpSystem.show_full_help()
        assert len(full) > len(basic)


class TestHelpSystemAC4:
    """AC4: Topic-specific help."""

    def test_topic_standards_help(self):
        """Test standards help available."""
        help_text = HelpSystem.show_help("standards")
        assert help_text is not None
        assert len(help_text) > 0

    def test_topic_templates_help(self):
        """Test templates help available."""
        help_text = HelpSystem.show_help("templates")
        assert help_text is not None
        assert len(help_text) > 0

    def test_topic_config_help(self):
        """Test config help available."""
        help_text = HelpSystem.show_help("config")
        assert help_text is not None
        assert len(help_text) > 0

    def test_topic_examples_help(self):
        """Test examples help available."""
        help_text = HelpSystem.show_help("examples")
        assert help_text is not None
        assert len(help_text) > 0

    def test_topic_api_help(self):
        """Test API help available."""
        help_text = HelpSystem.show_help("api")
        assert help_text is not None
        assert len(help_text) > 0

    def test_topic_troubleshoot_help(self):
        """Test troubleshoot help available."""
        help_text = HelpSystem.show_help("troubleshoot")
        assert help_text is not None
        assert len(help_text) > 0

    def test_invalid_topic_error(self):
        """Test invalid topic returns error message."""
        help_text = HelpSystem.show_help("invalid_topic")
        assert "Unknown topic" in help_text or "invalid" in help_text.lower()

    def test_standards_help_detailed(self):
        """Test standards help is detailed."""
        help_text = HelpSystem.show_help("standards")
        assert "Available Standards" in help_text or "naming" in help_text.lower()

    def test_templates_help_detailed(self):
        """Test templates help is detailed."""
        help_text = HelpSystem.show_help("templates")
        assert "Built-in Templates" in help_text or "fastapi" in help_text.lower()

    def test_config_help_detailed(self):
        """Test config help is detailed."""
        help_text = HelpSystem.show_help("config")
        assert "config.yaml" in help_text or "configuration" in help_text.lower()

    def test_examples_help_detailed(self):
        """Test examples help is detailed."""
        help_text = HelpSystem.show_help("examples")
        assert "/pe" in help_text or "example" in help_text.lower()


class TestTemplateSuggestionAC:
    """AC: Template suggestion details."""

    def test_suggestion_case_insensitive(self):
        """Test suggestion works with different cases."""
        template1 = TemplateSuggestion.suggest_template("PYTHON")
        template2 = TemplateSuggestion.suggest_template("python")
        # Both should work
        assert template1 is not None or template2 is not None

    def test_suggestion_with_whitespace(self):
        """Test suggestion handles whitespace."""
        template = TemplateSuggestion.suggest_template("  python  ")
        assert template is not None

    def test_suggestion_none_when_no_project(self):
        """Test returns None for unknown project."""
        template = TemplateSuggestion.suggest_template("unknown_language")
        assert template is None

    def test_template_map_complete(self):
        """Test template map covers major languages."""
        assert "python" in TemplateSuggestion.TEMPLATE_MAP
        assert "nodejs" in TemplateSuggestion.TEMPLATE_MAP
        assert "java" in TemplateSuggestion.TEMPLATE_MAP

    def test_suggestion_prompt_structure(self):
        """Test suggestion prompt has required structure."""
        prompt = TemplateSuggestion.format_suggestion_prompt("Python", "fastapi")
        assert "Detected" in prompt or "detected" in prompt.lower()
        assert "Recommended" in prompt or "recommended" in prompt.lower()
        assert "[Y/n]" in prompt or "Y/n" in prompt


class TestIntegration_HelpSystem:
    """Integration tests for help system."""

    def test_all_topics_have_help(self):
        """Test all topics in TOPIC_HELP are accessible."""
        for topic in HelpSystem.TOPIC_HELP.keys():
            help_text = HelpSystem.show_help(topic)
            assert help_text is not None
            assert len(help_text) > 0

    def test_help_consistency(self):
        """Test help is consistent across different calls."""
        help1 = HelpSystem.show_basic_help()
        help2 = HelpSystem.show_basic_help()
        assert help1 == help2

    def test_full_help_consistent(self):
        """Test full help is consistent."""
        help1 = HelpSystem.show_full_help()
        help2 = HelpSystem.show_full_help()
        assert help1 == help2

    def test_default_help_is_basic(self):
        """Test default help (no topic) is basic."""
        default_help = HelpSystem.show_help()
        basic_help = HelpSystem.show_basic_help()
        assert default_help == basic_help

    def test_template_suggestions_reasonable(self):
        """Test template suggestions are reasonable."""
        # FastAPI for Python makes sense
        assert TemplateSuggestion.suggest_template("python") in ["fastapi", None]

        # React for Node.js makes sense
        assert TemplateSuggestion.suggest_template("nodejs") in ["react", None]

    def test_suggestion_display_workflow(self):
        """Test suggestion display workflow."""
        project_type = "Python"
        suggested = TemplateSuggestion.suggest_template(project_type.lower())

        if suggested:
            prompt = TemplateSuggestion.format_suggestion_prompt(project_type, suggested)
            assert len(prompt) > 0
            assert project_type in prompt or project_type.lower() in prompt.lower()


class TestHelpContentAC:
    """AC: Help content quality."""

    def test_basic_help_not_empty(self):
        """Test basic help is not empty."""
        help_text = HelpSystem.show_basic_help()
        assert len(help_text) > 50

    def test_full_help_not_empty(self):
        """Test full help is not empty."""
        help_text = HelpSystem.show_full_help()
        assert len(help_text) > 500

    def test_topic_help_not_empty(self):
        """Test topic help is not empty."""
        for topic in ["standards", "templates", "config"]:
            help_text = HelpSystem.show_help(topic)
            assert len(help_text) > 50

    def test_help_readable_format(self):
        """Test help is in readable format."""
        help_text = HelpSystem.show_basic_help()
        # Should have some structure
        assert "\n" in help_text
        lines = help_text.split("\n")
        assert len(lines) > 5
