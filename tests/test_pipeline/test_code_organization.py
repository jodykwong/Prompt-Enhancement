"""
Comprehensive test suite for code organization pattern detection.
Tests all 8 acceptance criteria for Story 2.8.
"""

import pytest
import tempfile
import json
from pathlib import Path
from dataclasses import asdict

from src.prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from src.prompt_enhancement.pipeline.project_files import ProjectIndicatorResult
from src.prompt_enhancement.pipeline.code_organization import (
    CodeOrganizationDetector,
    OrganizationType,
    OrganizationPattern,
    CodeOrganizationResult,
)


class TestMonorepoDetection:
    """Test AC1: Monorepo vs Single-Repo Detection"""

    def test_lerna_monorepo_detection(self):
        """Test detection of Lerna monorepo structure"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Lerna monorepo structure
            Path(tmpdir, "package.json").write_text(json.dumps({
                "name": "monorepo",
                "private": True,
                "workspaces": ["packages/*"]
            }))
            Path(tmpdir, "packages").mkdir()
            Path(tmpdir, "packages", "package1").mkdir(parents=True)
            Path(tmpdir, "packages", "package1", "package.json").write_text(json.dumps({
                "name": "@org/package1",
                "version": "1.0.0"
            }))
            Path(tmpdir, "packages", "package2").mkdir(parents=True)
            Path(tmpdir, "packages", "package2", "package.json").write_text(json.dumps({
                "name": "@org/package2",
                "version": "1.0.0"
            }))

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.primary_type == OrganizationType.MONOREPO
            assert result.confidence >= 0.7

    def test_yarn_workspaces_detection(self):
        """Test detection of Yarn workspaces monorepo"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text(json.dumps({
                "name": "monorepo",
                "private": True,
                "workspaces": [
                    "packages/app",
                    "packages/lib",
                    "packages/cli"
                ]
            }))
            Path(tmpdir, "packages").mkdir()
            for pkg in ["app", "lib", "cli"]:
                Path(tmpdir, "packages", pkg).mkdir(parents=True)
                Path(tmpdir, "packages", pkg, "package.json").write_text(json.dumps({
                    "name": f"@org/{pkg}",
                    "version": "1.0.0"
                }))

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.primary_type == OrganizationType.MONOREPO

    def test_single_repo_detection(self):
        """Test detection of single-repo structure"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create single-repo structure
            Path(tmpdir, "package.json").write_text(json.dumps({
                "name": "single-app",
                "version": "1.0.0"
            }))
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "index.js").write_text("console.log('hello');")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.primary_type == OrganizationType.SINGLE_REPO

    def test_maven_multimodule_detection(self):
        """Test detection of Maven multi-module project"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Maven multi-module structure
            Path(tmpdir, "pom.xml").write_text("""<?xml version="1.0"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>module1</module>
        <module>module2</module>
    </modules>
</project>""")
            for module in ["module1", "module2"]:
                Path(tmpdir, module).mkdir()
                Path(tmpdir, module, "pom.xml").write_text(f"""<?xml version="1.0"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>{module}</artifactId>
</project>""")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.JAVA,
                version="11.0.0",
                confidence=0.95,
                markers_found=["pom.xml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.primary_type == OrganizationType.MONOREPO


class TestCommonDirectoryPatterns:
    """Test AC2: Common Directory Structure Patterns"""

    def test_src_lib_directory_pattern(self):
        """Test detection of src/lib directory patterns"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "main.py").write_text("print('hello')")
            Path(tmpdir, "lib").mkdir()
            Path(tmpdir, "lib", "helper.py").write_text("def help(): pass")
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "tests", "test_main.py").write_text("def test(): pass")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert len(result.detected_patterns) > 0
            # Check that src and lib patterns are detected
            pattern_names = [p.name for p in result.detected_patterns]
            assert any("src" in name.lower() for name in pattern_names)

    def test_components_services_pattern(self):
        """Test detection of components/services pattern"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "components").mkdir()
            Path(tmpdir, "src", "components", "Button.jsx").write_text("export Button;")
            Path(tmpdir, "src", "components", "Modal.jsx").write_text("export Modal;")
            Path(tmpdir, "src", "services").mkdir()
            Path(tmpdir, "src", "services", "api.js").write_text("export api;")
            Path(tmpdir, "src", "services", "auth.js").write_text("export auth;")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert len(result.detected_patterns) > 0

    def test_maven_directory_structure(self):
        """Test detection of Maven src/main/java structure"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src", "main", "java").mkdir(parents=True)
            Path(tmpdir, "src", "main", "java", "App.java").write_text("class App {}")
            Path(tmpdir, "src", "test", "java").mkdir(parents=True)
            Path(tmpdir, "src", "test", "java", "AppTest.java").write_text("class AppTest {}")
            Path(tmpdir, "src", "main", "resources").mkdir(parents=True)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.JAVA,
                version="11.0.0",
                confidence=0.95,
                markers_found=["pom.xml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert len(result.detected_patterns) > 0


class TestLanguageSpecificPatterns:
    """Test AC3: Language-Specific Organization Patterns"""

    def test_python_package_structure(self):
        """Test detection of Python package structure"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "mypackage").mkdir()
            Path(tmpdir, "src", "mypackage", "__init__.py").write_text("")
            Path(tmpdir, "src", "mypackage", "module.py").write_text("def func(): pass")
            Path(tmpdir, "src", "mypackage", "submodule").mkdir()
            Path(tmpdir, "src", "mypackage", "submodule", "__init__.py").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_javascript_entry_point_pattern(self):
        """Test detection of JavaScript index.js entry points"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "index.js").write_text("export default App;")
            Path(tmpdir, "src", "components").mkdir()
            Path(tmpdir, "src", "components", "index.js").write_text("export Button;")
            Path(tmpdir, "src", "utils").mkdir()
            Path(tmpdir, "src", "utils", "index.js").write_text("export helper;")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_java_package_naming_convention(self):
        """Test detection of Java package naming conventions"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src", "main", "java", "com", "example", "app").mkdir(parents=True)
            Path(tmpdir, "src", "main", "java", "com", "example", "app", "App.java").write_text(
                "package com.example.app; class App {}"
            )

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.JAVA,
                version="11.0.0",
                confidence=0.95,
                markers_found=["pom.xml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_go_workspace_pattern(self):
        """Test detection of Go workspace structure"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "cmd").mkdir()
            Path(tmpdir, "cmd", "server").mkdir()
            Path(tmpdir, "cmd", "server", "main.go").write_text("func main() {}")
            Path(tmpdir, "pkg").mkdir()
            Path(tmpdir, "pkg", "helper.go").write_text("func Helper() {}")
            Path(tmpdir, "internal").mkdir()
            Path(tmpdir, "internal", "utils.go").write_text("func utils() {}")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.GO,
                version="1.18.0",
                confidence=0.95,
                markers_found=["go.mod"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None


class TestModuleBoundaryDetection:
    """Test AC4: Module/Package Boundary Detection"""

    def test_monorepo_module_boundary_detection(self):
        """Test detection of module boundaries in monorepo"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create monorepo with distinct modules
            Path(tmpdir, "packages").mkdir()
            for module in ["ui", "api", "shared"]:
                Path(tmpdir, "packages", module).mkdir()
                Path(tmpdir, "packages", module, "package.json").write_text(
                    json.dumps({"name": f"@org/{module}", "version": "1.0.0"})
                )
                Path(tmpdir, "packages", module, "src").mkdir()
                Path(tmpdir, "packages", module, "src", "index.js").write_text(f"export {module};")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.module_count is not None
            assert result.module_count >= 3

    def test_shared_code_detection(self):
        """Test detection of shared code locations"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "packages").mkdir()
            Path(tmpdir, "packages", "shared").mkdir()
            Path(tmpdir, "packages", "shared", "utils.js").write_text("export utils;")
            Path(tmpdir, "packages", "shared", "hooks.js").write_text("export hooks;")
            Path(tmpdir, "packages", "app1").mkdir()
            Path(tmpdir, "packages", "app2").mkdir()

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None


class TestDirectoryMetrics:
    """Test AC5: Directory Depth and Layout Analysis"""

    def test_directory_depth_calculation(self):
        """Test calculation of directory depth metrics"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deep directory structure
            Path(tmpdir, "src", "components", "form", "input", "text").mkdir(parents=True)
            Path(tmpdir, "src", "utils", "helpers").mkdir(parents=True)
            Path(tmpdir, "src", "services").mkdir(parents=True)

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.metrics is not None
            assert result.metrics.max_depth >= 3

    def test_directory_fanout_analysis(self):
        """Test detection of directory fan-out patterns"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            # Create high fan-out directory
            for i in range(15):
                Path(tmpdir, "src", f"module{i}").mkdir()
                Path(tmpdir, "src", f"module{i}", "index.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_flat_vs_hierarchical_detection(self):
        """Test detection of flat vs hierarchical organization"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create flat structure
            Path(tmpdir, "module1.js").write_text("")
            Path(tmpdir, "module2.js").write_text("")
            Path(tmpdir, "module3.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None


class TestConfigurationOrganization:
    """Test AC6: Configuration File Organization"""

    def test_centralized_config_detection(self):
        """Test detection of centralized configuration"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create centralized config structure
            Path(tmpdir, ".eslintrc.json").write_text("{}")
            Path(tmpdir, ".prettierrc.json").write_text("{}")
            Path(tmpdir, "tsconfig.json").write_text("{}")
            Path(tmpdir, "jest.config.js").write_text("module.exports = {};")
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "index.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_environment_specific_config_detection(self):
        """Test detection of environment-specific configs"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "config").mkdir()
            Path(tmpdir, "config", "dev.env").write_text("DEBUG=true")
            Path(tmpdir, "config", "prod.env").write_text("DEBUG=false")
            Path(tmpdir, "config", "test.env").write_text("DEBUG=false")
            Path(tmpdir, ".env.local").write_text("DEBUG=true")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None


class TestResultFormat:
    """Test AC7: Organization Result Format"""

    def test_code_organization_result_structure(self):
        """Test that result has all required fields"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "index.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert hasattr(result, 'primary_type')
            assert hasattr(result, 'detected_patterns')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'version')
            assert result.detected_patterns is not None

    def test_result_serialization(self):
        """Test that result can be serialized to dict"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "index.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            result_dict = asdict(result)
            assert result_dict is not None
            assert 'detected_patterns' in result_dict


class TestIntegration:
    """Test AC8: Integration with Project Analysis"""

    def test_integration_with_project_analysis(self):
        """Test integration with other detection modules"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "main.py").write_text("def main(): pass")
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "tests", "test_main.py").write_text("def test(): pass")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.detected_patterns is not None


class TestPerformance:
    """Test performance targets"""

    def test_performance_within_1_5_second_budget(self):
        """Test that detection completes within 1.5-second budget"""
        import time

        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a moderately complex project structure
            Path(tmpdir, "src", "components").mkdir(parents=True)
            Path(tmpdir, "src", "services").mkdir(parents=True)
            Path(tmpdir, "src", "utils").mkdir(parents=True)
            Path(tmpdir, "tests", "unit").mkdir(parents=True)
            Path(tmpdir, "tests", "integration").mkdir(parents=True)

            for i in range(5):
                Path(tmpdir, "src", "components", f"comp{i}.js").write_text("")
                Path(tmpdir, "tests", "unit", f"test{i}.js").write_text("")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            start_time = time.time()
            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))
            elapsed = time.time() - start_time

            assert elapsed < 1.5
            assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_project_handling(self):
        """Test handling of empty projects"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is None or isinstance(result, CodeOrganizationResult)

    def test_mixed_organization_patterns(self):
        """Test handling of mixed organization patterns"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create structure with mixed patterns
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "lib").mkdir()
            Path(tmpdir, "app").mkdir()
            Path(tmpdir, "utils").mkdir()

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            assert result is not None

    def test_unsupported_language_handling(self):
        """Test handling of unsupported languages"""
        detector = CodeOrganizationDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.RUST,
                version="1.70",
                confidence=0.95,
                markers_found=["Cargo.toml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_code_organization(tech_result, file_result, str(tmpdir))

            # Should gracefully handle unsupported languages
            assert result is None or isinstance(result, CodeOrganizationResult)
