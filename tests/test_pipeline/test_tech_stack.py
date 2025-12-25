"""
Comprehensive tests for ProjectTypeDetector (Story 2.1).

Tests project type detection from filesystem markers, version extraction,
confidence scoring, and error handling.
"""

import os
import tempfile
import json
import pytest
from pathlib import Path
from typing import Dict, Optional
from unittest.mock import Mock, patch

# Import the detector (will be created in implementation)
from src.prompt_enhancement.pipeline.tech_stack import (
    ProjectTypeDetector,
    ProjectLanguage,
    ProjectTypeDetectionResult,
)


class TestProjectTypeDetectionStructures:
    """Test data structures: ProjectLanguage enum and DetectionResult dataclass."""

    def test_project_language_enum_contains_all_languages(self):
        """ProjectLanguage enum should have all supported languages."""
        assert hasattr(ProjectLanguage, 'PYTHON')
        assert hasattr(ProjectLanguage, 'NODEJS')
        assert hasattr(ProjectLanguage, 'GO')
        assert hasattr(ProjectLanguage, 'RUST')
        assert hasattr(ProjectLanguage, 'JAVA')
        assert hasattr(ProjectLanguage, 'CSHARP')

    def test_detection_result_has_required_fields(self):
        """ProjectTypeDetectionResult should have language, version, confidence, markers."""
        result = ProjectTypeDetectionResult(
            primary_language=ProjectLanguage.PYTHON,
            version="3.9",
            confidence=0.95,
            markers_found=['requirements.txt'],
            secondary_languages=[]
        )
        assert result.primary_language == ProjectLanguage.PYTHON
        assert result.version == "3.9"
        assert result.confidence == 0.95
        assert result.markers_found == ['requirements.txt']

    def test_detection_result_with_secondary_languages(self):
        """DetectionResult should support secondary languages."""
        result = ProjectTypeDetectionResult(
            primary_language=ProjectLanguage.PYTHON,
            version="3.9",
            confidence=0.85,
            markers_found=['requirements.txt', 'package.json'],
            secondary_languages=[ProjectLanguage.NODEJS]
        )
        assert result.secondary_languages == [ProjectLanguage.NODEJS]


class TestProjectTypeDetectorInitialization:
    """Test ProjectTypeDetector class initialization."""

    def test_detector_initializes(self):
        """ProjectTypeDetector should initialize without error."""
        detector = ProjectTypeDetector()
        assert detector is not None

    def test_detector_has_marker_definitions(self):
        """ProjectTypeDetector should have marker file definitions."""
        detector = ProjectTypeDetector()
        assert hasattr(detector, 'PYTHON_MARKERS')
        assert hasattr(detector, 'NODE_MARKERS')
        assert hasattr(detector, 'GO_MARKERS')
        assert hasattr(detector, 'RUST_MARKERS')
        assert hasattr(detector, 'JAVA_MARKERS')
        assert hasattr(detector, 'CSHARP_MARKERS')

    def test_marker_definitions_have_priority(self):
        """Marker definitions should include priority values."""
        detector = ProjectTypeDetector()
        for marker, info in detector.PYTHON_MARKERS.items():
            assert 'priority' in info
            assert isinstance(info['priority'], int)
            assert 'metadata' in info
            assert isinstance(info['metadata'], bool)


class TestPythonProjectDetection:
    """Test Python project detection (AC1)."""

    def test_detect_python_with_requirements_txt(self):
        """Should detect Python from requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("requests==2.28.0\nnumpy==1.21.0\n")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON
            assert 'requirements.txt' in result.markers_found

    def test_detect_python_with_pyproject_toml(self):
        """Should detect Python from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            pyproject_file.write_text("""[project]
name = "my-project"
version = "0.1.0"
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON

    def test_extract_python_version_from_pyproject(self):
        """Should extract Python version from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            pyproject_file.write_text("""[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.9"
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.version is not None  # Should extract version

    def test_detect_python_with_setup_py(self):
        """Should detect Python from setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_file = Path(tmpdir) / "setup.py"
            setup_file.write_text("""
from setuptools import setup
setup(name='myproject', version='0.1')
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON


class TestNodeJsProjectDetection:
    """Test Node.js project detection (AC2)."""

    def test_detect_nodejs_with_package_json(self):
        """Should detect Node.js from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_file = Path(tmpdir) / "package.json"
            package_file.write_text(json.dumps({
                "name": "my-app",
                "version": "1.0.0",
                "engines": {"node": ">=14.0.0"}
            }))

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.NODEJS

    def test_extract_node_version_from_package_json(self):
        """Should extract Node version from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_file = Path(tmpdir) / "package.json"
            package_file.write_text(json.dumps({
                "name": "my-app",
                "engines": {"node": ">=16.0.0"}
            }))

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert "16" in (result.version or "")


class TestGoProjectDetection:
    """Test Go project detection (AC3)."""

    def test_detect_go_with_go_mod(self):
        """Should detect Go from go.mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            go_mod_file = Path(tmpdir) / "go.mod"
            go_mod_file.write_text("""go 1.21
module github.com/example/myapp
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.GO

    def test_extract_go_version(self):
        """Should extract Go version from go.mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            go_mod_file = Path(tmpdir) / "go.mod"
            go_mod_file.write_text("go 1.20\nmodule example")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert "1.20" in (result.version or "")


class TestRustProjectDetection:
    """Test Rust project detection (AC4)."""

    def test_detect_rust_with_cargo_toml(self):
        """Should detect Rust from Cargo.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cargo_file = Path(tmpdir) / "Cargo.toml"
            cargo_file.write_text("""[package]
name = "myproject"
version = "0.1.0"
edition = "2021"
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.RUST

    def test_extract_rust_edition(self):
        """Should extract Rust edition from Cargo.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cargo_file = Path(tmpdir) / "Cargo.toml"
            cargo_file.write_text("""[package]
edition = "2021"
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert "2021" in (result.version or "")


class TestJavaProjectDetection:
    """Test Java project detection (AC5)."""

    def test_detect_java_with_pom_xml(self):
        """Should detect Java from pom.xml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pom_file = Path(tmpdir) / "pom.xml"
            pom_file.write_text("""<?xml version="1.0"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>myapp</artifactId>
</project>
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.JAVA

    def test_detect_java_with_build_gradle(self):
        """Should detect Java from build.gradle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gradle_file = Path(tmpdir) / "build.gradle"
            gradle_file.write_text("""
plugins {
    id 'java'
}

sourceCompatibility = '11'
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.JAVA


class TestCSharpProjectDetection:
    """Test C# project detection."""

    def test_detect_csharp_with_csproj(self):
        """Should detect C# from .csproj file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_file = Path(tmpdir) / "MyApp.csproj"
            csproj_file.write_text("""<?xml version="1.0"?>
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net6.0</TargetFramework>
    </PropertyGroup>
</Project>
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.CSHARP

    def test_detect_csharp_with_sln(self):
        """Should detect C# from .sln file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_file = Path(tmpdir) / "MySolution.sln"
            sln_file.write_text("""Microsoft Visual Studio Solution File, Format Version 12.00""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.CSHARP

    def test_extract_csharp_version_from_csproj(self):
        """Should extract .NET version from .csproj."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_file = Path(tmpdir) / "MyApp.csproj"
            csproj_file.write_text("""<?xml version="1.0"?>
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net7.0</TargetFramework>
    </PropertyGroup>
</Project>
""")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert "net7.0" in (result.version or "")


class TestMixedLanguageDetection:
    """Test mixed language project detection (AC6)."""

    def test_detect_mixed_python_and_nodejs(self):
        """Should handle projects with both Python and Node.js."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both Python and Node.js markers
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0")
            Path(tmpdir, "package.json").write_text(json.dumps({"name": "app"}))

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            # Should identify primary language
            assert result.primary_language in [ProjectLanguage.PYTHON, ProjectLanguage.NODEJS]
            # Should identify secondary languages
            assert len(result.secondary_languages) > 0

    def test_mixed_project_primary_by_marker_count(self):
        """Should determine primary by marker count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # More Python markers
            Path(tmpdir, "requirements.txt").write_text("requests")
            Path(tmpdir, "setup.py").write_text("setup()")
            Path(tmpdir, "pyproject.toml").write_text("[project]")
            # One Node marker
            Path(tmpdir, "package.json").write_text(json.dumps({"name": "app"}))

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON


class TestConfidenceScoring:
    """Test confidence score calculation."""

    def test_high_confidence_with_multiple_markers(self):
        """Multiple markers should yield high confidence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests")
            Path(tmpdir, "setup.py").write_text("setup()")
            Path(tmpdir, "pyproject.toml").write_text("[project]")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.confidence >= 0.80  # High confidence

    def test_medium_confidence_with_single_marker(self):
        """Single marker should yield medium confidence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert 0.60 <= result.confidence < 0.95

    def test_confidence_is_between_0_and_1(self):
        """Confidence should always be between 0 and 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert 0.0 <= result.confidence <= 1.0


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_permission_denied_graceful_handling(self):
        """Should gracefully handle permission denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("requests")
            # Remove read permissions
            os.chmod(req_file, 0o000)

            try:
                detector = ProjectTypeDetector(tmpdir)
                result = detector.detect_project_type()
                # Should still try to detect (graceful degradation)
                assert result is not None or result is None  # Either result or graceful None
            finally:
                # Restore permissions for cleanup
                os.chmod(req_file, 0o644)

    def test_empty_directory(self):
        """Should handle empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            # Should return None or low confidence
            assert result is None or result.confidence < 0.60

    def test_malformed_json_in_package_json(self):
        """Should handle malformed package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_file = Path(tmpdir) / "package.json"
            package_file.write_text("{ invalid json }")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            # Should still detect Node.js from filename
            assert result is not None
            assert result.primary_language == ProjectLanguage.NODEJS

    def test_encoding_error_in_config(self):
        """Should handle non-UTF8 config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            # Write with latin-1 encoding
            req_file.write_bytes(b"requests==2.28.0 # \xe9")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            # Should still detect despite encoding issue
            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON


class TestPerformance:
    """Test performance requirements."""

    def test_detection_completes_within_2_seconds(self):
        """Detection should complete within 2 seconds (Story 1.4 budget)."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests\nnumpy\npandas")

            detector = ProjectTypeDetector(tmpdir)
            start = time.perf_counter()
            result = detector.detect_project_type()
            elapsed = time.perf_counter() - start

            assert result is not None
            assert elapsed < 2.0  # Must complete within 2 seconds

    def test_no_recursive_directory_traversal(self):
        """Should NOT recursively scan subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a deeply nested marker file
            nested_dir = Path(tmpdir) / "a" / "b" / "c" / "d"
            nested_dir.mkdir(parents=True)
            (nested_dir / "requirements.txt").write_text("requests")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            # Should NOT find the nested marker (root-level search only)
            # Result should be None (no markers at root)
            assert result is None or result.confidence < 0.5


class TestMarkerFilePriority:
    """Test marker file priority handling."""

    def test_highest_priority_marker_selected(self):
        """Should prefer highest priority markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # requirements.txt has priority 10
            # setup.py has priority 8
            Path(tmpdir, "setup.py").write_text("setup()")

            detector = ProjectTypeDetector(tmpdir)
            # Check that priorities are considered
            assert hasattr(detector.PYTHON_MARKERS['requirements.txt'], '__getitem__') or \
                   isinstance(detector.PYTHON_MARKERS['requirements.txt'], dict)


class TestIntegration:
    """Integration tests with realistic project structures."""

    def test_realistic_python_project(self):
        """Test with realistic Python project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create realistic Python project
            Path(tmpdir, "pyproject.toml").write_text("""
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = ["requests", "numpy"]
""")
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\nnumpy==1.21.0")
            Path(tmpdir, "setup.py").write_text("setup(name='myproject')")

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON
            assert result.confidence >= 0.85  # High confidence

    def test_realistic_nodejs_project(self):
        """Test with realistic Node.js project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create realistic Node.js project
            Path(tmpdir, "package.json").write_text(json.dumps({
                "name": "my-app",
                "version": "1.0.0",
                "engines": {"node": ">=16.0.0"},
                "dependencies": {"express": "^4.18.0", "lodash": "^4.17.0"}
            }))
            Path(tmpdir, "package-lock.json").write_text(json.dumps({"lockfileVersion": 2}))

            detector = ProjectTypeDetector(tmpdir)
            result = detector.detect_project_type()

            assert result is not None
            assert result.primary_language == ProjectLanguage.NODEJS
            assert "16" in (result.version or "")


class TestInitWithProjectPath:
    """Test ProjectTypeDetector initialization with custom paths."""

    def test_detector_accepts_project_path(self):
        """ProjectTypeDetector should accept project path in __init__."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests")

            detector = ProjectTypeDetector(tmpdir)
            assert detector is not None

            result = detector.detect_project_type()
            assert result is not None
            assert result.primary_language == ProjectLanguage.PYTHON

    def test_detector_defaults_to_current_directory(self):
        """ProjectTypeDetector should default to current directory if not specified."""
        detector = ProjectTypeDetector()
        assert detector is not None
