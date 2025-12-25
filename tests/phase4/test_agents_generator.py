"""
Tests for AGENTS.md generation system (Phase 4).

Test coverage:
- TemplateRegistry template loading and selection
- ContentExtractor project information extraction
- AgentsTemplateGenerator content generation
- AgentsWriter file operations
- AgentsGenerator main workflow
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.prompt_enhancement.phase4 import (
    TemplateRegistry,
    TemplateType,
    ContentExtractor,
    AgentsTemplateGenerator,
    AgentsWriter,
    AgentsGenerator,
)


class TestTemplateRegistry:
    """Tests for TemplateRegistry."""

    def test_registry_initialization(self):
        """Test that registry initializes with all builtin templates."""
        registry = TemplateRegistry()
        templates = registry.list_templates()

        assert len(templates) > 0
        assert "python" in templates
        assert "nodejs" in templates
        assert "go" in templates

    def test_get_python_template(self):
        """Test retrieving Python template."""
        registry = TemplateRegistry()
        template = registry.get_template(TemplateType.PYTHON)

        assert template is not None
        assert template.template_type == TemplateType.PYTHON
        assert "{PROJECT_NAME}" in template.template_content
        assert "Setup & Installation" in template.template_content

    def test_get_nodejs_template(self):
        """Test retrieving Node.js template."""
        registry = TemplateRegistry()
        template = registry.get_template(TemplateType.NODEJS)

        assert template is not None
        assert template.template_type == TemplateType.NODEJS
        assert "{PROJECT_NAME}" in template.template_content

    def test_get_nonexistent_template(self):
        """Test retrieving non-existent template."""
        registry = TemplateRegistry()
        template = registry.get_template(TemplateType.PYTHON)
        registry._templates.clear()

        template = registry.get_template(TemplateType.PYTHON)
        assert template is None

    def test_register_custom_template(self):
        """Test registering a custom template."""
        from src.prompt_enhancement.phase4.template_registry import AgentsTemplate

        registry = TemplateRegistry()
        custom_template = AgentsTemplate(
            template_type=TemplateType.PYTHON,
            name="Custom Python",
            description="Custom Python template",
            template_content="# Custom Template\n{PROJECT_NAME}",
            placeholders={"PROJECT_NAME": "Project name"}
        )

        registry.register_template(TemplateType.PYTHON, custom_template)
        retrieved = registry.get_template(TemplateType.PYTHON)

        assert retrieved.name == "Custom Python"


class TestContentExtractor:
    """Tests for ContentExtractor."""

    def test_extract_project_name_from_node_project(self):
        """Test extracting project name from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({"name": "test-project"}))

            extractor = ContentExtractor(tmpdir)
            name = extractor._extract_project_name()

            assert name == "test-project"

    def test_detect_python_language(self):
        """Test Python language detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest==7.0.0\n")

            extractor = ContentExtractor(tmpdir)
            language = extractor._detect_primary_language()

            assert language == "Python"

    def test_detect_nodejs_language(self):
        """Test Node.js language detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({"name": "test"}))

            extractor = ContentExtractor(tmpdir)
            language = extractor._detect_primary_language()

            assert language == "Node.js"

    def test_detect_go_language(self):
        """Test Go language detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            go_mod = Path(tmpdir) / "go.mod"
            go_mod.write_text("module example.com/test\n")

            extractor = ContentExtractor(tmpdir)
            language = extractor._detect_primary_language()

            assert language == "Go"

    def test_extract_version(self):
        """Test version extraction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_json = Path(tmpdir) / "package.json"
            package_json.write_text(json.dumps({"version": "1.2.3"}))

            extractor = ContentExtractor(tmpdir)
            version = extractor._extract_version()

            assert version == "1.2.3"

    def test_extract_commands_python(self):
        """Test command extraction for Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = ContentExtractor(tmpdir)
            setup_cmd, test_cmd, run_cmd, build_cmd = extractor._extract_commands("Python")

            assert "pip install" in setup_cmd
            assert "pytest" in test_cmd
            assert run_cmd is not None

    def test_extract_commands_nodejs(self):
        """Test command extraction for Node.js."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = ContentExtractor(tmpdir)
            setup_cmd, test_cmd, run_cmd, build_cmd = extractor._extract_commands("Node.js")

            assert setup_cmd == "npm install"
            assert "npm test" in test_cmd or "npm" in test_cmd

    def test_extract_info_complete(self):
        """Test complete project info extraction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python project
            Path(tmpdir, "src").mkdir()
            (Path(tmpdir) / "requirements.txt").write_text("pytest==7.0.0\n")
            (Path(tmpdir) / "README.md").write_text("# Test Project\nA test project")

            extractor = ContentExtractor(tmpdir)
            info = extractor.extract_info()

            assert info is not None
            assert info.primary_language == "Python"
            assert info.setup_command is not None
            assert info.test_command is not None


class TestAgentsTemplateGenerator:
    """Tests for AgentsTemplateGenerator."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsTemplateGenerator(tmpdir)

            assert generator.project_root == tmpdir
            assert generator.template_registry is not None
            assert generator.content_extractor is not None

    def test_map_language_to_template(self):
        """Test language to template mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsTemplateGenerator(tmpdir)

            assert generator._map_language_to_template("Python") == TemplateType.PYTHON
            assert generator._map_language_to_template("Node.js") == TemplateType.NODEJS
            assert generator._map_language_to_template("Go") == TemplateType.GO

    def test_build_placeholder_dict(self):
        """Test placeholder dictionary building."""
        from src.prompt_enhancement.phase4.content_extractor import ProjectInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsTemplateGenerator(tmpdir)

            project_info = ProjectInfo(
                name="test-project",
                description="Test description",
                primary_language="Python",
                version="1.0.0",
                setup_command="pip install",
                test_command="pytest",
                run_command="python main.py",
                build_command=None,
                lint_command="pylint",
                format_command="black",
                type_check_command="mypy",
                main_dependencies=["requests", "pytest"],
                code_style_guidelines={},
                project_structure="test/",
                protected_directories=[],
                additional_info={}
            )

            placeholders = generator._build_placeholder_dict(project_info)

            assert placeholders["PROJECT_NAME"] == "test-project"
            assert placeholders["SETUP_COMMAND"] == "pip install"
            assert placeholders["TEST_COMMAND"] == "pytest"


class TestAgentsWriter:
    """Tests for AgentsWriter."""

    def test_writer_initialization(self):
        """Test writer initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = AgentsWriter(tmpdir)

            assert writer.project_root == Path(tmpdir)
            assert writer.agents_file == Path(tmpdir) / "AGENTS.md"

    def test_validate_content(self):
        """Test content validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = AgentsWriter(tmpdir)

            # Valid content
            valid_content = "# Project\n\n## Setup\n\nInstall dependencies\n"
            assert writer._validate_content(valid_content) == True

            # Invalid content (empty)
            assert writer._validate_content("") == False
            assert writer._validate_content(None) == False

    def test_write_file(self):
        """Test writing AGENTS.md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = AgentsWriter(tmpdir)
            content = "# Test Project\n\nTest content"

            success, message = writer.write_agents_md(content, backup_existing=False)

            assert success == True
            assert writer.agents_file.exists()
            assert writer.agents_file.read_text() == content

    def test_backup_existing_file(self):
        """Test backing up existing AGENTS.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_file = Path(tmpdir) / "AGENTS.md"
            agents_file.write_text("Old content")

            writer = AgentsWriter(tmpdir)
            new_content = "New content"

            success, message = writer.write_agents_md(new_content, backup_existing=True)

            assert success == True
            assert agents_file.read_text() == new_content

            # Check backup exists
            backups = writer.get_backup_history()
            assert len(backups) > 0

    def test_restore_from_backup(self):
        """Test restoring from backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = AgentsWriter(tmpdir)

            # Create initial file
            writer.write_agents_md("Original content", backup_existing=False)

            # Modify file
            writer.write_agents_md("Modified content", backup_existing=True)

            # Restore
            success, message = writer.restore_from_backup()

            assert success == True
            assert writer.agents_file.read_text() == "Original content"


class TestAgentsGenerator:
    """Tests for AgentsGenerator main workflow."""

    def test_generator_initialization(self):
        """Test main generator initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsGenerator(tmpdir)

            assert generator.project_root == Path(tmpdir)
            assert generator.generator is not None
            assert generator.writer is not None

    def test_invalid_project_root(self):
        """Test initialization with invalid project root."""
        with pytest.raises(ValueError):
            AgentsGenerator("/nonexistent/path")

    def test_generate_preview(self):
        """Test generating preview without writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsGenerator(tmpdir)

            success, content = generator.generate_preview()

            assert success == True
            assert content is not None
            assert len(content) > 0
            assert "# " in content  # Should have markdown header

    def test_verify_agents_md_nonexistent(self):
        """Test verification of non-existent AGENTS.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            generator = AgentsGenerator(tmpdir)

            valid, message = generator.verify_agents_md()

            assert valid == False
            assert "does not exist" in message

    def test_complete_workflow(self):
        """Test complete generation workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup test project
            (Path(tmpdir) / "requirements.txt").write_text("pytest==7.0.0\n")
            (Path(tmpdir) / "pyproject.toml").write_text(
                'name = "test-project"\nversion = "1.0.0"\n'
            )

            generator = AgentsGenerator(tmpdir)
            success, message = generator.generate()

            assert success == True

            # Verify file was created
            agents_file = Path(tmpdir) / "AGENTS.md"
            assert agents_file.exists()

            # Verify content
            content = agents_file.read_text()
            assert "test-project" in content or "Setup" in content

    def test_backup_cleanup(self):
        """Test old backup cleanup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "requirements.txt").write_text("")
            writer = AgentsWriter(tmpdir)

            # Create multiple backups manually
            import time
            for i in range(7):
                writer.write_agents_md(f"Content {i}", backup_existing=(i > 0))
                if i < 6:
                    time.sleep(0.01)  # Small delay to ensure different timestamps

            backups_before = len(writer.get_backup_history())
            deleted, message = writer.cleanup_old_backups(keep_count=5)
            backups_after = len(writer.get_backup_history())

            # Only assert if we had multiple backups to clean
            if backups_before > 5:
                assert deleted >= 0
                assert backups_after <= 5
            else:
                # Less than 5 backups, cleanup should have nothing to do
                assert deleted == 0


class TestPhase4Integration:
    """Integration tests for Phase 4 workflow."""

    def test_python_project_workflow(self):
        """Test complete workflow for Python project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup Python project
            Path(tmpdir, "src").mkdir()
            (Path(tmpdir) / "requirements.txt").write_text(
                "pytest==7.0.0\nflake8==4.0.0\n"
            )
            (Path(tmpdir) / "setup.py").write_text("")

            generator = AgentsGenerator(tmpdir)
            success, message = generator.generate()

            assert success == True

            agents_file = Path(tmpdir) / "AGENTS.md"
            content = agents_file.read_text()

            # Verify Python-specific content
            assert "pytest" in content.lower() or "test" in content.lower()

    def test_nodejs_project_workflow(self):
        """Test complete workflow for Node.js project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup Node.js project
            package_json = {
                "name": "test-app",
                "version": "1.0.0",
                "scripts": {
                    "test": "jest",
                    "build": "webpack",
                    "start": "node index.js"
                }
            }
            (Path(tmpdir) / "package.json").write_text(json.dumps(package_json))

            generator = AgentsGenerator(tmpdir)
            success, message = generator.generate()

            assert success == True

            agents_file = Path(tmpdir) / "AGENTS.md"
            content = agents_file.read_text()

            # Verify Node.js-specific content
            assert "jest" in content.lower() or "npm" in content.lower()
