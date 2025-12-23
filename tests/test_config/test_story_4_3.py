"""Tests for Story 4.3: Per-Request Override Flag."""

import pytest
from src.prompt_enhancement.config.schema import StandardsConfig
from src.prompt_enhancement.config.overrides import OverrideParser


class TestOverrideParsingAC1:
    """AC1: Parse override flags."""

    def test_parse_single_override(self):
        """Test parsing single override flag."""
        overrides, errors = OverrideParser.parse_overrides(["naming=camelCase"])
        assert len(errors) == 0
        assert overrides["naming"] == "camelCase"

    def test_parse_naming_override(self):
        """Test naming convention override."""
        overrides, errors = OverrideParser.parse_overrides(["naming=PascalCase"])
        assert len(errors) == 0
        assert overrides["naming"] == "PascalCase"

    def test_parse_test_framework_override(self):
        """Test test framework override."""
        overrides, errors = OverrideParser.parse_overrides(["test_framework=jest"])
        assert len(errors) == 0
        assert overrides["test_framework"] == "jest"

    def test_parse_documentation_override(self):
        """Test documentation override."""
        overrides, errors = OverrideParser.parse_overrides(["documentation=jsdoc"])
        assert len(errors) == 0
        assert overrides["documentation"] == "jsdoc"


class TestOverrideParsingAC2:
    """AC2: Apply overrides to enhancement."""

    def test_apply_single_override(self):
        """Test applying single override."""
        base_config = StandardsConfig(naming_convention="snake_case")
        overrides = {"naming": "camelCase"}

        result = OverrideParser.apply_overrides(base_config, overrides)

        assert result.naming_convention == "camelCase"

    def test_apply_multiple_overrides(self):
        """Test applying multiple overrides."""
        base_config = StandardsConfig(
            naming_convention="snake_case",
            test_framework="pytest",
        )
        overrides = {
            "naming": "camelCase",
            "test_framework": "jest",
        }

        result = OverrideParser.apply_overrides(base_config, overrides)

        assert result.naming_convention == "camelCase"
        assert result.test_framework == "jest"

    def test_override_preserves_other_settings(self):
        """Test that overrides don't affect other settings."""
        base_config = StandardsConfig(
            naming_convention="snake_case",
            test_framework="pytest",
            documentation_style="google",
        )
        overrides = {"naming": "camelCase"}

        result = OverrideParser.apply_overrides(base_config, overrides)

        assert result.naming_convention == "camelCase"
        assert result.test_framework == "pytest"
        assert result.documentation_style == "google"


class TestOverrideParsingAC3:
    """AC3: Validate override values."""

    def test_invalid_naming_value(self):
        """Test invalid naming convention value."""
        overrides, errors = OverrideParser.parse_overrides(["naming=InvalidCase"])
        assert len(errors) > 0
        assert "Invalid value for naming" in errors[0]

    def test_invalid_test_framework_value(self):
        """Test invalid test framework value."""
        overrides, errors = OverrideParser.parse_overrides(
            ["test_framework=InvalidFramework"]
        )
        assert len(errors) > 0
        assert "Invalid value for test_framework" in errors[0]

    def test_invalid_override_key(self):
        """Test invalid override key."""
        overrides, errors = OverrideParser.parse_overrides(["invalid_key=value"])
        assert len(errors) > 0
        assert "Unknown override key" in errors[0]

    def test_malformed_override(self):
        """Test malformed override syntax."""
        overrides, errors = OverrideParser.parse_overrides(["invalid_syntax"])
        assert len(errors) > 0
        assert "Invalid override format" in errors[0]

    def test_valid_override_values(self):
        """Test all valid naming convention values."""
        valid_values = ["snake_case", "camelCase", "PascalCase", "kebab-case"]

        for value in valid_values:
            overrides, errors = OverrideParser.parse_overrides([f"naming={value}"])
            assert len(errors) == 0, f"Failed for naming={value}"
            assert overrides["naming"] == value


class TestOverrideParsingAC4:
    """AC4: Handle multiple overrides for same standard."""

    def test_last_override_wins(self):
        """Test that last override value is used."""
        overrides, errors = OverrideParser.parse_overrides(
            ["naming=snake_case", "naming=camelCase"]
        )
        assert len(errors) == 0
        assert overrides["naming"] == "camelCase"  # Last value wins

    def test_multiple_different_overrides(self):
        """Test multiple different override keys."""
        overrides, errors = OverrideParser.parse_overrides(
            [
                "naming=camelCase",
                "test_framework=jest",
                "documentation=jsdoc",
            ]
        )
        assert len(errors) == 0
        assert overrides["naming"] == "camelCase"
        assert overrides["test_framework"] == "jest"
        assert overrides["documentation"] == "jsdoc"


class TestOverrideParsingAC5:
    """AC5: Override priority (CLI > config > auto-detection)."""

    def test_cli_override_priority(self):
        """Test CLI override takes priority."""
        # Simulate base config from file
        base_config = StandardsConfig(naming_convention="snake_case")

        # Apply CLI override
        overrides = {"naming": "camelCase"}
        result = OverrideParser.apply_overrides(base_config, overrides)

        # CLI override should win
        assert result.naming_convention == "camelCase"


class TestOverrideParsingAC6:
    """AC6: Non-invasive experimentation."""

    def test_override_doesnt_modify_base(self):
        """Test that applying override doesn't modify original config."""
        base_config = StandardsConfig(naming_convention="snake_case")
        overrides = {"naming": "camelCase"}

        result = OverrideParser.apply_overrides(base_config, overrides)

        # Original should be unchanged
        assert base_config.naming_convention == "snake_case"
        # Result should have override
        assert result.naming_convention == "camelCase"


class TestOverrideParsingAC7:
    """AC7: Override discovery."""

    def test_help_text_availability(self):
        """Test that help text is available."""
        help_text = OverrideParser.get_override_help()
        assert help_text is not None
        assert "naming" in help_text.lower()
        assert "test_framework" in help_text.lower()
        assert "camelCase" in help_text
        assert "snake_case" in help_text


class TestIntegration_OverrideBehavior:
    """Integration tests for override behavior."""

    def test_full_override_workflow(self):
        """Test complete override workflow."""
        # Start with auto-detected config
        auto_config = StandardsConfig(
            naming_convention="snake_case",
            test_framework="pytest",
            documentation_style="google",
        )

        # User provides overrides via CLI
        override_strings = [
            "naming=camelCase",
            "test_framework=jest",
        ]

        overrides, errors = OverrideParser.parse_overrides(override_strings)
        assert len(errors) == 0

        # Apply overrides
        final_config = OverrideParser.apply_overrides(auto_config, overrides)

        # Verify final state
        assert final_config.naming_convention == "camelCase"
        assert final_config.test_framework == "jest"
        assert final_config.documentation_style == "google"  # Unchanged

    def test_invalid_override_graceful_handling(self):
        """Test graceful handling of invalid overrides."""
        override_strings = [
            "naming=camelCase",  # Valid
            "test_framework=InvalidFramework",  # Invalid
            "documentation=jsdoc",  # Valid
        ]

        overrides, errors = OverrideParser.parse_overrides(override_strings)

        # Should have 1 error for invalid framework
        assert len(errors) == 1
        # But still process valid overrides
        assert "naming" in overrides
        assert "documentation" in overrides
        assert "test_framework" not in overrides

    def test_empty_overrides(self):
        """Test handling empty override list."""
        overrides, errors = OverrideParser.parse_overrides([])
        assert len(errors) == 0
        assert len(overrides) == 0

    def test_whitespace_handling(self):
        """Test handling of whitespace in overrides."""
        overrides, errors = OverrideParser.parse_overrides(
            ["  naming  =  camelCase  "]
        )
        assert len(errors) == 0
        assert overrides["naming"] == "camelCase"
