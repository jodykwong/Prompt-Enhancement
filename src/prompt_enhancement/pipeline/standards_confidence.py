"""
Standards confidence scoring and aggregation module.
Aggregates confidence scores from all detection modules and generates quality metrics.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class QualityGateLevel(str, Enum):
    """Quality gate levels for standards detection"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAIL = "fail"


@dataclass
class DetectorConfidence:
    """Confidence score from a single detector"""
    detector_name: str
    confidence: float
    weight: float
    contribution: float = 0.0


@dataclass
class FactorAnalysis:
    """Analysis of confidence factors"""
    strongest_detectors: List[str] = field(default_factory=list)
    weakest_detectors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    code_standards_confidence: float = 0.0
    testing_standards_confidence: float = 0.0
    documentation_standards_confidence: float = 0.0
    language_detection_confidence: float = 0.0


@dataclass
class StandardsConfidenceReport:
    """Complete confidence report for standards detection"""
    overall_confidence: float
    quality_gate: QualityGateLevel
    detector_scores: Dict[str, float] = field(default_factory=dict)
    standard_scores: Dict[str, float] = field(default_factory=dict)
    low_confidence_standards: List[str] = field(default_factory=list)
    quality_rationale: str = ""
    factor_analysis: Optional[FactorAnalysis] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"


class StandardsConfidenceAggregator:
    """Aggregates confidence scores from all detection modules"""

    # Weights for each detector (sum to 1.0)
    DETECTOR_WEIGHTS = {
        "project_type": 0.20,
        "indicator_files": 0.10,
        "git_history": 0.05,
        "fingerprinting": 0.05,
        "naming_conventions": 0.15,
        "test_framework": 0.15,
        "documentation_style": 0.15,
        "code_organization": 0.15,
    }

    # Quality gate thresholds
    QUALITY_GATES = {
        QualityGateLevel.HIGH: 0.85,
        QualityGateLevel.MEDIUM: 0.65,
        QualityGateLevel.LOW: 0.50,
        QualityGateLevel.FAIL: 0.0,
    }

    def __init__(self):
        """Initialize aggregator"""
        pass

    def aggregate_confidence(
        self,
        project_type_confidence: Optional[float] = None,
        indicator_files_confidence: Optional[float] = None,
        git_history_confidence: Optional[float] = None,
        fingerprinting_confidence: Optional[float] = None,
        naming_conventions_confidence: Optional[float] = None,
        test_framework_confidence: Optional[float] = None,
        documentation_style_confidence: Optional[float] = None,
        code_organization_confidence: Optional[float] = None,
    ) -> StandardsConfidenceReport:
        """
        Aggregate confidence scores from all detectors.

        Args:
            Individual confidence scores from each detector (0.0-1.0 or None)

        Returns:
            StandardsConfidenceReport with aggregated scores and analysis
        """
        # Collect detector scores
        detector_scores = {
            "project_type": project_type_confidence,
            "indicator_files": indicator_files_confidence,
            "git_history": git_history_confidence,
            "fingerprinting": fingerprinting_confidence,
            "naming_conventions": naming_conventions_confidence,
            "test_framework": test_framework_confidence,
            "documentation_style": documentation_style_confidence,
            "code_organization": code_organization_confidence,
        }

        # Validate and normalize scores
        normalized_scores = {}
        valid_count = 0
        for detector, score in detector_scores.items():
            if score is not None:
                # Clamp to 0.0-1.0 range
                score = max(0.0, min(1.0, score))
                normalized_scores[detector] = score
                valid_count += 1
            else:
                normalized_scores[detector] = None

        # Calculate weighted average
        overall_confidence = self._calculate_weighted_confidence(normalized_scores)

        # Determine quality gate
        quality_gate = self._determine_quality_gate(overall_confidence)

        # Get per-standard scores
        standard_scores = self._get_standard_scores(normalized_scores)

        # Identify low-confidence standards
        low_confidence_standards = self._identify_low_confidence_standards(
            standard_scores
        )

        # Generate quality rationale
        quality_rationale = self._generate_quality_rationale(
            overall_confidence, quality_gate, valid_count
        )

        # Perform factor analysis
        factor_analysis = self._perform_factor_analysis(normalized_scores)

        return StandardsConfidenceReport(
            overall_confidence=overall_confidence,
            quality_gate=quality_gate,
            detector_scores=normalized_scores,
            standard_scores=standard_scores,
            low_confidence_standards=low_confidence_standards,
            quality_rationale=quality_rationale,
            factor_analysis=factor_analysis,
        )

    def _calculate_weighted_confidence(self, scores: Dict[str, Optional[float]]) -> float:
        """Calculate weighted average confidence"""
        total_weighted = 0.0
        total_weight = 0.0

        for detector, score in scores.items():
            if score is not None:
                weight = self.DETECTOR_WEIGHTS.get(detector, 0.0)
                total_weighted += score * weight
                total_weight += weight

        # Calculate weighted average
        if total_weight > 0:
            return total_weighted / total_weight
        else:
            return 0.0

    def _determine_quality_gate(self, confidence: float) -> QualityGateLevel:
        """Determine quality gate level based on confidence"""
        if confidence >= self.QUALITY_GATES[QualityGateLevel.HIGH]:
            return QualityGateLevel.HIGH
        elif confidence >= self.QUALITY_GATES[QualityGateLevel.MEDIUM]:
            return QualityGateLevel.MEDIUM
        elif confidence >= self.QUALITY_GATES[QualityGateLevel.LOW]:
            return QualityGateLevel.LOW
        else:
            return QualityGateLevel.FAIL

    def _get_standard_scores(self, scores: Dict[str, Optional[float]]) -> Dict[str, float]:
        """Get per-standard confidence scores"""
        standard_scores = {
            "naming_conventions": scores.get("naming_conventions", 0.0) or 0.0,
            "test_framework": scores.get("test_framework", 0.0) or 0.0,
            "documentation_style": scores.get("documentation_style", 0.0) or 0.0,
            "code_organization": scores.get("code_organization", 0.0) or 0.0,
            "project_type": scores.get("project_type", 0.0) or 0.0,
        }

        # Sort by confidence (highest first)
        return dict(sorted(standard_scores.items(), key=lambda x: x[1], reverse=True))

    def _identify_low_confidence_standards(self, standard_scores: Dict[str, float]) -> List[str]:
        """Identify standards with low confidence (< 0.5)"""
        return [
            standard for standard, score in standard_scores.items()
            if score < 0.5 and score > 0.0
        ]

    def _generate_quality_rationale(
        self,
        confidence: float,
        gate: QualityGateLevel,
        valid_count: int
    ) -> str:
        """Generate rationale for quality gate decision"""
        if gate == QualityGateLevel.HIGH:
            return f"Overall confidence {confidence:.1%} indicates high reliability in detected standards. Use results with confidence."
        elif gate == QualityGateLevel.MEDIUM:
            return f"Overall confidence {confidence:.1%} indicates moderate reliability. Use detected standards with caution."
        elif gate == QualityGateLevel.LOW:
            return f"Overall confidence {confidence:.1%} indicates low reliability. Request user confirmation before using standards."
        else:
            return f"Overall confidence {confidence:.1%} indicates detection failures. Standards should not be used without review."

    def _perform_factor_analysis(self, scores: Dict[str, Optional[float]]) -> FactorAnalysis:
        """Perform analysis of confidence factors"""
        analysis = FactorAnalysis()

        # Identify strongest detectors
        sorted_detectors = sorted(
            [(k, v) for k, v in scores.items() if v is not None],
            key=lambda x: x[1],
            reverse=True
        )
        analysis.strongest_detectors = [name for name, _ in sorted_detectors[:3]]

        # Identify weakest detectors
        analysis.weakest_detectors = [name for name, _ in sorted_detectors[-3:] if name]

        # Calculate category confidence
        analysis.code_standards_confidence = (
            (scores.get("naming_conventions") or 0.0 + scores.get("code_organization") or 0.0) / 2
        )
        analysis.testing_standards_confidence = scores.get("test_framework") or 0.0
        analysis.documentation_standards_confidence = scores.get("documentation_style") or 0.0
        analysis.language_detection_confidence = scores.get("project_type") or 0.0

        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(scores)

        return analysis

    def _generate_recommendations(self, scores: Dict[str, Optional[float]]) -> List[str]:
        """Generate actionable recommendations for improvement"""
        recommendations = []

        # Check for low-confidence detectors and provide recommendations
        if (scores.get("naming_conventions") or 0.0) < 0.5:
            recommendations.append(
                "Standardize naming conventions (snake_case, camelCase, etc.) for better detection"
            )

        if (scores.get("documentation_style") or 0.0) < 0.5:
            recommendations.append(
                "Add docstrings/comments to code for better documentation style detection"
            )

        if (scores.get("test_framework") or 0.0) < 0.5:
            recommendations.append(
                "Clarify test framework usage by adding configuration files or test imports"
            )

        if (scores.get("code_organization") or 0.0) < 0.5:
            recommendations.append(
                "Organize code into clear directory structure (src/, lib/, test/, etc.)"
            )

        if (scores.get("project_type") or 0.0) < 0.5:
            recommendations.append(
                "Add language-specific marker files (package.json, setup.py, go.mod, etc.)"
            )

        return recommendations
