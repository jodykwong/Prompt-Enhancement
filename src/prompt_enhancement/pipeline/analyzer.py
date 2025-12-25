"""
Analysis Pipeline - Orchestrates project analysis phases.

Coordinates tech stack detection, standards detection, and other analysis
modules to provide comprehensive project insights.

This module implements the main P0.1-P0.3 analysis phases from Architecture.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from .tech_stack import ProjectTypeDetector, ProjectTypeDetectionResult
from .project_files import ProjectIndicatorFilesDetector, ProjectIndicatorResult
from .git_history import GitHistoryDetector, GitHistoryResult
from .standards_confidence import (
    StandardsConfidenceAggregator,
    StandardsConfidenceReport,
)


logger = logging.getLogger(__name__)


@dataclass
class ProjectAnalysisResult:
    """Complete project analysis result."""

    tech_stack: Optional[ProjectTypeDetectionResult] = None
    indicator_files: Optional[ProjectIndicatorResult] = None  # Story 2.2
    git_history: Optional[GitHistoryResult] = None  # Story 2.3
    confidence_report: Optional[StandardsConfidenceReport] = None
    analysis_success: bool = False
    analysis_time_seconds: float = 0.0
    errors: list = field(default_factory=list)


class ProjectAnalyzer:
    """
    Main analysis pipeline orchestrator.

    Coordinates project detection phases:
    - P0.1: Tech stack detection (Story 2.1)
    - P0.2: Standards detection (Stories 2.5-2.8)
    - P0.3: Confidence aggregation (Story 2.9)

    Attributes:
        project_root: Root directory of project to analyze
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            project_root: Root directory to analyze (defaults to current dir)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.confidence_aggregator = StandardsConfidenceAggregator()

    def analyze(self) -> ProjectAnalysisResult:
        """
        Run full project analysis pipeline.

        Returns:
            ProjectAnalysisResult with detection results
        """
        import time

        start_time = time.perf_counter()

        result = ProjectAnalysisResult()

        try:
            # Phase P0.1: Tech stack detection (Story 2.1)
            logger.info("Starting tech stack detection...")
            detector = ProjectTypeDetector(str(self.project_root))
            result.tech_stack = detector.detect_project_type()

            if result.tech_stack:
                logger.info(
                    f"Detected {result.tech_stack.primary_language.value} "
                    f"with {result.tech_stack.confidence:.2f} confidence"
                )
            else:
                logger.warning("Could not detect project type")

            # Phase P0.2: Project indicator files detection (Story 2.2)
            logger.info("Extracting project metadata from indicator files...")
            if result.tech_stack:
                indicator_detector = ProjectIndicatorFilesDetector(
                    str(self.project_root), result.tech_stack.primary_language
                )
                result.indicator_files = indicator_detector.extract_project_metadata()

                if result.indicator_files:
                    logger.info(
                        f"Found {len(result.indicator_files.files_found)} config files "
                        f"with {result.indicator_files.confidence:.2f} confidence"
                    )
                    if result.indicator_files.metadata:
                        meta = result.indicator_files.metadata
                        logger.info(
                            f"Project metadata: name={meta.name}, "
                            f"dependencies={len(meta.dependencies)}"
                        )
                else:
                    logger.warning(
                        "Could not extract project metadata from indicator files"
                    )

            # Phase P0.2: Git history analysis (Story 2.3)
            logger.info("Extracting Git history and development patterns...")
            git_detector = GitHistoryDetector(
                project_root=self.project_root,
                detected_language=(
                    result.tech_stack.primary_language if result.tech_stack else None
                ),
            )
            result.git_history = git_detector.extract_git_history()

            if result.git_history and result.git_history.git_available:
                logger.info(
                    f"Git analysis: {result.git_history.total_commits} commits, "
                    f"{len(result.git_history.contributors)} contributors, "
                    f"confidence={result.git_history.confidence:.2f}"
                )
            else:
                logger.info("Git history not available or accessible")

            # TODO: Add Phase P0.2 remaining: Standards detection (Stories 2.5-2.8)

            # Phase P0.3: Confidence aggregation (Story 2.9)
            logger.info("Aggregating confidence scores...")
            tech_confidence = (
                result.tech_stack.confidence if result.tech_stack else None
            )
            indicator_confidence = (
                result.indicator_files.confidence if result.indicator_files else None
            )
            git_confidence = (
                result.git_history.confidence if result.git_history else None
            )

            result.confidence_report = self.confidence_aggregator.aggregate_confidence(
                project_type_confidence=tech_confidence,
                indicator_files_confidence=indicator_confidence,
                git_history_confidence=git_confidence,
                # TODO: Add other detector confidences when implemented
                # etc.
            )

            if result.confidence_report:
                logger.info(
                    f"Overall confidence: {result.confidence_report.overall_confidence:.2f} "
                    f"({result.confidence_report.quality_gate.value})"
                )

            result.analysis_success = True

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            result.errors.append(str(e))
            result.analysis_success = False

        finally:
            result.analysis_time_seconds = time.perf_counter() - start_time

        return result

    def get_tech_stack(self) -> Optional[ProjectTypeDetectionResult]:
        """
        Quick tech stack detection only.

        Returns:
            ProjectTypeDetectionResult or None
        """
        detector = ProjectTypeDetector(str(self.project_root))
        return detector.detect_project_type()
