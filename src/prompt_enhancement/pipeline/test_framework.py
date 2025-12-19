"""
Test Framework Detector - Story 2.6.

Identifies which testing framework is used in a project.
Supports Python, JavaScript, and Java projects.
"""

import logging
import re
import time
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from .tech_stack import ProjectLanguage, ProjectTypeDetectionResult
from .project_files import ProjectIndicatorResult
from ..cli.performance import PerformanceTracker  # FIX CRITICAL #1
from .file_access import FileAccessHandler  # FIX CRITICAL #2


logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================


class FrameworkType(Enum):
    """
    Supported test frameworks.

    FIX HIGH #3: Renamed from TestFrameworkType to avoid pytest collection warnings.
    """

    # Python
    PYTEST = "pytest"
    UNITTEST = "unittest"
    NOSE = "nose"
    HYPOTHESIS = "hypothesis"

    # JavaScript
    JEST = "jest"
    MOCHA = "mocha"
    VITEST = "vitest"
    JASMINE = "jasmine"
    AVA = "ava"

    # Java
    JUNIT = "junit"
    TESTNG = "testng"
    SPOCK = "spock"
    CUCUMBER = "cucumber"

    # Other
    PYTEST_PLUS = "pytest_plus"
    MOCHA_CHAI = "mocha_chai"
    UNKNOWN = "unknown"


# FIX HIGH #3: Backward compatibility alias
TestFrameworkType = FrameworkType


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class FrameworkDetection:
    """
    Single framework detection result.

    FIX HIGH #3: Renamed from TestFrameworkDetection to avoid pytest collection warnings.
    """

    framework_type: FrameworkType
    confidence: float
    evidence: List[str] = field(default_factory=list)
    version: Optional[str] = None


# FIX HIGH #3: Backward compatibility alias
TestFrameworkDetection = FrameworkDetection


@dataclass
class FrameworkDetectionResult:
    """
    Complete test framework detection result.

    FIX HIGH #3: Renamed from TestFrameworkDetectionResult to avoid pytest collection warnings.
    """

    primary_framework: Optional[FrameworkType]
    detected_frameworks: List[FrameworkDetection]
    overall_confidence: float
    test_directories: List[str] = field(default_factory=list)
    test_file_patterns: List[str] = field(default_factory=list)
    configuration_files: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: int = 1


# FIX HIGH #3: Backward compatibility alias
TestFrameworkDetectionResult = FrameworkDetectionResult


# ============================================================================
# FrameworkDetector Class (FIX HIGH #3: renamed from TestFrameworkDetector)
# ============================================================================


class FrameworkDetector:
    """
    Detects test frameworks used in a project.

    FIX HIGH #3: Renamed from TestFrameworkDetector to avoid pytest collection warnings.

    Supports Python, JavaScript/TypeScript, and Java projects.
    Uses multiple detection methods: config files, dependencies, imports, patterns.

    Attributes:
        project_root: Root directory of the project
        timeout_sec: Timeout for detection (default 1.5)
    """

    DEFAULT_TIMEOUT_SEC = 1.5

    # Python framework configuration files
    PYTHON_CONFIG_FILES = {
        TestFrameworkType.PYTEST: ["pytest.ini", "conftest.py", "pyproject.toml"],
        TestFrameworkType.NOSE: [".noserc", "setup.cfg"],
        TestFrameworkType.UNITTEST: [],  # No standard config file
        TestFrameworkType.HYPOTHESIS: [],  # FIX MEDIUM #7: No standard config file, used with pytest
    }

    # JavaScript framework configuration files
    JS_CONFIG_FILES = {
        TestFrameworkType.JEST: ["jest.config.js", "jest.config.ts", "jest.config.json"],
        TestFrameworkType.MOCHA: [".mocharc.js", ".mocharc.json", ".mocharc.yaml"],
        TestFrameworkType.VITEST: ["vite.config.ts", "vite.config.js"],
    }

    # Test directory patterns
    TEST_DIR_PATTERNS = [
        "test",
        "tests",
        "__tests__",
        "spec",
        "specs",
        "src/test",
        "src/tests",
        "src/__tests__",
        "testing",
    ]

    # Test file patterns by language
    TEST_FILE_PATTERNS = {
        ProjectLanguage.PYTHON: [
            "test_*.py",
            "*_test.py",
        ],
        ProjectLanguage.NODEJS: [
            "*.test.js",
            "*.test.ts",
            "*.test.jsx",
            "*.test.tsx",
            "*.spec.js",
            "*.spec.ts",
            "*.spec.jsx",
            "*.spec.tsx",
        ],
        ProjectLanguage.JAVA: [
            "*Test.java",
            "*Tests.java",
        ],
    }

    def __init__(
        self,
        project_root: Path,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        performance_tracker: Optional[PerformanceTracker] = None,  # FIX CRITICAL #1
        file_access_handler: Optional[FileAccessHandler] = None,  # FIX CRITICAL #2
    ):
        """
        Initialize test framework detector.

        Args:
            project_root: Root directory to analyze
            timeout_sec: Timeout for detection (default 1.5 seconds)
            performance_tracker: Optional PerformanceTracker from Story 1.4 (FIX CRITICAL #1)
            file_access_handler: Optional FileAccessHandler from Story 2.10 (FIX CRITICAL #2)
        """
        self.project_root = Path(project_root)
        self.timeout_sec = timeout_sec
        self.start_time = time.perf_counter()
        self.performance_tracker = performance_tracker  # FIX CRITICAL #1
        self.file_access_handler = file_access_handler or FileAccessHandler(str(project_root))  # FIX CRITICAL #2

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def detect_test_framework(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
    ) -> Optional[TestFrameworkDetectionResult]:
        """
        Detect test framework used in project.

        Args:
            tech_result: Tech stack detection result (Story 2.1)
            files_result: Project indicator result (Story 2.2)

        Returns:
            TestFrameworkDetectionResult with detected frameworks, or None on failure
        """
        try:
            if self._is_timeout():
                logger.warning("Test framework detection timeout")
                return None

            # Detect based on language
            detected_frameworks: List[TestFrameworkDetection] = []
            config_files: List[str] = []
            test_dirs: List[str] = []
            test_patterns: Set[str] = set()

            language = tech_result.primary_language

            if language == ProjectLanguage.PYTHON:
                detected_frameworks = self._detect_python_frameworks(files_result)
            elif language == ProjectLanguage.NODEJS:
                detected_frameworks = self._detect_javascript_frameworks(files_result)
            elif language == ProjectLanguage.JAVA:
                detected_frameworks = self._detect_java_frameworks(files_result)
            else:
                # Generic detection
                detected_frameworks = self._detect_generic_frameworks(files_result)

            # Find test directories and patterns
            test_dirs = self._find_test_directories(files_result)
            test_patterns_list = self._find_test_patterns(files_result, language)
            test_patterns.update(test_patterns_list)

            # Find configuration files
            config_files = self._find_config_files(files_result)

            # Determine primary framework
            primary_framework = None
            overall_confidence = 0.0

            if detected_frameworks:
                # Sort by confidence
                sorted_frameworks = sorted(detected_frameworks, key=lambda f: f.confidence, reverse=True)
                primary_framework = sorted_frameworks[0].framework_type
                overall_confidence = sorted_frameworks[0].confidence

            return TestFrameworkDetectionResult(
                primary_framework=primary_framework,
                detected_frameworks=detected_frameworks,
                overall_confidence=overall_confidence,
                test_directories=test_dirs,
                test_file_patterns=list(test_patterns),
                configuration_files=config_files,
            )

        except Exception as e:
            logger.error(f"Error detecting test framework: {e}", exc_info=True)
            return None

    # ========================================================================
    # Python Framework Detection
    # ========================================================================

    def _detect_python_frameworks(
        self,
        files_result: ProjectIndicatorResult,
    ) -> List[TestFrameworkDetection]:
        """Detect Python test frameworks."""
        frameworks: List[TestFrameworkDetection] = []

        # Check for pytest
        if self._has_pytest_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.PYTEST,
                    confidence=self._calculate_framework_confidence(
                        has_config=self._has_config_file(files_result, TestFrameworkType.PYTEST),
                        has_dependency=self._has_dependency(files_result, "pytest"),
                        has_imports=self._has_import_pattern(files_result, "pytest"),
                        has_test_files=self._has_test_file_patterns(files_result),  # FIX MEDIUM #8
                    ),
                    evidence=self._get_pytest_evidence(files_result),
                )
            )

        # Check for unittest
        if self._has_unittest_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.UNITTEST,
                    confidence=self._calculate_framework_confidence(
                        has_imports=self._has_import_pattern(files_result, "unittest"),
                        has_test_files=self._has_test_file_patterns(files_result),  # FIX MEDIUM #8
                    ),
                    evidence=self._get_unittest_evidence(files_result),
                )
            )

        # Check for nose
        if self._has_nose_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.NOSE,
                    confidence=self._calculate_framework_confidence(
                        has_config=self._has_config_file(files_result, TestFrameworkType.NOSE),
                        has_dependency=self._has_dependency(files_result, "nose"),
                        has_test_files=self._has_test_file_patterns(files_result),  # FIX MEDIUM #8
                    ),
                    evidence=self._get_nose_evidence(files_result),
                )
            )

        # FIX MEDIUM #7: Check for hypothesis (property-based testing library)
        if self._has_hypothesis_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.HYPOTHESIS,
                    confidence=self._calculate_framework_confidence(
                        has_dependency=self._has_dependency(files_result, "hypothesis"),
                        has_imports=self._has_import_pattern(files_result, "hypothesis"),
                        has_test_files=self._has_test_file_patterns(files_result),  # FIX MEDIUM #8
                    ),
                    evidence=self._get_hypothesis_evidence(files_result),
                )
            )

        return frameworks

    def _has_pytest_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for pytest indicators."""
        return (
            self._has_config_file(files_result, TestFrameworkType.PYTEST)
            or self._has_dependency(files_result, "pytest")
            or self._has_import_pattern(files_result, "pytest")
        )

    def _has_unittest_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for unittest indicators."""
        return self._has_import_pattern(files_result, "unittest")

    def _has_nose_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for nose indicators."""
        return (
            self._has_config_file(files_result, TestFrameworkType.NOSE)
            or self._has_dependency(files_result, "nose")
        )

    def _get_pytest_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for pytest detection."""
        evidence = []
        if self._has_config_file(files_result, TestFrameworkType.PYTEST):
            evidence.append("pytest configuration file found")
        if self._has_dependency(files_result, "pytest"):
            evidence.append("pytest in dependencies")
        if self._has_import_pattern(files_result, "pytest"):
            evidence.append("pytest imports in test files")
        return evidence

    def _get_unittest_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for unittest detection."""
        evidence = []
        if self._has_import_pattern(files_result, "unittest"):
            evidence.append("unittest imports in test files")
        return evidence

    def _get_nose_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for nose detection."""
        evidence = []
        if self._has_config_file(files_result, TestFrameworkType.NOSE):
            evidence.append("nose configuration file found")
        if self._has_dependency(files_result, "nose"):
            evidence.append("nose in dependencies")
        return evidence

    def _has_hypothesis_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """
        Check for hypothesis indicators.

        FIX MEDIUM #7: Hypothesis is a property-based testing library often used with pytest.
        """
        return (
            self._has_dependency(files_result, "hypothesis")
            or self._has_import_pattern(files_result, "hypothesis")
        )

    def _get_hypothesis_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """
        Get evidence for hypothesis detection.

        FIX MEDIUM #7: Added hypothesis framework detection.
        """
        evidence = []
        if self._has_dependency(files_result, "hypothesis"):
            evidence.append("hypothesis in dependencies")
        if self._has_import_pattern(files_result, "hypothesis"):
            evidence.append("hypothesis imports in test files")
        return evidence

    # ========================================================================
    # JavaScript Framework Detection
    # ========================================================================

    def _detect_javascript_frameworks(
        self,
        files_result: ProjectIndicatorResult,
    ) -> List[TestFrameworkDetection]:
        """Detect JavaScript test frameworks."""
        frameworks: List[TestFrameworkDetection] = []

        # Check for jest
        if self._has_jest_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.JEST,
                    confidence=self._calculate_framework_confidence(
                        has_config=self._has_config_file(files_result, TestFrameworkType.JEST),
                        has_dependency=self._has_dependency(files_result, "jest"),
                    ),
                    evidence=self._get_jest_evidence(files_result),
                )
            )

        # Check for mocha
        if self._has_mocha_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.MOCHA,
                    confidence=self._calculate_framework_confidence(
                        has_config=self._has_config_file(files_result, TestFrameworkType.MOCHA),
                        has_dependency=self._has_dependency(files_result, "mocha"),
                    ),
                    evidence=self._get_mocha_evidence(files_result),
                )
            )

        # Check for vitest
        if self._has_vitest_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.VITEST,
                    confidence=self._calculate_framework_confidence(
                        has_dependency=self._has_dependency(files_result, "vitest"),
                    ),
                    evidence=self._get_vitest_evidence(files_result),
                )
            )

        return frameworks

    def _has_jest_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for jest indicators."""
        return (
            self._has_config_file(files_result, TestFrameworkType.JEST)
            or self._has_dependency(files_result, "jest")
        )

    def _has_mocha_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for mocha indicators."""
        return (
            self._has_config_file(files_result, TestFrameworkType.MOCHA)
            or self._has_dependency(files_result, "mocha")
        )

    def _has_vitest_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for vitest indicators."""
        return self._has_dependency(files_result, "vitest")

    def _get_jest_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for jest detection."""
        evidence = []
        if self._has_config_file(files_result, TestFrameworkType.JEST):
            evidence.append("jest configuration file found")
        if self._has_dependency(files_result, "jest"):
            evidence.append("jest in dependencies")
        return evidence

    def _get_mocha_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for mocha detection."""
        evidence = []
        if self._has_config_file(files_result, TestFrameworkType.MOCHA):
            evidence.append("mocha configuration file found")
        if self._has_dependency(files_result, "mocha"):
            evidence.append("mocha in dependencies")
        return evidence

    def _get_vitest_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for vitest detection."""
        evidence = []
        if self._has_dependency(files_result, "vitest"):
            evidence.append("vitest in dependencies")
        return evidence

    # ========================================================================
    # Java Framework Detection
    # ========================================================================

    def _detect_java_frameworks(
        self,
        files_result: ProjectIndicatorResult,
    ) -> List[TestFrameworkDetection]:
        """Detect Java test frameworks."""
        frameworks: List[TestFrameworkDetection] = []

        # Check for junit
        if self._has_junit_indicators(files_result):
            # FIX HIGH #4: Extract JUnit version (4 vs 5)
            junit_version = self._extract_junit_version(files_result)
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.JUNIT,
                    confidence=self._calculate_framework_confidence(
                        has_dependency=self._has_dependency(files_result, "junit"),
                    ),
                    evidence=self._get_junit_evidence(files_result),
                    version=junit_version,  # FIX HIGH #4
                )
            )

        # Check for testng
        if self._has_testng_indicators(files_result):
            frameworks.append(
                TestFrameworkDetection(
                    framework_type=TestFrameworkType.TESTNG,
                    confidence=self._calculate_framework_confidence(
                        has_dependency=self._has_dependency(files_result, "testng"),
                    ),
                    evidence=self._get_testng_evidence(files_result),
                )
            )

        return frameworks

    def _has_junit_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for junit indicators."""
        return self._has_dependency(files_result, "junit")

    def _has_testng_indicators(self, files_result: ProjectIndicatorResult) -> bool:
        """Check for testng indicators."""
        return self._has_dependency(files_result, "testng")

    def _get_junit_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for junit detection."""
        evidence = []
        if self._has_dependency(files_result, "junit"):
            evidence.append("junit in dependencies")
        return evidence

    def _get_testng_evidence(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Get evidence for testng detection."""
        evidence = []
        if self._has_dependency(files_result, "testng"):
            evidence.append("testng in dependencies")
        return evidence

    def _extract_junit_version(self, files_result: ProjectIndicatorResult) -> Optional[str]:
        """
        Extract JUnit version from dependencies.

        FIX HIGH #4: Implements AC3 requirement to distinguish between JUnit 4 and 5.

        Args:
            files_result: Project indicator result with dependencies

        Returns:
            Version string ("4", "5", or None if cannot determine)
        """
        if not files_result.metadata:
            return None

        all_deps = (files_result.metadata.dependencies or []) + (files_result.metadata.dev_dependencies or [])

        for dep in all_deps:
            dep_str = str(dep).lower()

            # JUnit 5 detection (org.junit.jupiter)
            if "org.junit.jupiter" in dep_str or "junit-jupiter" in dep_str:
                # Try to extract version number
                version_match = re.search(r'[:\s]5\.(\d+)', dep_str)
                if version_match:
                    return f"5.{version_match.group(1)}"
                return "5"

            # JUnit 4 detection (junit:junit)
            if "junit:junit" in dep_str or re.search(r'\bjunit\b.*4\.', dep_str):
                version_match = re.search(r'[:\s]4\.(\d+)', dep_str)
                if version_match:
                    return f"4.{version_match.group(1)}"
                return "4"

        return None

    # ========================================================================
    # Generic Framework Detection
    # ========================================================================

    def _detect_generic_frameworks(
        self,
        files_result: ProjectIndicatorResult,
    ) -> List[TestFrameworkDetection]:
        """Generic framework detection for unsupported languages."""
        frameworks: List[TestFrameworkDetection] = []

        # Check common frameworks regardless of language
        for framework_name in ["pytest", "jest", "unittest", "mocha"]:
            if self._has_dependency(files_result, framework_name):
                try:
                    fw_type = TestFrameworkType(framework_name)
                    frameworks.append(
                        TestFrameworkDetection(
                            framework_type=fw_type,
                            confidence=0.6,
                            evidence=[f"{framework_name} in dependencies"],
                        )
                    )
                except ValueError:
                    pass

        return frameworks

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _has_config_file(
        self,
        files_result: ProjectIndicatorResult,
        framework: TestFrameworkType,
    ) -> bool:
        """Check if framework has configuration file."""
        if not files_result.files_found:
            return False

        config_patterns = self.PYTHON_CONFIG_FILES.get(framework) or self.JS_CONFIG_FILES.get(framework)
        if not config_patterns:
            return False

        files_set = {str(f).lower() for f in files_result.files_found}

        for pattern in config_patterns:
            if pattern.lower() in files_set:
                return True

        return False

    def _has_dependency(self, files_result: ProjectIndicatorResult, dep_name: str) -> bool:
        """Check if project has a dependency."""
        if not files_result.metadata:
            return False

        all_deps = (files_result.metadata.dependencies or []) + (files_result.metadata.dev_dependencies or [])

        return any(dep_name.lower() in str(d).lower() for d in all_deps)

    def _has_test_file_patterns(self, files_result: ProjectIndicatorResult) -> bool:
        """
        Check if project contains test files matching standard patterns.

        FIX MEDIUM #8: Helper method to determine has_test_files parameter value.
        """
        if not files_result.files_found:
            return False

        # Check if any files match test file patterns
        return any("test" in str(f).lower() for f in files_result.files_found)

    def _has_import_pattern(self, files_result: ProjectIndicatorResult, module_name: str) -> bool:
        """
        Check if test files contain import pattern.

        FIX CRITICAL #2: Uses FileAccessHandler for safe file access.
        FIX HIGH #5: Added timeout check in loop.
        FIX MEDIUM #6: Limited to first 10 test files for performance.

        Note: This method checks only the first 10 test files to balance accuracy
        with performance. For most projects, this provides sufficient evidence while
        avoiding excessive file I/O in large test suites.
        """
        if not files_result.files_found:
            return False

        test_files = [f for f in files_result.files_found if "test" in str(f).lower()]

        for test_file in test_files[:10]:  # Check first 10 test files
            # FIX HIGH #5: Check timeout in loop
            if self._is_timeout():
                logger.warning("Timeout during import pattern check")
                break

            try:
                full_path = str(self.project_root / test_file)

                # FIX CRITICAL #2: Use FileAccessHandler instead of direct read
                content = self.file_access_handler.try_read_file(full_path)

                if content:
                    # Look for import pattern
                    if re.search(rf"import\s+{module_name}|from\s+{module_name}", content):
                        return True
            except Exception as e:
                logger.debug(f"Error checking imports in {test_file}: {e}")
                continue

        return False

    def _find_test_directories(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Find test directories in project."""
        directories = set()

        if not files_result.files_found:
            return []

        for file_path in files_result.files_found:
            path_str = str(file_path).lower()

            for pattern in self.TEST_DIR_PATTERNS:
                if f"/{pattern}/" in path_str or path_str.startswith(f"{pattern}/"):
                    directories.add(pattern)

        return sorted(list(directories))

    def _find_test_patterns(
        self,
        files_result: ProjectIndicatorResult,
        language: ProjectLanguage,
    ) -> List[str]:
        """Find test file naming patterns."""
        patterns = set()

        if not files_result.files_found:
            return []

        test_file_patterns = self.TEST_FILE_PATTERNS.get(language, [])

        for file_path in files_result.files_found:
            file_name = str(file_path).lower()

            for pattern in test_file_patterns:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
                if re.search(regex_pattern, file_name):
                    patterns.add(pattern)

        return sorted(list(patterns))

    def _find_config_files(self, files_result: ProjectIndicatorResult) -> List[str]:
        """Find test framework configuration files."""
        config_files = []

        if not files_result.files_found:
            return []

        # Flatten all config patterns
        all_patterns = set()
        for patterns_list in self.PYTHON_CONFIG_FILES.values():
            all_patterns.update(patterns_list)
        for patterns_list in self.JS_CONFIG_FILES.values():
            all_patterns.update(patterns_list)

        files_set = {str(f).lower() for f in files_result.files_found}

        for pattern in all_patterns:
            if pattern.lower() in files_set:
                config_files.append(pattern)

        return config_files

    def _calculate_framework_confidence(
        self,
        has_config: bool = False,
        has_dependency: bool = False,
        has_imports: bool = False,
        has_test_files: bool = False,
    ) -> float:
        """Calculate confidence score based on evidence."""
        score = 0.0

        if has_config:
            score += 0.35
        if has_dependency:
            score += 0.35
        if has_imports:
            score += 0.20
        if has_test_files:
            score += 0.10

        return min(score, 1.0)

    def _is_timeout(self) -> bool:
        """Check if timeout has been exceeded."""
        elapsed = time.perf_counter() - self.start_time
        return elapsed > self.timeout_sec


# ============================================================================
# Backward Compatibility Aliases (FIX HIGH #3)
# ============================================================================
# These aliases prevent breaking changes for existing code that imports
# the old class names. The classes were renamed to avoid pytest collection warnings.

TestFrameworkDetector = FrameworkDetector
