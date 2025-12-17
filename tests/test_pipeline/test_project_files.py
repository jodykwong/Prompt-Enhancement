"""
Comprehensive tests for ProjectIndicatorFilesDetector (Story 2.2).

Tests project indicator file identification, metadata extraction, dependency parsing,
and error handling across 6 supported languages.
"""

import json
import tempfile
import pytest
from pathlib import Path
from typing import Optional

# Import the detector (will be created in implementation)
from src.prompt_enhancement.pipeline.tech_stack import ProjectLanguage
from src.prompt_enhancement.pipeline.project_files import (
    ProjectIndicatorFilesDetector,
    DependencyInfo,
    ProjectMetadata,
    ProjectIndicatorResult,
)


# ============================================================================
# Data Structure Tests
# ============================================================================

class TestDataStructures:
    """Test data structures: DependencyInfo, ProjectMetadata, ProjectIndicatorResult."""

    def test_dependency_info_structure(self):
        """DependencyInfo should store dependency details."""
        dep = DependencyInfo(
            name="requests",
            version="2.28.0",
            scope="production",
            features=[]
        )
        assert dep.name == "requests"
        assert dep.version == "2.28.0"
        assert dep.scope == "production"

    def test_project_metadata_structure(self):
        """ProjectMetadata should store project information."""
        metadata = ProjectMetadata(
            name="my-project",
            version="1.0.0",
            source_language=ProjectLanguage.PYTHON,
            dependencies=[],
            dev_dependencies=[],
            target_version="3.9",
            package_manager="pip"
        )
        assert metadata.name == "my-project"
        assert metadata.source_language == ProjectLanguage.PYTHON

    def test_project_indicator_result_structure(self):
        """ProjectIndicatorResult should include metadata and files found."""
        result = ProjectIndicatorResult(
            metadata=None,
            files_found=["package.json"],
            lock_files_present={"package-lock.json"},
            confidence=0.95
        )
        assert result.files_found == ["package.json"]
        assert result.confidence == 0.95


# ============================================================================
# Python Configuration Parsing Tests (AC1, AC2, AC6)
# ============================================================================

class TestPythonConfigParsing:
    """Test Python configuration file parsing."""

    def test_detect_pyproject_toml(self):
        """Should detect pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "pyproject.toml").write_text("""
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["requests", "numpy"]
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-project"
            assert result.metadata.version == "0.1.0"

    def test_extract_python_dependencies_from_pyproject(self):
        """Should extract dependencies from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "pyproject.toml").write_text("""
[project]
name = "my-project"
dependencies = ["requests==2.28.0", "numpy>=1.21.0"]

[project.optional-dependencies]
dev = ["pytest", "black"]
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is not None
            assert len(result.metadata.dependencies) >= 2
            assert any(d.name == "requests" for d in result.metadata.dependencies)

    def test_detect_setup_py(self):
        """Should detect setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "setup.py").write_text("""
from setuptools import setup
setup(
    name='my-project',
    version='0.1.0',
    install_requires=['requests', 'numpy']
)
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-project"

    def test_detect_requirements_txt(self):
        """Should detect requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text(
                "requests==2.28.0\nnumpy>=1.21.0\npandas\n"
            )
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is not None
            assert any(d.name == "requests" for d in result.metadata.dependencies)

    def test_detect_poetry_lock(self):
        """Should detect poetry.lock as lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "pyproject.toml").write_text("[project]\nname='test'")
            Path(tmpdir, "poetry.lock").write_text("# lock content")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert "poetry.lock" in result.lock_files_present


# ============================================================================
# Node.js Configuration Parsing Tests (AC1, AC2, AC6)
# ============================================================================

class TestNodeConfigParsing:
    """Test Node.js configuration file parsing."""

    def test_detect_package_json(self):
        """Should detect package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_data = {
                "name": "my-app",
                "version": "1.0.0",
                "engines": {"node": ">=16.0.0"},
                "dependencies": {"express": "^4.18.0", "lodash": "^4.17.0"},
                "devDependencies": {"jest": "^29.0.0"}
            }
            Path(tmpdir, "package.json").write_text(json.dumps(package_data))

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-app"
            assert result.metadata.target_version == "16.0.0"

    def test_extract_node_dependencies(self):
        """Should extract dependencies from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_data = {
                "name": "my-app",
                "dependencies": {"express": "^4.18.0", "axios": "^1.0.0"},
                "devDependencies": {"jest": "^29.0.0"}
            }
            Path(tmpdir, "package.json").write_text(json.dumps(package_data))

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert len(result.metadata.dependencies) >= 2
            assert len(result.metadata.dev_dependencies) >= 1

    def test_detect_package_lock_json(self):
        """Should detect package-lock.json as lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_data = {"name": "my-app", "version": "1.0.0"}
            Path(tmpdir, "package.json").write_text(json.dumps(package_data))
            Path(tmpdir, "package-lock.json").write_text(json.dumps({"lockfileVersion": 2}))

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert "package-lock.json" in result.lock_files_present
            assert "npm" in result.metadata.package_manager.lower()

    def test_detect_yarn_lock(self):
        """Should detect yarn.lock as lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_data = {"name": "my-app", "version": "1.0.0"}
            Path(tmpdir, "package.json").write_text(json.dumps(package_data))
            Path(tmpdir, "yarn.lock").write_text("# yarn lock file")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert "yarn.lock" in result.lock_files_present


# ============================================================================
# Go Configuration Parsing Tests (AC1, AC2)
# ============================================================================

class TestGoConfigParsing:
    """Test Go configuration file parsing."""

    def test_detect_go_mod(self):
        """Should detect go.mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "go.mod").write_text("""go 1.21
module github.com/example/myapp

require (
    github.com/some/lib v1.2.3
    github.com/other/lib v2.0.0
)
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.GO)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.target_version == "1.21"

    def test_detect_go_sum(self):
        """Should detect go.sum as lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "go.mod").write_text("go 1.21\nmodule example")
            Path(tmpdir, "go.sum").write_text("github.com/lib v1.0.0 h1:...")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.GO)
            result = detector.extract_project_metadata()

            assert "go.sum" in result.lock_files_present


# ============================================================================
# Rust Configuration Parsing Tests (AC1, AC2)
# ============================================================================

class TestRustConfigParsing:
    """Test Rust configuration file parsing."""

    def test_detect_cargo_toml(self):
        """Should detect Cargo.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Cargo.toml").write_text("""[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = "1.35"
serde = { version = "1.0", features = ["derive"] }
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.RUST)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-crate"
            assert result.metadata.target_version == "2021"

    def test_detect_cargo_lock(self):
        """Should detect Cargo.lock as lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Cargo.toml").write_text("[package]\nname='test'")
            Path(tmpdir, "Cargo.lock").write_text("version = 3")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.RUST)
            result = detector.extract_project_metadata()

            assert "Cargo.lock" in result.lock_files_present


# ============================================================================
# Java Configuration Parsing Tests (AC1, AC2)
# ============================================================================

class TestJavaConfigParsing:
    """Test Java configuration file parsing."""

    def test_detect_pom_xml(self):
        """Should detect pom.xml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "pom.xml").write_text("""<?xml version="1.0"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>myapp</artifactId>
    <version>1.0.0</version>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
</project>
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.JAVA)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.target_version == "11"

    def test_detect_build_gradle(self):
        """Should detect build.gradle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "build.gradle").write_text("""
plugins {
    id 'java'
}

sourceCompatibility = '11'

dependencies {
    implementation 'junit:junit:4.13.2'
}
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.JAVA)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.target_version == "11"


# ============================================================================
# C# Configuration Parsing Tests (AC1)
# ============================================================================

class TestCSharpConfigParsing:
    """Test C# configuration file parsing."""

    def test_detect_csproj(self):
        """Should detect .csproj file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "MyProject.csproj").write_text("""<?xml version="1.0"?>
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net6.0</TargetFramework>
        <LangVersion>latest</LangVersion>
    </PropertyGroup>
</Project>
""")
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.CSHARP)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.target_version == "net6.0"


# ============================================================================
# Error Handling Tests (AC5)
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_config_files(self):
        """Should handle missing config files gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            # Should return None or low confidence
            assert result is None or result.confidence < 0.6

    def test_malformed_json_in_package_json(self):
        """Should handle malformed package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text("{ invalid json }")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            # Should not crash, may return partial or None
            assert result is None or isinstance(result, ProjectIndicatorResult)

    def test_encoding_error_in_config(self):
        """Should handle non-UTF8 config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write with latin-1 encoding
            config_path = Path(tmpdir, "pyproject.toml")
            config_path.write_bytes("[project]\nname = 'test' # \xe9".encode('latin-1'))

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            # Should not crash
            result = detector.extract_project_metadata()
            assert True  # If we got here, no crash

    def test_permission_denied_graceful(self):
        """Should gracefully handle permission denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir, "package.json")
            config_file.write_text(json.dumps({"name": "test"}))
            # Remove read permissions
            import os
            os.chmod(config_file, 0o000)

            try:
                detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
                result = detector.extract_project_metadata()
                # Should not crash
                assert result is None or isinstance(result, ProjectIndicatorResult)
            finally:
                # Restore permissions for cleanup
                os.chmod(config_file, 0o644)

    def test_empty_directory(self):
        """Should handle empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is None or result.confidence < 0.5


# ============================================================================
# Lock File Detection Tests (AC3)
# ============================================================================

class TestLockFileDetection:
    """Test lock file detection and package manager identification."""

    def test_identify_npm_from_lock(self):
        """Should identify npm from package-lock.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text(json.dumps({"name": "test"}))
            Path(tmpdir, "package-lock.json").write_text("{}")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert "npm" in result.metadata.package_manager.lower()

    def test_identify_cargo_from_lock(self):
        """Should identify cargo from Cargo.lock."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Cargo.toml").write_text("[package]\nname='test'")
            Path(tmpdir, "Cargo.lock").write_text("version = 3")

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.RUST)
            result = detector.extract_project_metadata()

            assert "cargo" in result.metadata.package_manager.lower()


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance requirements."""

    def test_detection_completes_within_2_seconds(self):
        """Metadata extraction should complete within 2 seconds."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text(
                json.dumps({"name": "test", "dependencies": {"express": "^4.18.0"}})
            )

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            start = time.perf_counter()
            result = detector.extract_project_metadata()
            elapsed = time.perf_counter() - start

            assert elapsed < 2.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests with realistic project structures."""

    def test_realistic_python_project(self):
        """Test with realistic Python project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create realistic structure
            Path(tmpdir, "pyproject.toml").write_text("""
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = ["requests", "numpy"]

[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]
""")
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0")
            Path(tmpdir, "poetry.lock").write_text("# lock file")
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-project"
            assert len(result.files_found) >= 3  # pyproject.toml, requirements.txt, poetry.lock

    def test_realistic_nodejs_project(self):
        """Test with realistic Node.js project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_data = {
                "name": "my-app",
                "version": "1.0.0",
                "engines": {"node": ">=16.0.0"},
                "dependencies": {"express": "^4.18.0", "lodash": "^4.17.0"},
                "devDependencies": {"jest": "^29.0.0", "webpack": "^5.0.0"}
            }
            Path(tmpdir, "package.json").write_text(json.dumps(package_data))
            Path(tmpdir, "package-lock.json").write_text(json.dumps({"lockfileVersion": 2}))
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "dist").mkdir()

            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.name == "my-app"
            assert len(result.metadata.dependencies) >= 2
            assert len(result.metadata.dev_dependencies) >= 2


class TestInitialization:
    """Test detector initialization."""

    def test_detector_accepts_project_path(self):
        """ProjectIndicatorFilesDetector should accept path and language."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.PYTHON)
            assert detector is not None

    def test_detector_with_language_input(self):
        """Should use provided language for parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text(
                json.dumps({"name": "test", "version": "1.0.0"})
            )
            detector = ProjectIndicatorFilesDetector(tmpdir, ProjectLanguage.NODEJS)
            result = detector.extract_project_metadata()

            assert result is not None
            assert result.metadata.source_language == ProjectLanguage.NODEJS
