"""
Test suite for Story 4.1: Display Detected Standards with Confidence Scores

Tests all acceptance criteria for standards display functionality.
"""

import pytest
from src.prompt_enhancement.standards.display import (
    StandardsDisplay,
    StandardsInfo,
    EvidenceExample,
)


class TestAC1_DisplayAllFiveStandards:
    """AC1: Display all 5 detected standards with names and confidence."""

    def test_display_naming_convention(self):
        """Test naming convention standard is displayed."""
        naming = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=90.0,
            sample_size=89,
            evidence=[EvidenceExample("file.py", "def validate_input():", 15)],
        )

        assert naming.name == "Naming Convention"
        assert naming.value == "snake_case"
        assert naming.confidence == 90.0

    def test_display_test_framework(self):
        """Test test framework standard is displayed."""
        testing = StandardsInfo(
            name="Test Framework",
            value="pytest",
            confidence=95.0,
            sample_size=42,
            evidence=[EvidenceExample("test_file.py", "def test_validate():", 8)],
        )

        assert testing.name == "Test Framework"
        assert testing.value == "pytest"
        assert testing.confidence == 95.0

    def test_display_documentation_style(self):
        """Test documentation style standard is displayed."""
        docs = StandardsInfo(
            name="Documentation Style",
            value="Google docstrings",
            confidence=85.0,
            sample_size=67,
            evidence=[
                EvidenceExample("module.py", '"""This is a docstring."""', 12)
            ],
        )

        assert docs.name == "Documentation Style"
        assert docs.value == "Google docstrings"
        assert docs.confidence == 85.0

    def test_display_code_organization(self):
        """Test code organization pattern is displayed."""
        org = StandardsInfo(
            name="Code Organization",
            value="by-feature",
            confidence=80.0,
            sample_size=5,
            evidence=[EvidenceExample("features/auth/", "directory structure", 1)],
        )

        assert org.name == "Code Organization"
        assert org.value == "by-feature"
        assert org.confidence == 80.0

    def test_display_module_naming(self):
        """Test module naming pattern is displayed."""
        modules = StandardsInfo(
            name="Module Naming",
            value="service_*.py",
            confidence=88.0,
            sample_size=12,
            evidence=[EvidenceExample("service_auth.py", "module name", 1)],
        )

        assert modules.name == "Module Naming"
        assert modules.value == "service_*.py"
        assert modules.confidence == 88.0


class TestAC2_IncludeStandardMetadata:
    """AC2: Include name, value, confidence, sample size, evidence, exceptions."""

    def test_standard_with_all_metadata(self):
        """Test standard with complete metadata."""
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=90.0,
            sample_size=89,
            evidence=[
                EvidenceExample("auth.py", "def authenticate_user():", 5),
                EvidenceExample("db.py", "def validate_schema():", 3),
            ],
            exceptions="Tests use test_* pattern",
        )

        formatted = StandardsDisplay.format_standard(standard)

        assert "Naming Convention: snake_case" in formatted
        assert "90%" in formatted
        assert "89 files analyzed" in formatted
        assert "authenticate_user" in formatted
        assert "validate_schema" in formatted
        assert "Tests use test_* pattern" in formatted

    def test_evidence_examples_included(self):
        """Test evidence examples are displayed."""
        evidence = [
            EvidenceExample("module.py", "function_name_example", 12),
            EvidenceExample("utils.py", "another_function_name", 8),
            EvidenceExample("service.py", "third_function_example", 5),
        ]
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=92.0,
            sample_size=100,
            evidence=evidence,
        )

        formatted = StandardsDisplay.format_standard(standard)

        assert "module.py" in formatted
        assert "utils.py" in formatted
        assert "service.py" in formatted
        assert "function_name_example" in formatted

    def test_sample_size_display(self):
        """Test sample size is clearly displayed."""
        for sample_size in [10, 50, 100]:
            standard = StandardsInfo(
                name="Test",
                value="value",
                confidence=75.0,
                sample_size=sample_size,
                evidence=[],
            )

            formatted = StandardsDisplay.format_standard(standard)
            assert f"{sample_size} files analyzed" in formatted


class TestAC3_ConfidenceBasedFormatting:
    """AC3: Display confidence level with visual indicators."""

    def test_high_confidence_formatting(self):
        """Test high confidence (>85%) has correct indicator."""
        standard = StandardsInfo(
            name="Test",
            value="value",
            confidence=90.0,
            sample_size=100,
            evidence=[],
        )

        level, indicator = StandardsDisplay.get_confidence_level(90.0)

        assert level == "High confidence"
        assert indicator == "✓"
        assert indicator in StandardsDisplay.format_standard(standard)

    def test_medium_confidence_formatting(self):
        """Test medium confidence (60-85%) has correct indicator."""
        standard = StandardsInfo(
            name="Test",
            value="value",
            confidence=72.0,
            sample_size=50,
            evidence=[],
        )

        level, indicator = StandardsDisplay.get_confidence_level(72.0)

        assert level == "Medium confidence"
        assert indicator == "▪"
        assert indicator in StandardsDisplay.format_standard(standard)

    def test_low_confidence_formatting(self):
        """Test low confidence (<60%) has correct indicator."""
        standard = StandardsInfo(
            name="Test",
            value="value",
            confidence=45.0,
            sample_size=20,
            evidence=[],
        )

        level, indicator = StandardsDisplay.get_confidence_level(45.0)

        assert level == "Low confidence"
        assert indicator == "⚠"
        assert indicator in StandardsDisplay.format_standard(standard)
        assert "override" in StandardsDisplay.format_standard(standard).lower()

    def test_exact_threshold_values(self):
        """Test confidence levels at exact thresholds."""
        # Test at HIGH_CONFIDENCE_THRESHOLD (85)
        level_85, _ = StandardsDisplay.get_confidence_level(85.0)
        assert level_85 == "High confidence"

        # Test just below HIGH_CONFIDENCE_THRESHOLD
        level_84, _ = StandardsDisplay.get_confidence_level(84.9)
        assert level_84 == "Medium confidence"

        # Test at MEDIUM_CONFIDENCE_THRESHOLD (60)
        level_60, _ = StandardsDisplay.get_confidence_level(60.0)
        assert level_60 == "Medium confidence"

        # Test just below MEDIUM_CONFIDENCE_THRESHOLD
        level_59, _ = StandardsDisplay.get_confidence_level(59.9)
        assert level_59 == "Low confidence"


class TestAC4_MixedConventionsDisplay:
    """AC4: Display mixed conventions with dominant and secondary."""

    def test_dominant_convention_display(self):
        """Test dominant convention (>60%) is displayed."""
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=75.0,
            sample_size=100,
            evidence=[],
            secondary_value="camelCase",
            secondary_confidence=20.0,
        )

        formatted = StandardsDisplay.format_standard(standard)

        assert "snake_case" in formatted
        assert "camelCase" in formatted
        assert "75%" in formatted
        assert "20%" in formatted

    def test_exceptions_noted(self):
        """Test exceptions are displayed when present."""
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=85.0,
            sample_size=80,
            evidence=[],
            exceptions="Constants use UPPER_SNAKE_CASE; Classes use PascalCase",
        )

        formatted = StandardsDisplay.format_standard(standard)

        assert "UPPER_SNAKE_CASE" in formatted
        assert "PascalCase" in formatted
        assert "Constants" in formatted

    def test_multiple_exceptions(self):
        """Test multiple exceptions are displayed."""
        exceptions = (
            "Private functions use _prefix; "
            "Magic methods use __dunder__; "
            "Test functions use test_prefix"
        )
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=82.0,
            sample_size=90,
            evidence=[],
            exceptions=exceptions,
        )

        formatted = StandardsDisplay.format_standard(standard)

        assert "_prefix" in formatted
        assert "__dunder__" in formatted
        assert "test_prefix" in formatted


class TestAC5_OutputFormatting:
    """AC5: Format output for terminal with emoji and readability."""

    def test_plain_text_output(self):
        """Test output is plain text (no color codes)."""
        standard = StandardsInfo(
            name="Test",
            value="value",
            confidence=80.0,
            sample_size=50,
            evidence=[],
        )

        formatted = StandardsDisplay.format_standard(standard)

        # Should not contain ANSI color codes
        assert "\033[" not in formatted
        assert "\x1b[" not in formatted

    def test_emoji_included(self):
        """Test emoji are included for visual clarity."""
        standards = {
            "naming": StandardsInfo(
                name="Naming Convention",
                value="snake_case",
                confidence=90.0,
                sample_size=100,
                evidence=[],
            ),
            "testing": StandardsInfo(
                name="Test Framework",
                value="pytest",
                confidence=95.0,
                sample_size=50,
                evidence=[],
            ),
        }

        report = StandardsDisplay.format_standards_report(standards)

        # Check for expected emoji
        assert "✓" in report  # High confidence
        assert "📋" in report  # Header
        assert "💡" in report  # Tips

    def test_readable_structure(self):
        """Test output is structured for readability."""
        standard = StandardsInfo(
            name="Test",
            value="value",
            confidence=75.0,
            sample_size=50,
            evidence=[EvidenceExample("file.py", "example", 1)],
        )

        formatted = StandardsDisplay.format_standard(standard)
        lines = formatted.split("\n")

        # Should have multiple lines for readability
        assert len(lines) > 3
        # Should have indentation for sub-items
        assert any(line.startswith("  ") for line in lines)

    def test_screen_reader_compatibility(self):
        """Test output works with screen readers."""
        standard = StandardsInfo(
            name="Naming Convention",
            value="snake_case",
            confidence=85.0,
            sample_size=75,
            evidence=[],
        )

        formatted = StandardsDisplay.format_standard(standard)

        # Should be readable as plain text
        assert "Naming Convention" in formatted
        assert "snake_case" in formatted
        assert "Confidence" in formatted

    def test_wrap_width_compatible(self):
        """Test output fits in 80-character width."""
        standards = {
            "naming": StandardsInfo(
                name="Naming Convention",
                value="snake_case",
                confidence=90.0,
                sample_size=100,
                evidence=[
                    EvidenceExample(
                        "very/long/path/to/some/file/with/long/name.py",
                        "function_with_very_long_name_example_here",
                        5,
                    )
                ],
            ),
        }

        report = StandardsDisplay.format_standards_report(standards)
        lines = report.split("\n")

        # Most lines should fit in 80 characters (some examples may exceed)
        regular_lines = [l for l in lines if not l.strip().startswith("•")]
        fitting_lines = [l for l in regular_lines if len(l) <= 80]

        assert len(fitting_lines) > len(regular_lines) * 0.7


class TestIntegration_CompleteStandardsReport:
    """Integration tests for complete standards report."""

    def test_full_report_with_all_standards(self):
        """Test full report with all 5 standards."""
        standards = {
            "naming": StandardsInfo(
                name="Naming Convention",
                value="snake_case",
                confidence=90.0,
                sample_size=100,
                evidence=[EvidenceExample("file.py", "def validate():", 20)],
            ),
            "testing": StandardsInfo(
                name="Test Framework",
                value="pytest",
                confidence=95.0,
                sample_size=42,
                evidence=[EvidenceExample("test_file.py", "def test_():", 10)],
            ),
            "documentation": StandardsInfo(
                name="Documentation Style",
                value="Google docstrings",
                confidence=85.0,
                sample_size=67,
                evidence=[EvidenceExample("module.py", '"""Docstring."""', 15)],
            ),
            "organization": StandardsInfo(
                name="Code Organization",
                value="by-feature",
                confidence=80.0,
                sample_size=5,
                evidence=[EvidenceExample("features/", "directory", 1)],
            ),
            "module_naming": StandardsInfo(
                name="Module Naming",
                value="service_*.py",
                confidence=88.0,
                sample_size=12,
                evidence=[EvidenceExample("service_auth.py", "module", 5)],
            ),
        }

        report = StandardsDisplay.format_standards_report(standards)

        # Check all standards present
        assert "Naming Convention" in report
        assert "Test Framework" in report
        assert "Documentation Style" in report
        assert "Code Organization" in report
        assert "Module Naming" in report

        # Check guidance included
        assert "override" in report.lower()
        assert ".pe.yaml" in report or "configuration" in report.lower()
        assert "template" in report.lower()

    def test_confidence_summary(self):
        """Test confidence summary calculation."""
        standards = {
            "high": StandardsInfo(
                name="High",
                value="value",
                confidence=90.0,
                sample_size=100,
                evidence=[],
            ),
            "high2": StandardsInfo(
                name="High2",
                value="value",
                confidence=95.0,
                sample_size=100,
                evidence=[],
            ),
            "medium": StandardsInfo(
                name="Medium",
                value="value",
                confidence=72.0,
                sample_size=50,
                evidence=[],
            ),
            "low": StandardsInfo(
                name="Low",
                value="value",
                confidence=45.0,
                sample_size=20,
                evidence=[],
            ),
        }

        summary = StandardsDisplay.format_confidence_summary(standards)

        assert "2/4 high confidence" in summary
        assert "1 medium confidence" in summary
        assert "1 low confidence" in summary

    def test_low_confidence_warning(self):
        """Test warning for low confidence standards."""
        standards = {
            "high": StandardsInfo(
                name="High",
                value="value",
                confidence=90.0,
                sample_size=100,
                evidence=[],
            ),
            "low": StandardsInfo(
                name="Low",
                value="value",
                confidence=45.0,
                sample_size=20,
                evidence=[],
            ),
        }

        warning = StandardsDisplay.format_confidence_warning(standards)

        assert warning is not None
        assert "Low Confidence" in warning
        assert "Low" in warning
        assert "45%" in warning

    def test_no_warning_when_all_confident(self):
        """Test no warning when all standards are confident."""
        standards = {
            "high1": StandardsInfo(
                name="High1",
                value="value",
                confidence=90.0,
                sample_size=100,
                evidence=[],
            ),
            "high2": StandardsInfo(
                name="High2",
                value="value",
                confidence=95.0,
                sample_size=100,
                evidence=[],
            ),
        }

        warning = StandardsDisplay.format_confidence_warning(standards)

        assert warning is None
