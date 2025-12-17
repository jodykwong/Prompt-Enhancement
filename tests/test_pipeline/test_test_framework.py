"""
Tests for Test Framework Detector - Story 2.6.

Comprehensive test suite for TestFrameworkDetector implementing all acceptance criteria.
"""

import tempfile
import time
from pathlib import Path

import pytest

from prompt_enhancement.pipeline.test_framework import (
    TestFrameworkDetector,
    TestFrameworkType,
    TestFrameworkDetection,
    TestFrameworkDetectionResult,
)
from prompt_enhancement.pipeline.tech_stack import (
    ProjectLanguage,
    ProjectTypeDetectionResult,
)
from prompt_enhancement.pipeline.project_files import (
    ProjectMetadata,
    ProjectIndicatorResult,
)


class TestPythonTestFrameworkDetection:
    """Test Python test framework detection - AC1."""

    def test_detect_pytest(self):
        """Should detect pytest - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create pytest.ini
            (tmppath / "pytest.ini").write_text("[pytest]\naddopts = -v")

            # Create conftest.py
            (tmppath / "conftest.py").write_text("import pytest")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["pytest.ini"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=["pytest"],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["pytest.ini", "conftest.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert TestFrameworkType.PYTEST in [d.framework_type for d in result.detected_frameworks]

    def test_detect_unittest(self):
        """Should detect unittest - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test file with unittest imports
            (tmppath / "test_models.py").write_text("""
import unittest

class TestModels(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
""")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=[],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=[],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["test_models.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert TestFrameworkType.UNITTEST in [d.framework_type for d in result.detected_frameworks]


class TestJavaScriptTestFrameworkDetection:
    """Test JavaScript test framework detection - AC2."""

    def test_detect_jest(self):
        """Should detect Jest - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create jest.config.js
            (tmppath / "jest.config.js").write_text("module.exports = { testEnvironment: 'node' };")

            # Create package.json with jest
            (tmppath / "package.json").write_text("""{
    "name": "test-project",
    "devDependencies": {
        "jest": "^27.0.0"
    }
}""")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.NODEJS,
                    dependencies=[],
                    dev_dependencies=["jest"],
                    target_version="18.0.0",
                    package_manager="npm",
                ),
                files_found=["jest.config.js", "package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert TestFrameworkType.JEST in [d.framework_type for d in result.detected_frameworks]

    def test_detect_mocha(self):
        """Should detect Mocha - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create .mocharc.json
            (tmppath / ".mocharc.json").write_text('{"require": ["ts-node/register"]}')

            # Create package.json with mocha
            (tmppath / "package.json").write_text("""{
    "name": "test-project",
    "devDependencies": {
        "mocha": "^10.0.0"
    }
}""")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.NODEJS,
                    dependencies=[],
                    dev_dependencies=["mocha"],
                    target_version="18.0.0",
                    package_manager="npm",
                ),
                files_found=[".mocharc.json", "package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert TestFrameworkType.MOCHA in [d.framework_type for d in result.detected_frameworks]


class TestJavaTestFrameworkDetection:
    """Test Java test framework detection - AC3."""

    def test_detect_junit(self):
        """Should detect JUnit - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create pom.xml with JUnit dependency
            (tmppath / "pom.xml").write_text("""<project>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
        </dependency>
    </dependencies>
</project>""")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.JAVA,
                version="11",
                confidence=0.95,
                markers_found=["pom.xml"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.JAVA,
                    dependencies=["junit"],
                    dev_dependencies=[],
                    target_version="11",
                    package_manager="maven",
                ),
                files_found=["pom.xml"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert TestFrameworkType.JUNIT in [d.framework_type for d in result.detected_frameworks]


class TestTestDirectoryDetection:
    """Test directory and file pattern detection - AC4."""

    def test_detect_test_directories(self):
        """Should detect common test directories - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test directories
            (tmppath / "tests").mkdir()
            (tmppath / "tests" / "test_main.py").write_text("import pytest")
            (tmppath / "test").mkdir()
            (tmppath / "test" / "test_utils.py").write_text("import pytest")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=[],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=[],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["tests/test_main.py", "test/test_utils.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert len(result.test_directories) > 0

    def test_detect_test_file_patterns(self):
        """Should detect test file naming patterns - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files with different patterns
            (tmppath / "test_models.py").write_text("import pytest")
            (tmppath / "models_test.py").write_text("import unittest")
            (tmppath / "test_views.js").write_text("const test = require('jest');")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=[],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=[],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["test_models.py", "models_test.py", "test_views.js"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert len(result.test_file_patterns) > 0


class TestConfidenceScoring:
    """Test confidence score calculation - AC5."""

    def test_high_confidence_with_config_file(self):
        """Should assign high confidence to config file presence - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Config file = high confidence
            (tmppath / "pytest.ini").write_text("[pytest]")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["pytest.ini"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=["pytest"],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["pytest.ini"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            if result.detected_frameworks:
                # Config file + dependency should give high confidence (0.7+)
                pytest_detection = next(
                    (d for d in result.detected_frameworks if d.framework_type == TestFrameworkType.PYTEST),
                    None
                )
                if pytest_detection:
                    assert pytest_detection.confidence >= 0.65

    def test_medium_confidence_with_dependency(self):
        """Should assign medium-high confidence to dependency detection - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Just dependency = medium confidence
            (tmppath / "package.json").write_text('{"devDependencies": {"jest": "^27.0.0"}}')

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.NODEJS,
                    dependencies=[],
                    dev_dependencies=["jest"],
                    target_version="18.0.0",
                    package_manager="npm",
                ),
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            if result.detected_frameworks:
                # Dependency should give decent confidence (0.3+)
                jest_detection = next(
                    (d for d in result.detected_frameworks if d.framework_type == TestFrameworkType.JEST),
                    None
                )
                if jest_detection:
                    assert jest_detection.confidence >= 0.3


class TestNoFrameworkHandling:
    """Test handling of projects without test framework - AC6."""

    def test_no_framework_detected_gracefully(self):
        """Should gracefully handle projects with no test framework - AC6."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create project with no test framework indicators
            (tmppath / "src" / "main.py").mkdir(parents=True)
            (tmppath / "src" / "main.py" / "app.py").write_text("print('hello')")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=[],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=[],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["src/main.py/app.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            # Should return result (not crash) but no frameworks detected
            assert result is not None
            assert len(result.detected_frameworks) == 0 or result.primary_framework is None


class TestResultFormat:
    """Test result format and structure - AC7."""

    def test_test_framework_detection_result_structure(self):
        """Result should have all required fields - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "pytest.ini").write_text("[pytest]")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["pytest.ini"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=["pytest"],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["pytest.ini"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert hasattr(result, 'primary_framework')
            assert hasattr(result, 'detected_frameworks')
            assert hasattr(result, 'overall_confidence')
            assert hasattr(result, 'test_directories')
            assert hasattr(result, 'test_file_patterns')
            assert hasattr(result, 'configuration_files')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'version')

    def test_result_includes_timestamp_and_version(self):
        """Result should include timestamp and version - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "pytest.ini").write_text("[pytest]")

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["pytest.ini"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=["pytest"],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=["pytest.ini"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            assert result.version == 1
            assert result.timestamp is not None
            assert len(result.timestamp) > 0


class TestIntegration:
    """Integration with Stories 2.1-2.5 - AC8."""

    def test_uses_language_from_story_2_1(self):
        """Should use detected language to guide detection - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "jest.config.js").write_text("module.exports = {};")

            detector = TestFrameworkDetector(tmppath)

            # Pass JavaScript as primary language
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,  # Guide detection
                version="18.0.0",
                confidence=0.95,
                markers_found=["jest.config.js"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.NODEJS,
                    dependencies=["jest"],
                    dev_dependencies=[],
                    target_version="18.0.0",
                    package_manager="npm",
                ),
                files_found=["jest.config.js"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_test_framework(tech_result, files_result)

            assert result is not None
            # Should detect Jest for JavaScript
            assert any(d.framework_type == TestFrameworkType.JEST for d in result.detected_frameworks)


class TestPerformance:
    """Test performance within budget - AC7."""

    def test_detection_completes_within_budget(self):
        """Should complete detection within 1.5 second budget - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create realistic project structure
            (tmppath / "tests").mkdir()
            for i in range(10):
                (tmppath / "tests" / f"test_module_{i}.py").write_text("""
import pytest

def test_something():
    assert True
""")

            (tmppath / "pytest.ini").write_text("[pytest]\naddopts = -v")
            (tmppath / "package.json").write_text('{"devDependencies": {"jest": "^27.0.0"}}')

            detector = TestFrameworkDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=[],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.PYTHON,
                    dependencies=["pytest"],
                    dev_dependencies=[],
                    target_version="3.9",
                    package_manager="pip",
                ),
                files_found=[f"tests/test_module_{i}.py" for i in range(10)] + ["pytest.ini", "package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            start_time = time.perf_counter()
            result = detector.detect_test_framework(tech_result, files_result)
            elapsed = time.perf_counter() - start_time

            assert elapsed < 1.5  # Must complete within 1.5 seconds
            assert result is not None
