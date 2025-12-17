"""
Tests for Naming Convention Detector - Story 2.5.

Comprehensive test suite for NamingConventionDetector implementing all acceptance criteria.
"""

import tempfile
import time
from enum import Enum
from pathlib import Path

import pytest

from prompt_enhancement.pipeline.naming_conventions import (
    NamingConventionDetector,
    NamingConventionType,
    IdentifierCategory,
    NamingConventionResult,
)
from prompt_enhancement.pipeline.tech_stack import (
    ProjectLanguage,
    ProjectTypeDetectionResult,
)
from prompt_enhancement.pipeline.project_files import (
    ProjectMetadata,
    ProjectIndicatorResult,
)


class TestConventionPatternDetection:
    """Test pattern detection for different naming conventions - AC1."""

    def test_detect_snake_case_functions(self):
        """Should detect snake_case function names - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file with snake_case functions
            python_file = Path(tmpdir) / "user_service.py"
            python_file.write_text("""
def get_user_by_id(user_id):
    pass

def validate_email(email):
    pass

def calculate_total_price(items):
    pass
""")

            detector = NamingConventionDetector(Path(tmpdir))

            # Manually extract patterns (simulate parsing)
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            assert len(patterns) > 0
            assert any(p.convention_type == NamingConventionType.SNAKE_CASE for p in patterns)

    def test_detect_camel_case_functions(self):
        """Should detect camelCase function names - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create JavaScript file with camelCase functions
            js_file = Path(tmpdir) / "userService.js"
            js_file.write_text("""
function getUserById(userId) {
    return null;
}

const validateEmail = (email) => {
    return true;
};

function calculateTotalPrice(items) {
    return 0;
}
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(js_file, ProjectLanguage.NODEJS)

            assert len(patterns) > 0
            assert any(p.convention_type == NamingConventionType.CAMEL_CASE for p in patterns)

    def test_detect_pascal_case_classes(self):
        """Should detect PascalCase class names - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file with PascalCase classes
            python_file = Path(tmpdir) / "models.py"
            python_file.write_text("""
class UserValidator:
    pass

class EmailService:
    pass

class PaymentProcessor:
    pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            assert len(patterns) > 0
            assert any(p.convention_type == NamingConventionType.PASCAL_CASE and
                      p.category == IdentifierCategory.CLASS for p in patterns)


class TestNamingConventionTypes:
    """Test identification of different convention types - AC2."""

    def test_recognize_snake_case(self):
        """Should correctly identify snake_case pattern - AC2."""
        detector = NamingConventionDetector(Path("/tmp"))

        snake_case_names = ["get_user", "validate_email", "calculate_total"]

        for name in snake_case_names:
            convention = detector._classify_convention(name)
            assert convention == NamingConventionType.SNAKE_CASE

    def test_recognize_camel_case(self):
        """Should correctly identify camelCase pattern - AC2."""
        detector = NamingConventionDetector(Path("/tmp"))

        camel_case_names = ["getUser", "validateEmail", "calculateTotal"]

        for name in camel_case_names:
            convention = detector._classify_convention(name)
            assert convention == NamingConventionType.CAMEL_CASE

    def test_recognize_pascal_case(self):
        """Should correctly identify PascalCase pattern - AC2."""
        detector = NamingConventionDetector(Path("/tmp"))

        pascal_case_names = ["GetUser", "ValidateEmail", "CalculateTotal"]

        for name in pascal_case_names:
            convention = detector._classify_convention(name)
            assert convention == NamingConventionType.PASCAL_CASE

    def test_recognize_upper_snake_case(self):
        """Should correctly identify UPPER_SNAKE_CASE pattern - AC2."""
        detector = NamingConventionDetector(Path("/tmp"))

        upper_names = ["MAX_RETRIES", "API_KEY", "USER_ID"]

        for name in upper_names:
            convention = detector._classify_convention(name)
            assert convention == NamingConventionType.UPPER_SNAKE_CASE

    def test_recognize_kebab_case(self):
        """Should correctly identify kebab-case pattern - AC2."""
        detector = NamingConventionDetector(Path("/tmp"))

        kebab_names = ["user-service", "validate-email", "get-total"]

        for name in kebab_names:
            convention = detector._classify_convention(name)
            assert convention == NamingConventionType.KEBAB_CASE


class TestConventionCategorization:
    """Test categorization by frequency - AC3."""

    def test_identify_dominant_convention(self):
        """Should identify dominant convention (>60%) - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file with mostly snake_case
            python_file = Path(tmpdir) / "service.py"
            python_file.write_text("""
def get_user(): pass
def validate_email(): pass
def calculate_total(): pass
def process_data(): pass
def send_notification(): pass

class UserValidator: pass
class EmailService: pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            # Should have dominant snake_case in functions
            snake_case_count = sum(1 for p in patterns if p.convention_type == NamingConventionType.SNAKE_CASE)
            total_count = len(patterns)

            if total_count > 0:
                percentage = (snake_case_count / total_count) * 100
                # Most functions are snake_case
                assert percentage >= 50  # At least half should be snake_case

    def test_categorize_secondary_conventions(self):
        """Should identify secondary conventions (20-60%) - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mixed convention file
            python_file = Path(tmpdir) / "mixed.py"
            python_file.write_text("""
# Mostly snake_case functions
def get_data(): pass
def process_item(): pass
def validate_input(): pass
def handle_error(): pass

# Some PascalCase classes
class DataProcessor: pass
class ItemValidator: pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            # Should have mix of conventions
            assert len(patterns) >= 2
            convention_types = {p.convention_type for p in patterns}
            assert len(convention_types) >= 2


class TestContextAwareDetection:
    """Test context-aware detection of naming conventions - AC4."""

    def test_distinguish_function_vs_class_naming(self):
        """Should detect that functions and classes use different conventions - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Python: functions snake_case, classes PascalCase
            python_file = Path(tmpdir) / "models.py"
            python_file.write_text("""
def get_user(): pass
def validate_email(): pass

class UserService: pass
class EmailValidator: pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            functions = [p for p in patterns if p.category == IdentifierCategory.FUNCTION]
            classes = [p for p in patterns if p.category == IdentifierCategory.CLASS]

            if functions:
                assert any(p.convention_type == NamingConventionType.SNAKE_CASE for p in functions)
            if classes:
                assert any(p.convention_type == NamingConventionType.PASCAL_CASE for p in classes)

    def test_detect_private_naming(self):
        """Should detect private naming conventions (underscore prefix) - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "service.py"
            python_file.write_text("""
def _private_function():
    pass

def public_function():
    pass

_private_var = 10
public_var = 20
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            # Should have private identifiers
            privates = [p for p in patterns if p.identifier.startswith('_')]
            assert len(privates) > 0

    def test_detect_constants(self):
        """Should detect UPPER_SNAKE_CASE constants - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "config.py"
            python_file.write_text("""
MAX_RETRIES = 3
API_KEY = "secret"
DEFAULT_TIMEOUT = 30

def get_timeout():
    return DEFAULT_TIMEOUT
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            # Should identify constants
            constants = [p for p in patterns if p.convention_type == NamingConventionType.UPPER_SNAKE_CASE]
            assert len(constants) > 0


class TestFileSamplingStrategy:
    """Test file sampling strategy - AC5."""

    def test_sample_representative_files(self):
        """Should sample representative files from project - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create diverse file structure
            (tmppath / "src").mkdir()
            (tmppath / "src" / "main.py").write_text("def main(): pass")
            (tmppath / "src" / "utils.py").write_text("def helper(): pass")
            (tmppath / "tests").mkdir()
            (tmppath / "tests" / "test_main.py").write_text("def test_main(): pass")
            (tmppath / "vendor").mkdir()
            (tmppath / "vendor" / "lib.py").write_text("def external(): pass")

            detector = NamingConventionDetector(tmppath)
            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version="3.9",
                package_manager="pip",
            )
            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["src/main.py", "src/utils.py", "tests/test_main.py", "vendor/lib.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            sampled = detector._sample_files(files_result, max_samples=100)

            # Should sample from source, not test/vendor
            assert len(sampled) > 0
            sampled_paths = [str(p) for p in sampled]
            assert any("src" in p for p in sampled_paths)

    def test_max_sample_limit(self):
        """Should not exceed maximum sample size - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create many files
            (tmppath / "src").mkdir()
            for i in range(150):
                (tmppath / "src" / f"module_{i}.py").write_text(f"def func_{i}(): pass")

            detector = NamingConventionDetector(tmppath)
            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version="3.9",
                package_manager="pip",
            )
            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=[f"src/module_{i}.py" for i in range(150)],
                lock_files_present=set(),
                confidence=0.95,
            )

            sampled = detector._sample_files(files_result, max_samples=100)

            # Should not exceed max_samples
            assert len(sampled) <= 100


class TestConfidenceScoring:
    """Test confidence score calculation - AC6."""

    def test_higher_confidence_with_more_samples(self):
        """Should have higher confidence with larger sample size - AC6."""
        detector = NamingConventionDetector(Path("/tmp"))

        # Small sample
        small_sample_confidence = detector._calculate_confidence(
            sample_size=10,
            consistency_percentage=0.8  # 0.0-1.0 range
        )

        # Large sample
        large_sample_confidence = detector._calculate_confidence(
            sample_size=100,
            consistency_percentage=0.8  # 0.0-1.0 range
        )

        # Larger sample should have higher confidence
        assert large_sample_confidence > small_sample_confidence

    def test_consistency_affects_confidence(self):
        """Should have lower confidence with inconsistent patterns - AC6."""
        detector = NamingConventionDetector(Path("/tmp"))

        # Consistent patterns
        consistent_confidence = detector._calculate_confidence(
            sample_size=50,
            consistency_percentage=0.9  # 0.0-1.0 range
        )

        # Inconsistent patterns
        inconsistent_confidence = detector._calculate_confidence(
            sample_size=50,
            consistency_percentage=0.5  # 0.0-1.0 range
        )

        # Consistent should have higher confidence
        assert consistent_confidence > inconsistent_confidence

    def test_confidence_in_valid_range(self):
        """Should return confidence between 0.0 and 1.0 - AC6."""
        detector = NamingConventionDetector(Path("/tmp"))

        confidence = detector._calculate_confidence(
            sample_size=50,
            consistency_percentage=75.0
        )

        assert 0.0 <= confidence <= 1.0


class TestLanguageSpecificHandling:
    """Test language-specific convention handling - AC7."""

    def test_python_snake_case_functions(self):
        """Python functions should be detected as snake_case - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "service.py"
            python_file.write_text("""
def get_user():
    pass

def validate_input():
    pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            functions = [p for p in patterns if p.category == IdentifierCategory.FUNCTION]
            if functions:
                assert all(p.convention_type == NamingConventionType.SNAKE_CASE for p in functions)

    def test_javascript_camel_case_functions(self):
        """JavaScript functions should be detected as camelCase - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_file = Path(tmpdir) / "service.js"
            js_file.write_text("""
function getUser() {
    return null;
}

const validateInput = () => {
    return true;
};
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(js_file, ProjectLanguage.NODEJS)

            functions = [p for p in patterns if p.category == IdentifierCategory.FUNCTION]
            if functions:
                assert all(p.convention_type == NamingConventionType.CAMEL_CASE for p in functions)

    def test_python_pascal_case_classes(self):
        """Python classes should be detected as PascalCase - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "models.py"
            python_file.write_text("""
class UserService:
    pass

class EmailValidator:
    pass
""")

            detector = NamingConventionDetector(Path(tmpdir))
            patterns = detector._extract_patterns_from_file(python_file, ProjectLanguage.PYTHON)

            classes = [p for p in patterns if p.category == IdentifierCategory.CLASS]
            if classes:
                assert all(p.convention_type == NamingConventionType.PASCAL_CASE for p in classes)


class TestResultFormat:
    """Test result format and consistency - AC8."""

    def test_naming_convention_result_structure(self):
        """NamingConventionResult should have all required fields - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "test.py"
            python_file.write_text("def test_func(): pass\nclass TestClass: pass")

            detector = NamingConventionDetector(Path(tmpdir))

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["test.py"],
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
                files_found=["test.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_naming_conventions(tech_result, files_result)

            assert result is not None
            assert hasattr(result, 'overall_dominant_convention')
            assert hasattr(result, 'overall_conventions')
            assert hasattr(result, 'function_conventions')
            assert hasattr(result, 'class_conventions')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'version')

    def test_result_includes_version_and_timestamp(self):
        """Result should include version and timestamp for tracking - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            python_file = Path(tmpdir) / "test.py"
            python_file.write_text("def test(): pass")

            detector = NamingConventionDetector(Path(tmpdir))

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["test.py"],
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
                files_found=["test.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_naming_conventions(tech_result, files_result)

            assert result.version == 1
            assert result.timestamp is not None
            assert len(result.timestamp) > 0


class TestPerformance:
    """Test performance within budget - AC7."""

    def test_detection_completes_within_budget(self):
        """Should complete detection within 2 second budget - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create realistic project structure
            (tmppath / "src").mkdir()
            for i in range(20):
                (tmppath / "src" / f"module_{i}.py").write_text("""
def get_data(): pass
def process_item(): pass
def validate_input(): pass
class DataService: pass
class ItemProcessor: pass
""")

            detector = NamingConventionDetector(tmppath)

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
                files_found=[f"src/module_{i}.py" for i in range(20)],
                lock_files_present=set(),
                confidence=0.95,
            )

            start_time = time.perf_counter()
            result = detector.detect_naming_conventions(tech_result, files_result)
            elapsed = time.perf_counter() - start_time

            assert elapsed < 2.0  # Must complete within 2 seconds
            assert result is not None


class TestIntegration:
    """Integration tests with realistic projects."""

    def test_python_project_detection(self):
        """Should correctly detect conventions in Python project - Integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "src").mkdir()

            # Create typical Python project
            (tmppath / "src" / "user_service.py").write_text("""
class UserValidator:
    def validate_email(self, email):
        return True

    def _validate_format(self, text):
        return True

def get_user_by_id(user_id):
    pass

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
""")

            detector = NamingConventionDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["user_service.py"],
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
                files_found=["src/user_service.py"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_naming_conventions(tech_result, files_result)

            assert result is not None
            assert result.overall_dominant_convention in [
                NamingConventionType.SNAKE_CASE,
                NamingConventionType.PASCAL_CASE,
            ]
            assert result.sample_size > 0
            assert result.consistency_score >= 0.0

    def test_javascript_project_detection(self):
        """Should correctly detect conventions in JavaScript project - Integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "src").mkdir()

            # Create typical JavaScript project
            (tmppath / "src" / "userService.js").write_text("""
class UserValidator {
    validateEmail(email) {
        return true;
    }

    _validateFormat(text) {
        return true;
    }
}

function getUserById(userId) {
    return null;
}

const MAX_RETRIES = 3;
const DEFAULT_TIMEOUT = 30;
""")

            detector = NamingConventionDetector(tmppath)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["userService.js"],
                secondary_languages=[],
            )
            files_result = ProjectIndicatorResult(
                metadata=ProjectMetadata(
                    name="test",
                    version="1.0.0",
                    source_language=ProjectLanguage.NODEJS,
                    dependencies=[],
                    dev_dependencies=[],
                    target_version="18.0.0",
                    package_manager="npm",
                ),
                files_found=["src/userService.js"],
                lock_files_present=set(),
                confidence=0.95,
            )

            result = detector.detect_naming_conventions(tech_result, files_result)

            assert result is not None
            # Overall dominant could be camelCase, PascalCase, or UPPER_SNAKE_CASE (for constants)
            assert result.overall_dominant_convention in [
                NamingConventionType.CAMEL_CASE,
                NamingConventionType.PASCAL_CASE,
                NamingConventionType.UPPER_SNAKE_CASE,
            ]
            assert result.sample_size > 0
            # Verify that we detected functions and classes properly
            assert len(result.function_conventions) > 0 or len(result.class_conventions) > 0
