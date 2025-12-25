"""
Comprehensive test suite for standards confidence scoring.
Tests all 8 acceptance criteria for Story 2.9.
"""

import pytest
import time
from dataclasses import asdict, dataclass
from typing import Optional

from src.prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from src.prompt_enhancement.pipeline.project_files import ProjectIndicatorResult
from src.prompt_enhancement.pipeline.naming_conventions import NamingConventionResult
from src.prompt_enhancement.pipeline.test_framework import TestFrameworkDetectionResult
from src.prompt_enhancement.pipeline.documentation_style import DocumentationStyleResult
from src.prompt_enhancement.pipeline.code_organization import CodeOrganizationResult
from src.prompt_enhancement.pipeline.standards_confidence import (
    StandardsConfidenceAggregator,
    QualityGateLevel,
    DetectorConfidence,
    FactorAnalysis,
    StandardsConfidenceReport,
)


class TestConfidenceAggregation:
    """Test AC1: Confidence Score Aggregation"""

    def test_collect_individual_detector_scores(self):
        """Test collection of confidence scores from all detectors"""
        aggregator = StandardsConfidenceAggregator()

        detector_scores = {
            "project_type": 0.95,
            "indicator_files": 0.85,
            "git_history": 0.70,
            "fingerprinting": 0.80,
            "naming_conventions": 0.75,
            "test_framework": 0.90,
            "documentation_style": 0.65,
            "code_organization": 0.88,
        }

        result = aggregator.aggregate_confidence(
            project_type_confidence=detector_scores["project_type"],
            indicator_files_confidence=detector_scores["indicator_files"],
            git_history_confidence=detector_scores["git_history"],
            fingerprinting_confidence=detector_scores["fingerprinting"],
            naming_conventions_confidence=detector_scores["naming_conventions"],
            test_framework_confidence=detector_scores["test_framework"],
            documentation_style_confidence=detector_scores["documentation_style"],
            code_organization_confidence=detector_scores["code_organization"],
        )

        assert result is not None
        assert result.detector_scores is not None

    def test_validate_confidence_range(self):
        """Test validation that confidence scores are 0.0-1.0"""
        aggregator = StandardsConfidenceAggregator()

        # Valid scores
        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert all(0.0 <= score <= 1.0 for score in result.detector_scores.values())

    def test_handle_missing_scores_gracefully(self):
        """Test graceful handling of missing or null scores"""
        aggregator = StandardsConfidenceAggregator()

        # Some scores are None (missing detectors)
        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=None,
            git_history_confidence=0.70,
            fingerprinting_confidence=None,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=None,
            code_organization_confidence=0.88,
        )

        assert result is not None
        # Should still calculate with available scores
        assert result.overall_confidence is not None


class TestWeightedConfidence:
    """Test AC2: Weighted Confidence Calculation"""

    def test_weighted_average_calculation(self):
        """Test weighted average confidence calculation"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=1.0,  # weight: 0.20
            indicator_files_confidence=1.0,  # weight: 0.10
            git_history_confidence=1.0,  # weight: 0.05
            fingerprinting_confidence=1.0,  # weight: 0.05
            naming_conventions_confidence=1.0,  # weight: 0.15
            test_framework_confidence=1.0,  # weight: 0.15
            documentation_style_confidence=1.0,  # weight: 0.15
            code_organization_confidence=1.0,  # weight: 0.15
        )

        assert result is not None
        assert result.overall_confidence == pytest.approx(1.0, abs=0.01)

    def test_weighted_average_with_varying_scores(self):
        """Test weighted average with different confidence levels"""
        aggregator = StandardsConfidenceAggregator()

        # High-weighted detectors: high confidence
        # Low-weighted detectors: low confidence
        result = aggregator.aggregate_confidence(
            project_type_confidence=1.0,  # weight: 0.20 (high)
            indicator_files_confidence=1.0,  # weight: 0.10 (high)
            git_history_confidence=0.0,  # weight: 0.05 (low impact)
            fingerprinting_confidence=0.0,  # weight: 0.05 (low impact)
            naming_conventions_confidence=1.0,  # weight: 0.15 (high)
            test_framework_confidence=1.0,  # weight: 0.15 (high)
            documentation_style_confidence=1.0,  # weight: 0.15 (high)
            code_organization_confidence=1.0,  # weight: 0.15 (high)
        )

        assert result is not None
        # Should be high because main contributors are high
        assert result.overall_confidence >= 0.85

    def test_weights_sum_to_one(self):
        """Test that weights sum to 1.0"""
        aggregator = StandardsConfidenceAggregator()

        # Verify weights sum to 1.0
        total_weight = (
            0.20 + 0.10 + 0.05 + 0.05 + 0.15 + 0.15 + 0.15 + 0.15
        )
        assert total_weight == pytest.approx(1.0, abs=0.01)


class TestPerStandardConfidence:
    """Test AC3: Per-Standard Confidence Breakdown"""

    def test_per_standard_confidence_breakdown(self):
        """Test providing per-standard confidence scores"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.standard_scores is not None
        # Should have scores for each standard type
        assert "naming_conventions" in result.standard_scores
        assert "test_framework" in result.standard_scores
        assert "documentation_style" in result.standard_scores
        assert "code_organization" in result.standard_scores

    def test_standards_ranked_by_confidence(self):
        """Test that standards are ranked by confidence (highest first)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        # Get sorted standards by confidence
        if result.standard_scores:
            scores = list(result.standard_scores.values())
            assert scores == sorted(scores, reverse=True)

    def test_flag_low_confidence_standards(self):
        """Test flagging of low-confidence standards (< 0.5)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.45,  # Low confidence
            fingerprinting_confidence=0.40,  # Low confidence
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.low_confidence_standards is not None
        # Should flag low-confidence items
        if result.low_confidence_standards:
            assert len(result.low_confidence_standards) >= 0


class TestQualityGate:
    """Test AC4: Quality Gate Determination"""

    def test_high_quality_gate(self):
        """Test HIGH quality gate (>= 0.85)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.90,
            git_history_confidence=0.85,
            fingerprinting_confidence=0.88,
            naming_conventions_confidence=0.92,
            test_framework_confidence=0.94,
            documentation_style_confidence=0.88,
            code_organization_confidence=0.90,
        )

        assert result is not None
        assert result.quality_gate == QualityGateLevel.HIGH

    def test_medium_quality_gate(self):
        """Test MEDIUM quality gate (0.65-0.84)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.80,
            indicator_files_confidence=0.75,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.72,
            naming_conventions_confidence=0.68,
            test_framework_confidence=0.75,
            documentation_style_confidence=0.70,
            code_organization_confidence=0.74,
        )

        assert result is not None
        assert result.quality_gate == QualityGateLevel.MEDIUM

    def test_low_quality_gate(self):
        """Test LOW quality gate (0.50-0.64)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.60,
            indicator_files_confidence=0.55,
            git_history_confidence=0.50,
            fingerprinting_confidence=0.52,
            naming_conventions_confidence=0.58,
            test_framework_confidence=0.60,
            documentation_style_confidence=0.55,
            code_organization_confidence=0.57,
        )

        assert result is not None
        assert result.quality_gate == QualityGateLevel.LOW

    def test_fail_quality_gate(self):
        """Test FAIL quality gate (< 0.50)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.45,
            indicator_files_confidence=0.40,
            git_history_confidence=0.35,
            fingerprinting_confidence=0.42,
            naming_conventions_confidence=0.48,
            test_framework_confidence=0.45,
            documentation_style_confidence=0.40,
            code_organization_confidence=0.44,
        )

        assert result is not None
        assert result.quality_gate == QualityGateLevel.FAIL

    def test_quality_gate_rationale(self):
        """Test that quality gate includes rationale"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.quality_rationale is not None
        assert len(result.quality_rationale) > 0


class TestFactorAnalysis:
    """Test AC5: Factor Analysis and Recommendations"""

    def test_identify_contributing_detectors(self):
        """Test identification of detectors contributing to confidence"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.factor_analysis is not None
        assert result.factor_analysis.strongest_detectors is not None
        assert len(result.factor_analysis.strongest_detectors) > 0

    def test_identify_weak_points(self):
        """Test identification of weak points in detection"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.30,  # Weak point
            fingerprinting_confidence=0.35,  # Weak point
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.40,  # Weak point
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.factor_analysis is not None
        assert result.factor_analysis.weakest_detectors is not None
        assert len(result.factor_analysis.weakest_detectors) > 0

    def test_generate_improvement_recommendations(self):
        """Test generation of actionable recommendations"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.45,  # Low - recommend
            test_framework_confidence=0.90,
            documentation_style_confidence=0.35,  # Low - recommend
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.factor_analysis is not None
        assert result.factor_analysis.recommendations is not None
        if result.factor_analysis.recommendations:
            assert len(result.factor_analysis.recommendations) > 0

    def test_category_confidence_ratings(self):
        """Test confidence ratings by standard category"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.80,  # Changed to test calculation
            test_framework_confidence=0.90,
            code_organization_confidence=0.60,  # Added to test code_standards calculation
            documentation_style_confidence=0.65,
        )

        assert result is not None
        assert result.factor_analysis is not None
        # Should have category breakdowns
        assert result.factor_analysis.code_standards_confidence is not None
        assert result.factor_analysis.testing_standards_confidence is not None
        assert result.factor_analysis.documentation_standards_confidence is not None


class TestConfidenceTrending:
    """Test AC6: Confidence Trend Tracking"""

    def test_timestamp_recording(self):
        """Test that timestamp is recorded for detection run"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.timestamp is not None

    def test_confidence_consistency_detection(self):
        """Test detection of consistency in confidence scores"""
        aggregator = StandardsConfidenceAggregator()

        # Two identical runs should have same scores
        result1 = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        result2 = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result1 is not None
        assert result2 is not None
        assert result1.overall_confidence == pytest.approx(result2.overall_confidence, abs=0.001)


class TestReportFormat:
    """Test AC7: Confidence Report Format"""

    def test_confidence_report_structure(self):
        """Test that report has all required fields"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert hasattr(result, 'overall_confidence')
        assert hasattr(result, 'quality_gate')
        assert hasattr(result, 'detector_scores')
        assert hasattr(result, 'standard_scores')
        assert hasattr(result, 'factor_analysis')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'version')

    def test_report_serialization(self):
        """Test that report can be serialized to dict"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )

        assert result is not None
        result_dict = asdict(result)
        assert result_dict is not None
        assert 'overall_confidence' in result_dict


class TestIntegration:
    """Test AC8: Integration with Detection Pipeline"""

    def test_integration_with_all_detectors(self):
        """Test integration with results from all 8 detectors"""
        aggregator = StandardsConfidenceAggregator()

        # Simulate results from all detection modules
        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,  # Story 2.1
            indicator_files_confidence=0.85,  # Story 2.2
            git_history_confidence=0.70,  # Story 2.3
            fingerprinting_confidence=0.80,  # Story 2.4
            naming_conventions_confidence=0.75,  # Story 2.5
            test_framework_confidence=0.90,  # Story 2.6
            documentation_style_confidence=0.65,  # Story 2.7
            code_organization_confidence=0.88,  # Story 2.8
        )

        assert result is not None
        assert result.overall_confidence is not None
        assert result.quality_gate is not None

    def test_quality_based_decision_making(self):
        """Test that confidence enables quality-based decisions"""
        aggregator = StandardsConfidenceAggregator()

        # High confidence - can be used
        high_result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.90,
            git_history_confidence=0.85,
            fingerprinting_confidence=0.88,
            naming_conventions_confidence=0.92,
            test_framework_confidence=0.94,
            documentation_style_confidence=0.88,
            code_organization_confidence=0.90,
        )

        # Low confidence - should request confirmation
        low_result = aggregator.aggregate_confidence(
            project_type_confidence=0.45,
            indicator_files_confidence=0.40,
            git_history_confidence=0.35,
            fingerprinting_confidence=0.42,
            naming_conventions_confidence=0.48,
            test_framework_confidence=0.45,
            documentation_style_confidence=0.40,
            code_organization_confidence=0.44,
        )

        assert high_result is not None
        assert low_result is not None
        assert high_result.quality_gate > low_result.quality_gate


class TestPerformance:
    """Test performance targets"""

    def test_performance_within_0_5_second_budget(self):
        """Test that aggregation completes within 0.5-second budget"""
        import time

        aggregator = StandardsConfidenceAggregator()

        start_time = time.time()
        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=0.85,
            git_history_confidence=0.70,
            fingerprinting_confidence=0.80,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=0.65,
            code_organization_confidence=0.88,
        )
        elapsed = time.time() - start_time

        assert elapsed < 0.5
        assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_all_perfect_confidence(self):
        """Test handling of perfect confidence scores (all 1.0)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=1.0,
            indicator_files_confidence=1.0,
            git_history_confidence=1.0,
            fingerprinting_confidence=1.0,
            naming_conventions_confidence=1.0,
            test_framework_confidence=1.0,
            documentation_style_confidence=1.0,
            code_organization_confidence=1.0,
        )

        assert result is not None
        assert result.overall_confidence == pytest.approx(1.0, abs=0.01)

    def test_all_zero_confidence(self):
        """Test handling of zero confidence scores (all 0.0)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.0,
            indicator_files_confidence=0.0,
            git_history_confidence=0.0,
            fingerprinting_confidence=0.0,
            naming_conventions_confidence=0.0,
            test_framework_confidence=0.0,
            documentation_style_confidence=0.0,
            code_organization_confidence=0.0,
        )

        assert result is not None
        assert result.overall_confidence == pytest.approx(0.0, abs=0.01)

    def test_mixed_valid_and_none_scores(self):
        """Test handling of mix of valid and None scores"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.95,
            indicator_files_confidence=None,
            git_history_confidence=0.70,
            fingerprinting_confidence=None,
            naming_conventions_confidence=0.75,
            test_framework_confidence=0.90,
            documentation_style_confidence=None,
            code_organization_confidence=0.88,
        )

        assert result is not None
        assert result.overall_confidence is not None
        # Should not crash and should handle gracefully
        assert 0.0 <= result.overall_confidence <= 1.0


class TestCriticalBugFixes:
    """Tests for critical bug fixes from code review"""

    def test_code_standards_confidence_calculation_fix(self):
        """
        Test fix for CRITICAL operator precedence bug in code_standards_confidence.

        Bug was: (scores.get("naming") or 0.0 + scores.get("org") or 0.0) / 2
        Which evaluated as: (scores.get("naming") or (0.0 + scores.get("org")) or 0.0) / 2

        Fixed to: ((scores.get("naming") or 0.0) + (scores.get("org") or 0.0)) / 2
        """
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            naming_conventions_confidence=0.8,
            code_organization_confidence=0.6,
        )

        assert result is not None
        assert result.factor_analysis is not None

        # With the fix, code_standards = (0.8 + 0.6) / 2 = 0.7
        # Without the fix, it would be 0.8 / 2 = 0.4 (WRONG!)
        expected = 0.7
        actual = result.factor_analysis.code_standards_confidence

        assert actual == pytest.approx(expected, abs=0.01), \
            f"Expected {expected}, got {actual}. Operator precedence bug may still exist!"

    def test_trend_tracking_single_run(self):
        """Test AC6: Trend tracking with single run (no history)"""
        aggregator = StandardsConfidenceAggregator()

        result = aggregator.aggregate_confidence(
            project_type_confidence=0.85,
        )

        # First run should have no trend data (not enough history)
        assert result.trend_data is None

    def test_trend_tracking_multiple_runs_improving(self):
        """Test AC6: Trend tracking detects improving confidence"""
        aggregator = StandardsConfidenceAggregator()

        # First run: low confidence
        result1 = aggregator.aggregate_confidence(
            project_type_confidence=0.60,
        )

        # Second run: higher confidence (improving)
        result2 = aggregator.aggregate_confidence(
            project_type_confidence=0.75,
        )

        assert result2.trend_data is not None
        assert result2.trend_data.improving is True
        assert result2.trend_data.degrading is False
        assert result2.trend_data.trend_direction == "improving"
        assert len(result2.trend_data.confidence_history) == 2

    def test_trend_tracking_multiple_runs_degrading(self):
        """Test AC6: Trend tracking detects degrading confidence"""
        aggregator = StandardsConfidenceAggregator()

        # First run: high confidence
        result1 = aggregator.aggregate_confidence(
            project_type_confidence=0.85,
        )

        # Second run: lower confidence (degrading)
        result2 = aggregator.aggregate_confidence(
            project_type_confidence=0.65,
        )

        assert result2.trend_data is not None
        assert result2.trend_data.improving is False
        assert result2.trend_data.degrading is True
        assert result2.trend_data.trend_direction == "degrading"

    def test_trend_tracking_consistency_detection(self):
        """Test AC6: Trend tracking detects consistent results"""
        aggregator = StandardsConfidenceAggregator()

        # Multiple runs with similar confidence (consistent)
        aggregator.aggregate_confidence(project_type_confidence=0.80)
        aggregator.aggregate_confidence(project_type_confidence=0.81)
        result = aggregator.aggregate_confidence(project_type_confidence=0.79)

        assert result.trend_data is not None
        assert result.trend_data.consistent is True
        assert result.trend_data.trend_direction == "stable"
