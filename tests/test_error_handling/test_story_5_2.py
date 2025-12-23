"""Tests for Story 5.2: Graceful Degradation Mechanism."""

import pytest
from src.prompt_enhancement.error_handling.degradation import (
    DegradationLevel,
    DegradationInfo,
    DegradationStrategy,
)


class TestDegradationAC1:
    """AC1: Project detection failure degradation."""

    def test_project_detection_fails_degrades_to_level_3(self):
        """Test project detection failure → Level 3."""
        info = DegradationStrategy.determine_level(
            project_detected=False,
            standards_confidence=1.0,
        )
        assert info.level == DegradationLevel.GENERIC

    def test_degradation_info_includes_missing_component(self):
        """Test degradation info includes missing components."""
        info = DegradationStrategy.determine_level(
            project_detected=False,
            standards_confidence=1.0,
        )
        assert len(info.missing_components) > 0
        assert "Project context" in info.missing_components

    def test_degradation_info_includes_reason(self):
        """Test degradation info includes reason."""
        info = DegradationStrategy.determine_level(
            project_detected=False,
            standards_confidence=1.0,
        )
        assert info.reason is not None
        assert len(info.reason) > 0


class TestDegradationAC2:
    """AC2: Low confidence standards detection degradation."""

    def test_low_confidence_degrades_to_level_2(self):
        """Test <60% confidence → Level 2."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.45,
        )
        assert info.level == DegradationLevel.WITHOUT_STANDARDS

    def test_high_confidence_stays_level_1(self):
        """Test >=60% confidence stays Level 1."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.75,
        )
        assert info.level == DegradationLevel.FULL

    def test_boundary_confidence_60_percent(self):
        """Test exactly 60% confidence threshold."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.60,
        )
        assert info.level == DegradationLevel.FULL

    def test_boundary_confidence_59_percent(self):
        """Test just below 60% confidence threshold."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.59,
        )
        assert info.level == DegradationLevel.WITHOUT_STANDARDS

    def test_confidence_included_in_reason(self):
        """Test degradation reason includes confidence percentage."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.45,
        )
        assert "45%" in info.reason


class TestDegradationAC3:
    """AC3: API timeout degradation."""

    def test_api_timeout_with_cache_degrades_to_level_2(self):
        """Test timeout + cache available → Level 2."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            api_timeout=True,
            cache_available=True,
        )
        assert info.level == DegradationLevel.WITHOUT_STANDARDS
        assert info.cached is True

    def test_api_timeout_without_cache_degrades_to_level_3(self):
        """Test timeout - cache → Level 3."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            api_timeout=True,
            cache_available=False,
        )
        assert info.level == DegradationLevel.GENERIC

    def test_timeout_with_cache_shows_cache_note(self):
        """Test timeout with cache shows cache in reason."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            api_timeout=True,
            cache_available=True,
        )
        assert info.cached is True
        assert "cache" in info.reason.lower()


class TestDegradationAC4:
    """AC4: File access restriction degradation."""

    def test_permission_denied_affects_degradation(self):
        """Test file access restriction triggers degradation."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.75,
            file_access_denied=True,
        )
        assert info.level != DegradationLevel.FULL

    def test_permission_denied_included_in_missing(self):
        """Test file access included in missing components."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.75,
            file_access_denied=True,
        )
        assert any("access" in comp.lower() for comp in info.missing_components)


class TestDegradationAC5:
    """AC5: Degradation level selection logic and priority."""

    def test_full_enhancement_all_good(self):
        """Test Level 1 when all conditions met."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.85,
            api_timeout=False,
            file_access_denied=False,
        )
        assert info.level == DegradationLevel.FULL

    def test_multiple_failures_handled(self):
        """Test system handles multiple simultaneous failures."""
        info = DegradationStrategy.determine_level(
            project_detected=False,
            standards_confidence=0.30,
            api_timeout=True,
            cache_available=False,
            file_access_denied=True,
        )
        # Should degrade appropriately despite multiple issues
        assert info.level is not None
        assert len(info.missing_components) > 0

    def test_project_success_standards_fail_level_2(self):
        """Test project detected but standards fail → Level 2."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.45,
        )
        assert info.level == DegradationLevel.WITHOUT_STANDARDS

    def test_all_failures_level_3(self):
        """Test all major failures → Level 3."""
        info = DegradationStrategy.determine_level(
            project_detected=False,
            standards_confidence=0.20,
            api_timeout=True,
            cache_available=False,
            file_access_denied=True,
        )
        assert info.level == DegradationLevel.GENERIC


class TestDegradationAC6:
    """AC6: Degradation status tracking."""

    def test_degradation_info_has_level(self):
        """Test degradation info includes level."""
        info = DegradationStrategy.determine_level(project_detected=False)
        assert info.level is not None
        assert isinstance(info.level, DegradationLevel)

    def test_degradation_info_has_missing_components(self):
        """Test degradation info tracks missing components."""
        info = DegradationStrategy.determine_level(project_detected=False)
        assert hasattr(info, "missing_components")
        assert isinstance(info.missing_components, list)

    def test_degradation_info_has_reason(self):
        """Test degradation info includes reason."""
        info = DegradationStrategy.determine_level(project_detected=False)
        assert hasattr(info, "reason")
        assert isinstance(info.reason, str)

    def test_degradation_info_has_recommendation(self):
        """Test degradation info includes recommendation."""
        info = DegradationStrategy.determine_level(project_detected=False)
        assert hasattr(info, "recommendation")
        assert isinstance(info.recommendation, str)

    def test_format_degradation_info_includes_level(self):
        """Test formatted output includes level description."""
        info = DegradationStrategy.determine_level(project_detected=False)
        display = DegradationStrategy.format_degradation_info(info)
        assert "Degradation Level:" in display
        assert "Generic" in display or "Level 3" in display

    def test_format_degradation_info_includes_reason(self):
        """Test formatted output includes reason."""
        info = DegradationStrategy.determine_level(project_detected=False)
        display = DegradationStrategy.format_degradation_info(info)
        assert "Reason:" in display

    def test_format_degradation_info_includes_recommendation(self):
        """Test formatted output includes recommendation."""
        info = DegradationStrategy.determine_level(project_detected=False)
        display = DegradationStrategy.format_degradation_info(info)
        assert "Recommendation:" in display


class TestDegradationIntegration:
    """Integration tests for degradation strategy."""

    def test_level_descriptions_exist_for_all_levels(self):
        """Test all levels have descriptions."""
        for level in DegradationLevel:
            desc = DegradationStrategy.get_level_description(level)
            assert desc is not None
            assert len(desc) > 0

    def test_level_capabilities_exist_for_all_levels(self):
        """Test all levels have capability descriptions."""
        for level in DegradationLevel:
            caps = DegradationStrategy.get_level_capabilities(level)
            assert caps is not None
            assert len(caps) > 0

    def test_full_enhancement_has_all_capabilities(self):
        """Test Level 1 has all capabilities enabled."""
        caps = DegradationStrategy.get_level_capabilities(DegradationLevel.FULL)
        assert caps["project_detection"] is True
        assert caps["standards_detection"] is True
        assert caps["implementation_steps"] is True

    def test_level_2_has_project_not_standards(self):
        """Test Level 2 has project but not standards."""
        caps = DegradationStrategy.get_level_capabilities(
            DegradationLevel.WITHOUT_STANDARDS
        )
        assert caps["project_detection"] is True
        assert caps["standards_detection"] is False
        assert caps["implementation_steps"] is False

    def test_level_3_minimal_capabilities(self):
        """Test Level 3 has minimal capabilities."""
        caps = DegradationStrategy.get_level_capabilities(DegradationLevel.GENERIC)
        assert caps["project_detection"] is False
        assert caps["standards_detection"] is False

    def test_quality_assessment_levels(self):
        """Test quality assessment for each level."""
        quality_levels = {
            DegradationLevel.FULL: "High",
            DegradationLevel.WITHOUT_STANDARDS: "Reduced",
            DegradationLevel.GENERIC: "Minimum",
        }

        for level, expected_quality in quality_levels.items():
            caps = DegradationStrategy.get_level_capabilities(level)
            assert caps["quality"] == expected_quality

    def test_complex_scenario_project_timeout_low_confidence(self):
        """Test complex scenario: project detected but timeout + low confidence."""
        info = DegradationStrategy.determine_level(
            project_detected=True,
            standards_confidence=0.45,
            api_timeout=False,
        )
        # Should be Level 2 (low confidence, but no timeout)
        assert info.level == DegradationLevel.WITHOUT_STANDARDS

    def test_cache_affects_degradation_decision(self):
        """Test that cache availability affects timeout handling."""
        # Same scenario, different cache status
        info_with_cache = DegradationStrategy.determine_level(
            project_detected=True,
            api_timeout=True,
            cache_available=True,
        )
        info_without_cache = DegradationStrategy.determine_level(
            project_detected=True,
            api_timeout=True,
            cache_available=False,
        )

        assert info_with_cache.level != info_without_cache.level
        assert info_with_cache.cached is True
        assert info_without_cache.cached is False
